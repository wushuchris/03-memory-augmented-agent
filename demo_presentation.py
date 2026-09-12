from html import escape
from typing import Iterable

from schemas import MemoryEvent


APP_CSS = """
:root,
.gradio-container {
    color-scheme: light !important;
    --body-background-fill: #f8fafc !important;
    --body-text-color: #0f172a !important;
    --block-background-fill: #ffffff !important;
    --block-label-text-color: #334155 !important;
    --input-background-fill: #ffffff !important;
    --input-border-color: #cbd5e1 !important;
    --input-placeholder-color: #94a3b8 !important;
    --button-primary-background-fill: #4f46e5 !important;
    --button-primary-background-fill-hover: #4338ca !important;
    --button-primary-text-color: #ffffff !important;
}

.gradio-container {
    max-width: 1080px !important;
    margin: 0 auto !important;
    padding: 26px 24px 48px !important;
    background: #f8fafc !important;
    color: #0f172a !important;
}

.gradio-container textarea,
.gradio-container input[type="text"],
.gradio-container input[type="number"] {
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border-color: #cbd5e1 !important;
    box-shadow: none !important;
}
.gradio-container textarea::placeholder,
.gradio-container input::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
    opacity: 1 !important;
}
.gradio-container label,
.gradio-container label span,
.gradio-container .label-wrap,
.gradio-container .label-wrap span {
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    opacity: 1 !important;
}

.hero-card,
.privacy-card,
.concept-card,
.activity-card,
.boundary-box,
.business-story,
.business-outcome,
.evidence-panel {
    border: 1px solid #dbe3ee !important;
    background: #ffffff !important;
    color: #0f172a !important;
    box-shadow: 0 8px 28px rgba(15, 23, 42, 0.06) !important;
}

.hero-card {
    padding: 30px;
    margin-bottom: 18px;
    border-radius: 18px;
}
.hero-eyebrow {
    font-size: .82rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #4338ca !important;
    -webkit-text-fill-color: #4338ca !important;
}
.hero-card h1 {
    font-size: 2.35rem;
    line-height: 1.1;
    margin: 8px 0 14px;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}
.hero-card p {
    font-size: 1.06rem;
    line-height: 1.65;
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    margin: 0;
}
.pattern-line {
    margin-top: 18px;
    padding: 13px 15px;
    border-radius: 12px;
    background: #eef2ff !important;
    color: #312e81 !important;
    -webkit-text-fill-color: #312e81 !important;
    font-weight: 800;
}

.privacy-card {
    padding: 18px 20px;
    margin: 14px 0 20px;
    border-radius: 18px;
    background: #f8fafc !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    line-height: 1.55;
}
.privacy-card strong {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

.business-story {
    border-radius: 18px;
    padding: 24px;
    margin: 4px 0 20px;
}
.business-kicker {
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
    text-transform: uppercase;
    letter-spacing: .07em;
    font-size: .78rem;
    font-weight: 850;
    margin-bottom: 7px;
}
.business-story h2 {
    margin: 0 0 10px;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-size: 1.38rem;
}
.business-story > p {
    margin: 0;
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    line-height: 1.65;
}
.business-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
    margin-top: 18px;
}
.business-mini {
    border: 1px solid #e2e8f0;
    border-radius: 13px;
    background: #f8fafc;
    padding: 14px 15px;
}
.business-mini strong {
    display: block;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    margin-bottom: 4px;
}
.business-mini span {
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    line-height: 1.5;
}

.concept-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    margin: 16px 0 22px;
}
.concept-card {
    padding: 18px 20px;
    border-radius: 18px;
}
.concept-card h3,
.boundary-box h3 {
    margin: 0 0 7px;
    font-size: 1.02rem;
    font-weight: 800;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}
.concept-card p,
.boundary-box p {
    margin: 0;
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    line-height: 1.55;
}
.concept-card strong {
    color: #312e81 !important;
    -webkit-text-fill-color: #312e81 !important;
}

.memory-boundary {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    margin: 14px 0 24px;
}
.boundary-box {
    border-radius: 16px;
    padding: 18px 20px;
}

.section-title h2,
.section-title {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

#memory-query {
    border: 1px solid #dbe3ee !important;
    border-radius: 16px !important;
    background: #ffffff !important;
    padding: 12px 14px !important;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04) !important;
}
#memory-query > div,
#memory-query .wrap,
#memory-query .form,
#memory-query .input-container,
#memory-query textarea {
    background: #ffffff !important;
}
#memory-query textarea {
    min-height: 92px !important;
    border: 0 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    font-size: 1rem !important;
    line-height: 1.5 !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    box-shadow: inset 0 0 0 1px #e2e8f0 !important;
}
.control-row {
    gap: 14px !important;
    margin-top: 12px !important;
}
#memory-top-k,
#memory-write-permission {
    background: #ffffff !important;
    border: 1px solid #dbe3ee !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}
#memory-top-k input[type="range"],
#memory-write-permission input[type="checkbox"] {
    accent-color: #4f46e5 !important;
}

.example-actions,
.primary-actions {
    gap: 12px !important;
}
.example-button,
.secondary-action,
.primary-action {
    border-radius: 12px !important;
    min-height: 46px !important;
    font-weight: 750 !important;
    box-shadow: none !important;
}
.example-button,
.secondary-action {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
}
.example-button:hover,
.secondary-action:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
}
.primary-action,
#run-memory-request {
    background: #4f46e5 !important;
    border: 1px solid #4f46e5 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
.primary-action:hover,
#run-memory-request:hover {
    background: #4338ca !important;
    border-color: #4338ca !important;
}

.activity-card {
    padding: 20px;
    min-height: 118px;
    border-radius: 18px;
    margin-top: 8px;
}
.activity-header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
    margin-bottom: 12px;
}
.activity-title {
    font-weight: 800;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}
.activity-badge {
    border-radius: 999px;
    padding: 4px 10px;
    font-size: .76rem;
    font-weight: 800;
    background: #e2e8f0 !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
}
.activity-badge.running {
    background: #e0e7ff !important;
    color: #3730a3 !important;
    -webkit-text-fill-color: #3730a3 !important;
}
.activity-badge.complete {
    background: #dcfce7 !important;
    color: #166534 !important;
    -webkit-text-fill-color: #166534 !important;
}
.event-row {
    border-left: 3px solid #cbd5e1;
    padding: 7px 0 7px 12px;
    margin: 7px 0;
}
.event-label {
    font-weight: 800;
    color: #1e293b !important;
    -webkit-text-fill-color: #1e293b !important;
}
.event-message {
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    margin-top: 2px;
}

.answer-panel,
.business-outcome,
.evidence-panel {
    border-radius: 18px !important;
    padding: 20px 22px !important;
    min-height: 96px !important;
}
.answer-panel,
.answer-panel p,
.answer-panel li,
.answer-panel strong,
.business-outcome,
.business-outcome p,
.business-outcome li,
.business-outcome strong {
    color: #1e293b !important;
    -webkit-text-fill-color: #1e293b !important;
}
.answer-panel p,
.business-outcome p,
.business-outcome li {
    line-height: 1.62 !important;
}

.outcome-header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
    margin-bottom: 10px;
}
.outcome-title {
    font-weight: 850;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}
.outcome-badge {
    border-radius: 999px;
    padding: 4px 10px;
    background: #eef2ff;
    color: #3730a3 !important;
    -webkit-text-fill-color: #3730a3 !important;
    font-size: .76rem;
    font-weight: 850;
}
.outcome-list {
    margin: 8px 0 0 20px;
    padding: 0;
}
.outcome-policy {
    margin-top: 14px;
    border-top: 1px solid #e2e8f0;
    padding-top: 12px;
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
}

.evidence-panel {
    padding: 0 !important;
    overflow: hidden;
}
.evidence-empty {
    padding: 18px 20px;
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
}
.evidence-table-wrap {
    overflow-x: auto;
}
.evidence-table {
    width: 100%;
    border-collapse: collapse;
    background: #ffffff;
    color: #1e293b;
    font-size: .9rem;
}
.evidence-table th {
    text-align: left;
    padding: 11px 12px;
    background: #f1f5f9;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    border-bottom: 1px solid #dbe3ee;
    font-weight: 800;
    white-space: nowrap;
}
.evidence-table td {
    vertical-align: top;
    padding: 11px 12px;
    background: #ffffff;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    border-bottom: 1px solid #edf2f7;
    line-height: 1.45;
}
.evidence-table tr:last-child td {
    border-bottom: 0;
}

#compressed-context,
#compressed-context > div,
#compressed-context .wrap,
#compressed-context .form,
#compressed-context .input-container,
#compressed-context textarea {
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

@media (min-width: 760px) {
    .business-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 860px) {
    .memory-boundary { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 700px) {
    .gradio-container { padding: 18px 14px 36px !important; }
    .hero-card { padding: 22px; }
    .hero-card h1 { font-size: 1.9rem; }
}

footer { display: none !important; }
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


BUSINESS_STORY_HTML = """
<div class="business-story">
  <div class="business-kicker">The business problem</div>
  <h2>Harborlight is preparing an enterprise customer pilot across several teams.</h2>
  <p>
    Support, Operations, and Engineering have already made decisions about launch prerequisites,
    ownership, timing, and readiness reviews. Those decisions were made across different meetings.
    The operational risk is losing an important decision during a handoff—or forcing every new
    conversation to reload the entire project history just to stay consistent.
  </p>
  <div class="business-grid">
    <div class="business-mini"><strong>Business risk</strong><span>Missed prerequisites, repeated decisions, and inconsistent customer handoffs.</span></div>
    <div class="business-mini"><strong>Agent contribution</strong><span>Recall only the prior project context that matters for the request being handled now.</span></div>
    <div class="business-mini"><strong>Application authority</strong><span>Decide what becomes memory, what is skipped, and what sensitive content is blocked.</span></div>
  </div>
</div>
"""


CONCEPT_HTML = """
<div class="concept-grid">
  <div class="concept-card"><h3>1 · Recall only what is relevant</h3><p>Semantic similarity ranks prior project memories instead of loading the entire history into every turn.</p></div>
  <div class="concept-card"><h3>2 · Separate stable facts from prior events</h3><p>Semantic memory represents durable context; episodic memory represents decisions and events that happened over time.</p></div>
  <div class="concept-card"><h3>3 · Make memory writes an application decision</h3><p>The write policy returns <strong>SAVE / SKIP / BLOCK</strong> before any new information becomes durable memory.</p></div>
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
