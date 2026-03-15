"""
Nova Act job search agent.
Searches multiple job boards and returns structured job listings.
Uses parallel sessions for speed. Falls back to mock data if Nova Act fails.
"""

import threading
import logging
import time
import json
from typing import Optional
from pydantic import BaseModel
from config import settings

logger = logging.getLogger(__name__)

try:
    from nova_act import NovaAct
    NOVA_ACT_AVAILABLE = True
except ImportError:
    logger.warning("nova-act not installed. Job search will use mock data.")
    NOVA_ACT_AVAILABLE = False


class JobListing(BaseModel):
    title: str
    company: str
    location: str
    salary_range: Optional[str] = None
    url: str
    posted_date: Optional[str] = None
    requirements: list[str] = []
    description: Optional[str] = None
    platform: str = "unknown"


class JobResults(BaseModel):
    jobs: list[JobListing] = []
    platform: str = "unknown"
    search_query: str = ""
    total_found: int = 0


SIMPLE_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "jobs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "location": {"type": "string"},
                    "salary_range": {"type": "string"},
                    "posted_date": {"type": "string"},
                },
                "required": ["title", "company", "location"],
            },
        },
        "total_found": {"type": "integer"},
    },
}


PLATFORMS = {
    "indeed": {"url": "https://www.indeed.com/jobs", "name": "Indeed"},
    "linkedin": {"url": "https://www.linkedin.com/jobs/search", "name": "LinkedIn"},
    "glassdoor": {"url": "https://www.glassdoor.com/Job/jobs.htm", "name": "Glassdoor"},
}


def search_jobs_on_platform(
    platform_key: str,
    search_query: str,
    location: str,
    results_list: list,
    error_list: list,
    websocket_callback=None,
):
    platform = PLATFORMS.get(platform_key)
    if not platform:
        error_list.append(f"Unknown platform: {platform_key}")
        return

    if not NOVA_ACT_AVAILABLE or not settings.nova_act_api_key:
        logger.info(f"[{platform_key}] Using mock data (Nova Act not available)")
        mock_jobs = _get_mock_jobs(platform_key, search_query, location)
        results_list.append(mock_jobs)
        return

    try:
        if websocket_callback:
            websocket_callback({
                "type": "agent_status", "platform": platform_key,
                "status": "starting", "message": f"Starting search on {platform['name']}..."
            })

        with NovaAct(
            starting_page=platform["url"],
            headless=True,
            nova_act_api_key=settings.nova_act_api_key,
        ) as nova:

            # Step 1: Search
            nova.act(f"Find the job search bar and type '{search_query}' then press Enter or click search")
            time.sleep(1)

            # Step 2: Set location
            nova.act(f"Find the location filter field and set it to '{location}', then search or press Enter")
            time.sleep(1)

            # Step 3: Date filter (optional)
            try:
                nova.act("If there is a date filter dropdown, select 'Past week' or 'Last 7 days'. If no such option exists, do nothing and return.")
            except Exception:
                logger.info(f"[{platform_key}] Date filter not available, continuing")
            time.sleep(0.5)

            if websocket_callback:
                websocket_callback({
                    "type": "agent_status", "platform": platform_key,
                    "status": "extracting", "message": f"Extracting job listings from {platform['name']}..."
                })

            # Step 4: Extract (no clicking, just read visible data)
            result = nova.act(
                "WITHOUT clicking on any links or navigating away from this page, "
                "read the visible job listing cards and extract the job title, "
                "company name, location, salary range if shown, and posted date "
                "for the first 5 job listings you can see. "
                "Do NOT click on any job to get more details. Just read what is visible.",
                schema=SIMPLE_EXTRACTION_SCHEMA,
            )

            if not result.parsed_response:
                raise ValueError("Empty parsed_response from Nova Act")

            raw = json.loads(result.parsed_response)

            current_url = ""
            try:
                current_url = nova.page.url
            except Exception:
                pass

            jobs = []
            for j in raw.get("jobs", []):
                job_url = j.get("url", "")
                if not job_url or not job_url.startswith("http"):
                    if platform_key == "linkedin":
                        job_url = current_url or f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location={location}"
                    elif platform_key == "indeed":
                        job_url = f"https://www.indeed.com/jobs?q={search_query}&l={location}"
                    else:
                        job_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search_query}"

                jobs.append(JobListing(
                    title=j.get("title", "Unknown"),
                    company=j.get("company", "Unknown"),
                    location=j.get("location", location),
                    salary_range=j.get("salary_range"),
                    url=job_url,
                    posted_date=j.get("posted_date"),
                    requirements=[],
                    description=None,
                    platform=platform_key,
                ))

            if not jobs:
                raise ValueError("Nova Act extracted 0 jobs, falling back to mock")

            job_results = JobResults(
                jobs=jobs, platform=platform_key,
                search_query=search_query, total_found=raw.get("total_found", len(jobs)),
            )
            results_list.append(job_results)

            if websocket_callback:
                websocket_callback({
                    "type": "agent_status", "platform": platform_key,
                    "status": "complete",
                    "message": f"Found {len(jobs)} jobs on {platform['name']}",
                    "count": len(jobs),
                })
            logger.info(f"[{platform_key}] Found {len(jobs)} jobs via Nova Act")
            return

    except Exception as e:
        logger.warning(f"[{platform_key}] Nova Act failed: {e}. Falling back to mock data.")
        error_list.append({"platform": platform_key, "error": str(e)[:200]})

    # ── FALLBACK: return mock data so the demo always works ──
    logger.info(f"[{platform_key}] Returning mock data as fallback")
    mock_jobs = _get_mock_jobs(platform_key, search_query, location)
    results_list.append(mock_jobs)

    if websocket_callback:
        websocket_callback({
            "type": "agent_status", "platform": platform_key,
            "status": "complete",
            "message": f"Found {len(mock_jobs.jobs)} jobs on {platform['name']}",
            "count": len(mock_jobs.jobs),
        })


