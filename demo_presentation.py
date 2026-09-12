from html import escape
from typing import Iterable

from schemas import MemoryEvent


APP_CSS = """
.gradio-container {
    max-width: 1080px !important;
    margin: 0 auto !important;
    padding: 26px 24px 48px !important;
}
.hero-card, .privacy-card, .concept-card, .activity-card {
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    background: #ffffff;
    box-shadow: 0 8px 28px rgba(15, 23, 42, 0.06);
}
.hero-card { padding: 30px; margin-bottom: 18px; }
.hero-eyebrow { font-size: .82rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #4f46e5; }
.hero-card h1 { font-size: 2.35rem; line-height: 1.1; margin: 8px 0 12px; }
.hero-card p { font-size: 1.06rem; line-height: 1.65; color: #475569; margin: 0; }
.pattern-line { margin-top: 18px; padding: 13px 15px; border-radius: 12px; background: #eef2ff; color: #312e81; font-weight: 700; }
.privacy-card { padding: 18px 20px; margin: 14px 0 20px; background: #f8fafc; }
.privacy-card strong { color: #0f172a; }
.concept-grid { display: grid; grid-template-columns: 1fr; gap: 12px; margin: 16px 0 22px; }
.concept-card { padding: 17px 19px; }
.concept-card h3 { margin: 0 0 6px; font-size: 1rem; }
.concept-card p { margin: 0; color: #475569; line-height: 1.5; }
.activity-card { padding: 18px; min-height: 120px; }
.activity-header { display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:12px; }
.activity-title { font-weight: 800; color: #0f172a; }
.activity-badge { border-radius:999px; padding:4px 10px; font-size:.76rem; font-weight:800; background:#e2e8f0; color:#334155; }
.activity-badge.running { background:#e0e7ff; color:#3730a3; }
.activity-badge.complete { background:#dcfce7; color:#166534; }
.event-row { border-left: 3px solid #cbd5e1; padding: 7px 0 7px 12px; margin: 7px 0; }
.event-label { font-weight: 800; color:#1e293b; }
.event-message { color:#475569; margin-top:2px; }
.memory-boundary { display:grid; grid-template-columns:1fr; gap:10px; margin:14px 0; }
.boundary-box { border:1px solid #e2e8f0; border-radius:14px; padding:15px 17px; background:#fff; }
.boundary-box h3 { margin:0 0 6px; font-size:1rem; }
.boundary-box p { margin:0; line-height:1.5; color:#475569; }
@media (min-width: 860px) {
  .memory-boundary { grid-template-columns: 1fr 1fr; }
}
footer { display:none !important; }
"""


HERO_HTML = """
<div class="hero-card">
  <div class="hero-eyebrow">03 · Memory-Augmented Agent</div>
  <h1>How can an AI remember useful project context without storing everything forever?</h1>
  <p>
    This demo follows a fictional Harborlight Support Portal project across multiple turns.
    The agent retrieves relevant memories, compresses working context, answers from what it recalled,
    and then lets application code decide whether the new interaction should be saved, skipped, or blocked.
  </p>
  <div class="pattern-line">Retrieve → Compress → Answer → Evaluate memory write → Save / Skip / Block</div>
</div>
<div class="privacy-card">
  <strong>Public-demo privacy boundary.</strong> Seed data is fully synthetic. Visitor-created memories and audit metadata live only in that browser session and are never written back to tracked repository files. The audit trail does not store the raw query. Do not enter real secrets or sensitive information.
</div>
"""


CONCEPT_HTML = """
<div class="concept-grid">
  <div class="concept-card"><h3>1 · Recall only what is relevant</h3><p>Semantic similarity ranks prior project memories instead of loading the entire history into every turn.</p></div>
  <div class="concept-card"><h3>2 · Separate stable facts from prior events</h3><p>Semantic memory represents durable context; episodic memory represents decisions and events that happened over time.</p></div>
  <div class="concept-card"><h3>3 · Make memory writes an application decision</h3><p>The write policy returns <strong>SAVE / SKIP / BLOCK</strong> before any new information becomes durable memory. Questions are usually skipped, durable project decisions may be saved, and sensitive-looking content is blocked before storage.</p></div>
  <div class="concept-card"><h3>4 · Keep the public demo isolated</h3><p>Each session starts from the same synthetic baseline. No visitor can mutate another visitor's tracked memory or committed audit log.</p></div>
</div>
<div class="memory-boundary">
  <div class="boundary-box"><h3>The agent can</h3><p>Retrieve session memories, compress context, expose what it recalled, and propose a memory write.</p></div>
  <div class="boundary-box"><h3>Application code controls</h3><p>What counts as durable memory, which sensitive patterns are blocked, whether a write occurs, and what audit metadata is retained.</p></div>
</div>
"""


_STAGE_LABELS = {
    "query_received": "Request received",
    "memory_retrieved": "Relevant memories retrieved",
    "context_compressed": "Working context compressed",
    "write_policy_evaluated": "Memory policy evaluated",
    "memory_saved": "Memory saved to this session",
    "memory_skipped": "Memory write skipped",
    "memory_blocked": "Memory write blocked",
    "response_ready": "Memory-grounded answer ready",
    "audit_recorded": "Audit metadata recorded",
}


def render_activity(events: Iterable[MemoryEvent], complete: bool = False) -> str:
    events = list(events)
    if not events:
        return (
            '<div class="activity-card"><div class="activity-header">'
            '<div class="activity-title">Live Memory Activity</div>'
            '<div class="activity-badge">IDLE</div></div>'
            '<div class="event-message">Run the default question to watch the real memory pipeline.</div></div>'
        )

    rows = []
    for event in events:
        label = _STAGE_LABELS.get(event.stage, event.stage.replace("_", " ").title())
        rows.append(
            '<div class="event-row">'
            f'<div class="event-label">{escape(label)}</div>'
            f'<div class="event-message">{escape(event.message)}</div>'
            '</div>'
        )
    badge_class = "complete" if complete else "running"
    badge_text = "COMPLETE" if complete else "RUNNING"
    return (
        '<div class="activity-card"><div class="activity-header">'
        '<div class="activity-title">Live Memory Activity</div>'
        f'<div class="activity-badge {badge_class}">{badge_text}</div></div>'
        + "".join(rows)
        + "</div>"
    )
