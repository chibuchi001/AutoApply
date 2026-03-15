"""
S3 service for storing resumes, cover letters, and agent screenshots.
Falls back gracefully to local disk when S3 is not configured.
"""

import os
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)

# Local fallback directory when S3 not configured
LOCAL_STORAGE = Path("uploads")
LOCAL_STORAGE.mkdir(exist_ok=True)

s3_available = bool(settings.aws_access_key_id and settings.s3_bucket_name)

if s3_available:
    try:
        s3_client = boto3.client(
            "s3",
            region_name=settings.s3_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=Config(retries={"max_attempts": 3}),
        )
    except Exception as e:
        logger.warning(f"S3 client init failed: {e}. Using local storage.")
        s3_available = False
        s3_client = None
else:
    s3_client = None
    logger.info("S3 not configured — using local disk storage")


def upload_resume(local_path: str, user_id: str, filename: str) -> str:
    """
    Upload a resume PDF to S3 (or keep locally).
    Returns the S3 key or local path.
    """
    s3_key = f"resumes/{user_id}/{filename}"

    if not s3_available or s3_client is None:
        logger.info(f"S3 not available — resume stored locally at {local_path}")
        return local_path

    try:
        s3_client.upload_file(
            local_path,
            settings.s3_bucket_name,
            s3_key,
            ExtraArgs={"ContentType": "application/pdf", "ServerSideEncryption": "AES256"},
        )
        logger.info(f"Resume uploaded to s3://{settings.s3_bucket_name}/{s3_key}")
        return s3_key
    except (ClientError, NoCredentialsError) as e:
        logger.error(f"S3 upload failed: {e}. Using local path.")
        return local_path


def upload_cover_letter(content: str, user_id: str, job_id: str) -> str:
    """
    Upload a generated cover letter as a text file to S3.
    Returns the S3 key or local path.
    """
    filename = f"cover_letter_{job_id}.txt"
    s3_key = f"cover_letters/{user_id}/{filename}"

    if not s3_available or s3_client is None:
        local_path = LOCAL_STORAGE / filename
        local_path.write_text(content, encoding="utf-8")
        return str(local_path)

    try:
        s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=content.encode("utf-8"),
            ContentType="text/plain",
            ServerSideEncryption="AES256",
        )
        logger.info(f"Cover letter uploaded to s3://{settings.s3_bucket_name}/{s3_key}")
        return s3_key
    except (ClientError, NoCredentialsError) as e:
        logger.error(f"S3 cover letter upload failed: {e}")
        return ""


def upload_screenshot(local_path: str, user_id: str, session_id: str, name: str) -> str:
    """Upload agent screenshot to S3 for audit trail."""
    s3_key = f"screenshots/{user_id}/{session_id}/{name}"

    if not s3_available or s3_client is None:
        return local_path

    try:
        s3_client.upload_file(
            local_path,
            settings.s3_bucket_name,
            s3_key,
            ExtraArgs={"ContentType": "image/png"},
        )
        return s3_key
    except Exception as e:
        logger.error(f"Screenshot upload failed: {e}")
        return local_path


def get_presigned_url(s3_key: str, expires_in: int = 3600) -> str:
    """
    Generate a presigned URL to allow temporary access to an S3 object.
    Used for sharing resume download links.
    """
    if not s3_available or s3_client is None or not s3_key.startswith("resumes/"):
        return s3_key  # Return the key/path as-is

    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": s3_key},
            ExpiresIn=expires_in,
        )
        return url
    except Exception as e:
        logger.error(f"Presigned URL generation failed: {e}")
        return ""


def download_resume(s3_key: str, destination: str) -> str:
    """
    Download a resume from S3 to a local path.
    Returns the local path.
    """
    if not s3_available or s3_client is None or not s3_key.startswith("resumes/"):
        # It's already a local path
        return s3_key

    try:
        s3_client.download_file(settings.s3_bucket_name, s3_key, destination)
        logger.info(f"Resume downloaded from S3 to {destination}")
        return destination
    except Exception as e:
        logger.error(f"S3 download failed: {e}")
        return s3_key


def ensure_bucket_exists() -> bool:
    """Create the S3 bucket if it doesn't exist. Call once on startup."""
    if not s3_available or s3_client is None:
        return False

    try:
        s3_client.head_bucket(Bucket=settings.s3_bucket_name)
        logger.info(f"S3 bucket '{settings.s3_bucket_name}' is accessible")
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            try:
                if settings.s3_region == "us-east-1":
                    s3_client.create_bucket(Bucket=settings.s3_bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=settings.s3_bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": settings.s3_region},
                    )
                logger.info(f"Created S3 bucket '{settings.s3_bucket_name}'")
                return True
            except Exception as create_err:
                logger.error(f"Failed to create S3 bucket: {create_err}")
                return False
        else:
            logger.error(f"S3 bucket check failed: {e}")
            return False