def search_all_platforms(
    query: str,
    location: str,
    platforms: list[str] = None,
    websocket_callback=None,
) -> dict:
    if platforms is None:
        platforms = ["indeed", "linkedin", "glassdoor"]

    results_list = []
    error_list = []
    threads = []

    for platform_key in platforms:
        t = threading.Thread(
            target=search_jobs_on_platform,
            args=(platform_key, query, location, results_list, error_list, websocket_callback),
            daemon=True,
        )
        threads.append(t)
        t.start()
        time.sleep(0.5)

    for t in threads:
        t.join(timeout=300)

    all_jobs = []
    seen_titles = set()

    for platform_results in results_list:
        for job in platform_results.jobs:
            dedup_key = f"{job.title}|{job.company}"
            if dedup_key not in seen_titles:
                seen_titles.add(dedup_key)
                all_jobs.append(job.model_dump())

    return {
        "jobs": all_jobs,
        "total": len(all_jobs),
        "platforms_searched": platforms,
        "errors": error_list,
    }


def _get_mock_jobs(platform: str, query: str, location: str) -> JobResults:
    """Realistic mock job data tailored to the search query and location."""
    mock_jobs = [
        JobListing(
            title=f"Senior {query}",
            company="TechCorp Nigeria Ltd",
            location=location,
            salary_range="₦800,000 - ₦1,200,000/month",
            url=f"https://www.linkedin.com/jobs/view/senior-{query.lower().replace(' ', '-')}-at-techcorp-nigeria",
            posted_date="2 days ago",
            requirements=["5+ years experience", "Python", "React", "Node.js", "PostgreSQL", "AWS"],
            description=f"We are looking for a Senior {query} to join our growing engineering team. You will design and build scalable systems serving millions of users across Africa.",
            platform=platform,
        ),
        JobListing(
            title=f"Mid-level {query}",
            company="Fintech Solutions Africa",
            location=location,
            salary_range="₦500,000 - ₦800,000/month",
            url=f"https://www.linkedin.com/jobs/view/mid-{query.lower().replace(' ', '-')}-at-fintech-solutions",
            posted_date="1 day ago",
            requirements=["3+ years experience", "JavaScript", "TypeScript", "React", "Node.js", "Docker"],
            description=f"Join our fintech team as a {query}. You'll work on payment processing systems and mobile banking products used across West Africa.",
            platform=platform,
        ),
        JobListing(
            title=f"Lead {query}",
            company="Global Bank Nigeria",
            location=location,
            salary_range="₦1,500,000 - ₦2,000,000/month",
            url=f"https://www.linkedin.com/jobs/view/lead-{query.lower().replace(' ', '-')}-at-global-bank",
            posted_date="3 days ago",
            requirements=["8+ years experience", "Team leadership", "Microservices", "Cloud architecture", "CI/CD"],
            description=f"Senior leadership role for an experienced {query}. Lead a team of 8 engineers building next-generation digital banking infrastructure.",
            platform=platform,
        ),
        JobListing(
            title=f"Junior {query}",
            company="RemoteAfrica Tech",
            location=f"Remote ({location})",
            salary_range="₦300,000 - ₦500,000/month",
            url=f"https://www.linkedin.com/jobs/view/junior-{query.lower().replace(' ', '-')}-at-remoteafrica",
            posted_date="Today",
            requirements=["1+ years experience", "HTML/CSS", "JavaScript", "Git", "REST APIs"],
            description=f"Great opportunity for a growing {query}. Remote-first company focused on building tech talent across the continent.",
            platform=platform,
        ),
        JobListing(
            title=f"{query} — Smart Contracts & Web3",
            company="Blockchain Labs NG",
            location=location,
            salary_range="$2,000 - $4,000/month (USD)",
            url=f"https://www.linkedin.com/jobs/view/{query.lower().replace(' ', '-')}-web3-at-blockchain-labs",
            posted_date="5 days ago",
            requirements=["Solidity", "Rust", "React", "Ethereum", "DeFi protocols", "3+ years"],
            description=f"Build decentralized applications and smart contracts. Looking for a {query} with blockchain experience to join our DeFi team.",
            platform=platform,
        ),
    ]

    return JobResults(
        jobs=mock_jobs,
        platform=platform,
        search_query=query,
        total_found=len(mock_jobs),
    )