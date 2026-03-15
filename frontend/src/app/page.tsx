'use client';

import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';

function useInView(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } },
      { threshold }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, visible };
}

export default function LandingPage() {
  const [mounted, setMounted] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const hero = useInView(0.1);
  const powered = useInView();
  const features = useInView(0.08);
  const steps = useInView(0.08);
  const mockup = useInView(0.1);
  const africa = useInView();

  useEffect(() => { setMounted(true); }, []);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handler);
    return () => window.removeEventListener('mousemove', handler);
  }, []);

  return (
    <div className={`lr ${mounted ? 'lr--ready' : ''}`}>
      <style jsx global>{`
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Instrument+Serif:ital@0;1&display=swap');

:root {
  --bg: #060609;
  --bg2: #0c0c14;
  --card: #0f0f1a;
  --v: #7C3AED;
  --v2: #A78BFA;
  --v3: #C4B5FD;
  --o: #F97316;
  --o2: #FB923C;
  --g: #10B981;
  --g2: #34D399;
  --b: #3B82F6;
  --t1: #F8FAFC;
  --t2: #94A3B8;
  --t3: #475569;
  --border: rgba(255,255,255,0.05);
  --glow-v: rgba(124,58,237,0.25);
  --glow-o: rgba(249,115,22,0.2);
}

*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--t1);font-family:'Outfit',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased}

.lr{opacity:0;transition:opacity .5s}.lr--ready{opacity:1}

/* cursor glow */
.cursor-glow{position:fixed;width:600px;height:600px;border-radius:50%;pointer-events:none;z-index:0;background:radial-gradient(circle,rgba(124,58,237,0.07) 0%,transparent 70%);transform:translate(-50%,-50%);transition:left .3s ease-out,top .3s ease-out}

/* grain */
.grain{position:fixed;inset:0;z-index:9999;pointer-events:none;opacity:.025;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}

/* anim */
.reveal{opacity:0;transform:translateY(40px);transition:opacity .8s cubic-bezier(.16,1,.3,1),transform .8s cubic-bezier(.16,1,.3,1)}
.reveal.in{opacity:1;transform:translateY(0)}
.reveal-d1{transition-delay:.1s}
.reveal-d2{transition-delay:.2s}
.reveal-d3{transition-delay:.3s}
.reveal-d4{transition-delay:.4s}
.reveal-d5{transition-delay:.5s}
.reveal-d6{transition-delay:.6s}

/* ── NAV ── */
.nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;backdrop-filter:blur(24px) saturate(1.2);background:rgba(6,6,9,.65);border-bottom:1px solid var(--border)}
.nav-left{display:flex;align-items:center;gap:.6rem;text-decoration:none}
.nav-mark{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,var(--v),var(--o));display:grid;place-items:center;font-size:14px;font-weight:800;color:#fff;box-shadow:0 0 20px var(--glow-v)}
.nav-word{font-weight:700;font-size:1.05rem;color:var(--t1);letter-spacing:-.02em}
.nav-mid{display:flex;gap:2.5rem}
.nav-mid a{color:var(--t2);text-decoration:none;font-size:.82rem;font-weight:500;transition:color .2s}
.nav-mid a:hover{color:var(--t1)}
.nav-go{display:inline-flex;align-items:center;gap:.4rem;background:var(--v);color:#fff;padding:.55rem 1.4rem;border-radius:100px;font-size:.82rem;font-weight:600;text-decoration:none;border:none;cursor:pointer;transition:all .25s;box-shadow:0 0 24px var(--glow-v)}
.nav-go:hover{transform:translateY(-1px);box-shadow:0 0 36px var(--glow-v);background:#6D28D9}

/* ── HERO ── */
.hero{position:relative;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:7rem 2rem 4rem;overflow:hidden}
.hero-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(124,58,237,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,.04) 1px,transparent 1px);background-size:60px 60px;mask-image:radial-gradient(ellipse 70% 50% at 50% 50%,black 30%,transparent 100%)}
.hero-orb{position:absolute;border-radius:50%;filter:blur(100px);animation:orbPulse 10s ease-in-out infinite}
.hero-orb.o1{width:500px;height:500px;background:var(--v);top:-15%;left:10%;opacity:.12}
.hero-orb.o2{width:400px;height:400px;background:var(--o);bottom:5%;right:5%;opacity:.08;animation-delay:-5s}
.hero-orb.o3{width:250px;height:250px;background:var(--g);top:50%;left:55%;opacity:.06;animation-delay:-3s}
@keyframes orbPulse{0%,100%{transform:scale(1) translate(0,0)}50%{transform:scale(1.15) translate(20px,-15px)}}

.hero-chip{display:inline-flex;align-items:center;gap:.5rem;padding:.45rem 1.1rem;border-radius:100px;background:rgba(249,115,22,.08);border:1px solid rgba(249,115,22,.18);font-size:.75rem;font-weight:600;color:var(--o2);margin-bottom:2rem;letter-spacing:.04em}
.hero-chip-dot{width:6px;height:6px;border-radius:50%;background:var(--o);animation:chipPulse 2s ease-in-out infinite}
@keyframes chipPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.4)}}

.hero-h1{font-family:'Instrument Serif',serif;font-size:clamp(3.2rem,8vw,6.5rem);font-weight:400;line-height:1;letter-spacing:-.04em;max-width:900px;margin-bottom:1.5rem}
.hero-h1 em{font-style:italic;background:linear-gradient(135deg,var(--v2),var(--o2),var(--g2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

.hero-p{font-size:clamp(.95rem,1.8vw,1.15rem);color:var(--t2);max-width:520px;line-height:1.7;margin-bottom:2.5rem;font-weight:400}

.hero-btns{display:flex;gap:.75rem;flex-wrap:wrap;justify-content:center}
.btn-main{display:inline-flex;align-items:center;gap:.5rem;background:linear-gradient(135deg,var(--v),#6D28D9);color:#fff;padding:.95rem 2.4rem;border-radius:100px;font-size:.95rem;font-weight:600;text-decoration:none;border:none;cursor:pointer;transition:all .3s;box-shadow:0 4px 30px var(--glow-v),inset 0 1px 0 rgba(255,255,255,.1)}
.btn-main:hover{transform:translateY(-2px) scale(1.02);box-shadow:0 8px 40px var(--glow-v)}
.btn-ghost{display:inline-flex;align-items:center;gap:.5rem;background:rgba(255,255,255,.04);color:var(--t1);padding:.95rem 2.4rem;border-radius:100px;font-size:.95rem;font-weight:500;text-decoration:none;border:1px solid rgba(255,255,255,.08);cursor:pointer;transition:all .3s;backdrop-filter:blur(8px)}
.btn-ghost:hover{border-color:rgba(255,255,255,.15);background:rgba(255,255,255,.07);transform:translateY(-1px)}

.hero-metrics{display:flex;gap:3.5rem;margin-top:4rem;padding-top:3rem;border-top:1px solid var(--border)}
.metric{text-align:center}
.metric-val{font-family:'Instrument Serif',serif;font-size:2.2rem;font-weight:400;letter-spacing:-.02em}
.metric-val.c-v{color:var(--v2)}.metric-val.c-o{color:var(--o2)}.metric-val.c-g{color:var(--g2)}.metric-val.c-b{color:var(--b)}
.metric-lbl{font-size:.65rem;text-transform:uppercase;letter-spacing:.14em;color:var(--t3);margin-top:.2rem;font-weight:600}

/* ── LOGOS ── */
.logos{padding:3.5rem 2rem;border-top:1px solid var(--border);border-bottom:1px solid var(--border);background:var(--bg2);overflow:hidden}
.logos-label{font-size:.6rem;text-transform:uppercase;letter-spacing:.18em;color:var(--t3);text-align:center;margin-bottom:1.5rem;font-weight:700}
.logos-row{display:flex;justify-content:center;align-items:center;gap:2rem;flex-wrap:wrap}
.logo-pill{display:flex;align-items:center;gap:.5rem;padding:.5rem 1rem;border-radius:100px;border:1px solid var(--border);background:rgba(255,255,255,.02);transition:all .3s}
.logo-pill:hover{border-color:rgba(124,58,237,.2);background:rgba(124,58,237,.04);transform:translateY(-1px)}
.logo-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.logo-dot.d-o{background:var(--o)}.logo-dot.d-v{background:var(--v2)}.logo-dot.d-g{background:var(--g)}.logo-dot.d-b{background:var(--b)}.logo-dot.d-y{background:#EAB308}
.logo-name{font-size:.78rem;color:var(--t2);font-weight:500}

/* ── FEATURES ── */
.feat{padding:7rem 2rem;max-width:1200px;margin:0 auto}
.eyebrow{font-size:.65rem;text-transform:uppercase;letter-spacing:.18em;color:var(--v2);text-align:center;margin-bottom:.5rem;font-weight:700}
.sect-h{font-family:'Instrument Serif',serif;font-size:clamp(2rem,4vw,3.2rem);text-align:center;margin-bottom:.75rem;letter-spacing:-.03em;font-weight:400}
.sect-p{text-align:center;color:var(--t2);max-width:460px;margin:0 auto 4rem;font-size:.95rem;line-height:1.6}
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
.feat-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.75rem;transition:all .4s cubic-bezier(.25,.46,.45,.94);position:relative;overflow:hidden}
.feat-card::after{content:'';position:absolute;inset:0;border-radius:16px;opacity:0;transition:opacity .4s;background:radial-gradient(circle at 50% 0%,rgba(124,58,237,.08),transparent 70%)}
.feat-card:hover{border-color:rgba(124,58,237,.15);transform:translateY(-6px);box-shadow:0 24px 60px rgba(0,0,0,.4)}
.feat-card:hover::after{opacity:1}
.feat-emoji{font-size:1.75rem;margin-bottom:1rem;display:block}
.feat-name{font-size:1rem;font-weight:700;margin-bottom:.4rem;letter-spacing:-.01em;position:relative;z-index:1}
.feat-desc{font-size:.85rem;color:var(--t2);line-height:1.6;position:relative;z-index:1}
.feat-tag{display:inline-block;margin-top:.75rem;padding:.2rem .6rem;border-radius:100px;font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;position:relative;z-index:1}
.feat-tag.tag-v{background:rgba(124,58,237,.12);color:var(--v2)}
.feat-tag.tag-o{background:rgba(249,115,22,.12);color:var(--o2)}
.feat-tag.tag-g{background:rgba(16,185,129,.12);color:var(--g2)}
.feat-tag.tag-b{background:rgba(59,130,246,.12);color:var(--b)}

/* ── MOCKUP ── */
.mockup-sect{padding:5rem 2rem;max-width:1100px;margin:0 auto}
.mockup-frame{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,.5),0 0 60px var(--glow-v);position:relative}
.mockup-bar{display:flex;align-items:center;gap:.5rem;padding:.75rem 1rem;background:rgba(255,255,255,.03);border-bottom:1px solid var(--border)}
.mockup-dot{width:10px;height:10px;border-radius:50%}
.mockup-dot.r{background:#EF4444}.mockup-dot.y{background:#EAB308}.mockup-dot.g{background:#22C55E}
.mockup-url{flex:1;text-align:center;font-size:.7rem;color:var(--t3);font-weight:500}
.mockup-body{display:grid;grid-template-columns:1fr 2fr;min-height:420px}
.mock-sidebar{padding:1.5rem;border-right:1px solid var(--border);display:flex;flex-direction:column;gap:1rem}
.mock-widget{background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:10px;padding:1rem}
.mock-widget-title{font-size:.7rem;font-weight:700;color:var(--t2);margin-bottom:.6rem;display:flex;align-items:center;gap:.4rem}
.mock-skill-row{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.4rem}
.mock-skill{padding:.15rem .5rem;border-radius:100px;font-size:.55rem;font-weight:600;background:rgba(124,58,237,.1);color:var(--v2);border:1px solid rgba(124,58,237,.15)}
.mock-main{padding:1.5rem;display:flex;flex-direction:column;gap:.75rem}
.mock-feed{background:rgba(0,0,0,.3);border-radius:10px;padding:.75rem;font-family:monospace;font-size:.6rem;color:var(--g2);line-height:1.8;border:1px solid var(--border)}
.mock-feed-line{opacity:0;animation:feedIn .3s forwards}
@keyframes feedIn{to{opacity:1}}
.mock-job-card{background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:10px;padding:.75rem 1rem;display:flex;justify-content:space-between;align-items:center;transition:border-color .2s}
.mock-job-card:hover{border-color:rgba(124,58,237,.2)}
.mock-job-title{font-size:.75rem;font-weight:700}
.mock-job-co{font-size:.6rem;color:var(--t2);margin-top:.15rem}
.mock-job-right{display:flex;align-items:center;gap:.5rem}
.mock-badge{padding:.15rem .5rem;border-radius:100px;font-size:.55rem;font-weight:700}
.mock-badge.badge-green{background:rgba(16,185,129,.12);color:var(--g2)}
.mock-btn-sm{padding:.25rem .6rem;border-radius:6px;font-size:.55rem;font-weight:700;background:var(--v);color:#fff;border:none;cursor:default}

/* ── STEPS ── */
.steps-sect{padding:7rem 2rem;background:var(--bg2);border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
.steps-box{max-width:800px;margin:0 auto;display:flex;flex-direction:column;gap:0}
.stp{display:flex;gap:1.75rem;padding-bottom:2.5rem}
.stp:last-child{padding-bottom:0}
.stp-left{display:flex;flex-direction:column;align-items:center;flex-shrink:0}
.stp-num{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,var(--v),var(--o));display:grid;place-items:center;font-weight:800;font-size:1rem;color:#fff;box-shadow:0 0 24px var(--glow-v)}
.stp-line{width:2px;flex:1;background:linear-gradient(180deg,rgba(124,58,237,.3),transparent);margin-top:.5rem;min-height:30px}
.stp:last-child .stp-line{display:none}
.stp-right{padding-top:.4rem}
.stp-title{font-size:1.1rem;font-weight:700;margin-bottom:.35rem;letter-spacing:-.01em}
.stp-text{color:var(--t2);font-size:.9rem;line-height:1.6}

/* ── AFRICA ── */
.africa{padding:7rem 2rem;text-align:center;position:relative;overflow:hidden}
.africa-glow{position:absolute;width:500px;height:500px;border-radius:50%;background:var(--o);filter:blur(150px);opacity:.06;top:50%;left:50%;transform:translate(-50%,-50%)}
.africa-q{font-family:'Instrument Serif',serif;font-size:clamp(1.6rem,3.5vw,2.6rem);font-weight:400;line-height:1.35;max-width:750px;margin:0 auto 1.25rem;letter-spacing:-.02em;position:relative;z-index:1}
.africa-q em{font-style:italic;color:var(--o2)}
.africa-sub{color:var(--t2);font-size:.95rem;line-height:1.7;max-width:550px;margin:0 auto 2.5rem;position:relative;z-index:1}

/* ── FOOTER ── */
.foot{padding:2.5rem 2rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;max-width:1200px;margin:0 auto;flex-wrap:wrap;gap:1rem}
.foot-l{font-size:.75rem;color:var(--t3)}
.foot-r{display:flex;gap:1.5rem}
.foot-r a{color:var(--t3);text-decoration:none;font-size:.75rem;transition:color .2s}
.foot-r a:hover{color:var(--t2)}

/* ── RESPONSIVE ── */
@media(max-width:900px){
  .feat-grid{grid-template-columns:1fr 1fr}
  .mockup-body{grid-template-columns:1fr}
  .mock-sidebar{display:none}
}
@media(max-width:640px){
  .nav-mid{display:none}
  .feat-grid{grid-template-columns:1fr}
  .hero-metrics{flex-wrap:wrap;gap:1.5rem;justify-content:center}
  .hero-btns{flex-direction:column;align-items:center}
  .foot{justify-content:center;text-align:center}
}
      `}</style>

      <div className="grain" />
      <div className="cursor-glow" style={{ left: mousePos.x, top: mousePos.y }} />

      {/* NAV */}
      <nav className="nav">
        <Link href="/" className="nav-left">
          <div className="nav-mark">⚡</div>
          <span className="nav-word">AutoApply</span>
        </Link>
        <div className="nav-mid">
          <a href="#features">Features</a>
          <a href="#preview">Preview</a>
          <a href="#how-it-works">How It Works</a>
          <a href="https://github.com/chibuchi001/AutoApply" target="_blank" rel="noopener noreferrer">GitHub</a>
        </div>
        <Link href="/app" className="nav-go">Launch App →</Link>
      </nav>

      {/* HERO */}
      <section className="hero" ref={hero.ref}>
        <div className="hero-grid" />
        <div className="hero-orb o1" />
        <div className="hero-orb o2" />
        <div className="hero-orb o3" />

        <div className={`reveal ${hero.visible ? 'in' : ''}`}>
          <div className="hero-chip">
            <span className="hero-chip-dot" />
            Amazon Nova Hackathon 2026
          </div>
        </div>

        <h1 className={`hero-h1 reveal reveal-d1 ${hero.visible ? 'in' : ''}`}>
          Stop Applying.<br /><em>Start Getting Hired.</em>
        </h1>

        <p className={`hero-p reveal reveal-d2 ${hero.visible ? 'in' : ''}`}>
          An AI agent fleet that searches job boards, matches your skills,
          writes cover letters, applies for you, and coaches you through
          interviews — all powered by Amazon Nova.
        </p>

        <div className={`hero-btns reveal reveal-d3 ${hero.visible ? 'in' : ''}`}>
          <Link href="/app" className="btn-main">⚡ Get Started Free</Link>
          <a href="https://github.com/chibuchi001/AutoApply" target="_blank" rel="noopener noreferrer" className="btn-ghost">
            ✦ View Source
          </a>
        </div>

        <div className={`hero-metrics reveal reveal-d4 ${hero.visible ? 'in' : ''}`}>
          <div className="metric"><div className="metric-val c-v">3+</div><div className="metric-lbl">Job Boards</div></div>
          <div className="metric"><div className="metric-val c-o">34</div><div className="metric-lbl">Skills Parsed</div></div>
          <div className="metric"><div className="metric-val c-g">5×</div><div className="metric-lbl">Faster Apply</div></div>
          <div className="metric"><div className="metric-val c-b">100%</div><div className="metric-lbl">AI-Powered</div></div>
        </div>
      </section>

      {/* LOGOS */}
      <section className="logos" ref={powered.ref}>
        <div className="logos-label">Built on Amazon Nova &amp; AWS</div>
        <div className={`logos-row reveal ${powered.visible ? 'in' : ''}`}>
          {[
            { name: 'Nova Act', dot: 'd-o' },
            { name: 'Nova 2 Lite', dot: 'd-v' },
            { name: 'Nova 2 Sonic', dot: 'd-g' },
            { name: 'Bedrock', dot: 'd-b' },
            { name: 'Amazon S3', dot: 'd-y' },
          ].map((l) => (
            <div className="logo-pill" key={l.name}>
              <div className={`logo-dot ${l.dot}`} />
              <span className="logo-name">{l.name}</span>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section className="feat" id="features" ref={features.ref}>
        <div className="eyebrow">Features</div>
        <h2 className="sect-h">Your AI Career Team</h2>
        <p className="sect-p">Three Nova models. Six capabilities. One mission: get you hired.</p>

        <div className="feat-grid">
          {[
            { emoji: '🔍', name: 'Parallel Search', desc: 'Nova Act launches browser agents across Indeed, LinkedIn & Glassdoor simultaneously — extracting jobs in real time.', tag: 'Nova Act', tc: 'tag-o' },
            { emoji: '🎯', name: 'Smart Matching', desc: 'Nova 2 Lite scores every job 0–100, identifies skill gaps, and tells you exactly how to address them.', tag: 'Nova 2 Lite', tc: 'tag-v' },
            { emoji: '✍️', name: 'Cover Letters', desc: 'Unique, cliché-free cover letters tailored to each job — highlighting your most relevant experience.', tag: 'Nova 2 Lite', tc: 'tag-v' },
            { emoji: '🤖', name: 'Auto-Apply', desc: 'Nova Act fills forms, uploads your resume, and answers screening questions. CAPTCHAs are escalated to you.', tag: 'Nova Act', tc: 'tag-o' },
            { emoji: '🎙️', name: 'Voice Coach', desc: 'Nova 2 Sonic conducts mock interviews with real-time voice feedback, tailored to each specific role.', tag: 'Nova 2 Sonic', tc: 'tag-g' },
            { emoji: '📡', name: 'Live Agent Feed', desc: 'Watch every agent action via WebSocket streaming. Full transparency into what your AI is doing.', tag: 'WebSocket', tc: 'tag-b' },
          ].map((f, i) => (
            <div className={`feat-card reveal reveal-d${i + 1} ${features.visible ? 'in' : ''}`} key={f.name}>
              <span className="feat-emoji">{f.emoji}</span>
              <div className="feat-name">{f.name}</div>
              <div className="feat-desc">{f.desc}</div>
              <span className={`feat-tag ${f.tc}`}>{f.tag}</span>
            </div>
          ))}
        </div>
      </section>

      {/* MOCKUP */}
      <section className="mockup-sect" id="preview" ref={mockup.ref}>
        <div className="eyebrow">App Preview</div>
        <h2 className="sect-h">See It In Action</h2>
        <p className="sect-p">Real-time job search, matching, and application tracking</p>

        <div className={`mockup-frame reveal ${mockup.visible ? 'in' : ''}`}>
          <div className="mockup-bar">
            <div className="mockup-dot r" /><div className="mockup-dot y" /><div className="mockup-dot g" />
            <div className="mockup-url">auto-apply-beta.vercel.app/app</div>
          </div>
          <div className="mockup-body">
            <div className="mock-sidebar">
              <div className="mock-widget">
                <div className="mock-widget-title">📋 Resume Parsed</div>
                <div style={{ fontSize: '.65rem', color: 'var(--t2)' }}>Experience: 3 yrs · Skills: 34</div>
                <div className="mock-skill-row">
                  {['Python', 'React', 'Node.js', 'FastAPI', 'TypeScript', 'AWS', 'Docker', 'PostgreSQL'].map(s => (
                    <span className="mock-skill" key={s}>{s}</span>
                  ))}
                </div>
              </div>
              <div className="mock-widget">
                <div className="mock-widget-title">🔍 Search Config</div>
                <div style={{ fontSize: '.65rem', color: 'var(--t2)', lineHeight: 1.8 }}>
                  Role: Smart Contract Developer<br />
                  Location: Lagos, Nigeria<br />
                  Platforms: LinkedIn<br />
                  Min Match: 40%
                </div>
              </div>
            </div>
            <div className="mock-main">
              <div className="mock-feed">
                {[
                  { time: '15:02', tag: 'SEARCH', text: 'Starting parallel search across 3 platforms...' },
                  { time: '15:05', tag: 'SEARCH', text: 'Found 5 jobs across 1 platforms' },
                  { time: '15:05', tag: 'MATCH', text: 'Analyzing match scores for 5 jobs...' },
                  { time: '15:06', tag: 'COVER', text: 'Generating tailored cover letters...' },
                  { time: '15:07', tag: 'DONE', text: 'Ready to apply to 5 matched jobs.' },
                ].map((l, i) => (
                  <div className="mock-feed-line" key={i} style={{ animationDelay: `${mockup.visible ? i * 0.4 : 0}s` }}>
                    <span style={{ color: 'var(--t3)' }}>{l.time}</span>{' '}
                    <span style={{ color: l.tag === 'DONE' ? 'var(--g2)' : l.tag === 'SEARCH' ? 'var(--v2)' : 'var(--o2)' }}>[{l.tag}]</span>{' '}
                    {l.text}
                  </div>
                ))}
              </div>
              {[
                { title: 'Senior Smart Contract Developer', co: 'TechCorp Nigeria Ltd', score: '85%' },
                { title: 'Mid-level Blockchain Engineer', co: 'Fintech Solutions Africa', score: '72%' },
                { title: 'Lead Web3 Developer', co: 'Global Bank Nigeria', score: '68%' },
              ].map((j) => (
                <div className="mock-job-card" key={j.title}>
                  <div>
                    <div className="mock-job-title">{j.title}</div>
                    <div className="mock-job-co">{j.co}</div>
                  </div>
                  <div className="mock-job-right">
                    <span className="mock-badge badge-green">{j.score} match</span>
                    <span className="mock-btn-sm">Apply</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="steps-sect" id="how-it-works" ref={steps.ref}>
        <div className="eyebrow">How It Works</div>
        <h2 className="sect-h">Four Steps to Your Next Job</h2>
        <p className="sect-p">From resume upload to interview prep in under 5 minutes</p>

        <div className="steps-box">
          {[
            { n: '1', t: 'Upload Your Resume', d: 'Drop your PDF and Nova 2 Lite extracts 34+ data points — skills, experience, education, contact info — instantly.' },
            { n: '2', t: 'Set Your Preferences', d: 'Choose your target role, location, platforms, and minimum match score. Toggle dry-run mode to test safely.' },
            { n: '3', t: 'Watch Agents Work', d: 'Nova Act browser agents search job boards in parallel. Each job gets a match score, gap analysis, and tailored cover letter.' },
            { n: '4', t: 'Apply & Practice', d: 'One-click apply with Nova Act. Then practice with Nova 2 Sonic\'s voice coach — tailored questions for each specific role.' },
          ].map((s, i) => (
            <div className={`stp reveal reveal-d${i + 1} ${steps.visible ? 'in' : ''}`} key={s.n}>
              <div className="stp-left">
                <div className="stp-num">{s.n}</div>
                <div className="stp-line" />
              </div>
              <div className="stp-right">
                <div className="stp-title">{s.t}</div>
                <div className="stp-text">{s.d}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* AFRICA */}
      <section className="africa" ref={africa.ref}>
        <div className="africa-glow" />
        <p className={`africa-q reveal ${africa.visible ? 'in' : ''}`}>
          A developer in Lagos with identical skills shouldn&apos;t lose opportunities
          because they can&apos;t spend <em>40 hours a week</em> on applications.
        </p>
        <p className={`africa-sub reveal reveal-d1 ${africa.visible ? 'in' : ''}`}>
          AutoApply levels the playing field — giving every developer in Lagos,
          Nairobi, and Accra the same AI-powered tools as candidates in San Francisco.
        </p>
        <div className={`reveal reveal-d2 ${africa.visible ? 'in' : ''}`}>
          <Link href="/app" className="btn-main">⚡ Start Applying Now</Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="foot">
        <span className="foot-l">AutoApply — Amazon Nova Hackathon 2026 · #AmazonNova</span>
        <div className="foot-r">
          <a href="https://github.com/chibuchi001/AutoApply" target="_blank" rel="noopener noreferrer">GitHub</a>
          <Link href="/app">Launch App</Link>
        </div>
      </footer>
    </div>
  );
}