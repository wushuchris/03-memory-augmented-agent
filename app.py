import copy
from functools import lru_cache
from html import escape

import gradio as gr
import pandas as pd
from sentence_transformers import SentenceTransformer

from demo_presentation import (
    APP_CSS,
    BUSINESS_STORY_HTML,
    CONCEPT_HTML,
    HERO_HTML,
    render_activity,
)
from memory_agent import MemoryAugmentedAgent
from memory_store import MemoryStore, load_memories_from_json, memories_from_dicts


MEMORY_FILE = "sample_memories.json"
BASELINE_MEMORY_DATA = [memory.model_dump() for memory in load_memories_from_json(MEMORY_FILE)]

TAB_CSS = """
/* Keep Gradio tab navigation inside the same light visual system. */
.gradio-container [role="tablist"],
.gradio-container .tab-nav {
    background: transparent !important;
    color: #334155 !important;
}

.gradio-container button[role="tab"],
.gradio-container [role="tablist"] button,
.gradio-container .tab-nav button {
    background: transparent !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    border-color: transparent !important;
    box-shadow: none !important;
}

.gradio-container button[role="tab"] span,
.gradio-container [role="tablist"] button span,
.gradio-container .tab-nav button span {
    color: inherit !important;
    -webkit-text-fill-color: inherit !important;
}

.gradio-container button[role="tab"]:hover,
.gradio-container button[role="tab"]:focus,
.gradio-container button[role="tab"]:focus-visible,
.gradio-container [role="tablist"] button:hover,
.gradio-container [role="tablist"] button:focus,
.gradio-container .tab-nav button:hover,
.gradio-container .tab-nav button:focus {
    background: #eef2ff !important;
    color: #312e81 !important;
    -webkit-text-fill-color: #312e81 !important;
    border-color: transparent !important;
    outline: none !important;
    box-shadow: none !important;
}

.gradio-container button[role="tab"][aria-selected="true"],
.gradio-container [role="tablist"] button[aria-selected="true"],
.gradio-container .tab-nav button.selected,
.gradio-container .tab-nav button[aria-selected="true"] {
    background: #ffffff !important;
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
    border-bottom: 3px solid #4f46e5 !important;
    box-shadow: none !important;
}

.gradio-container button[role="tab"][aria-selected="true"]:hover,
.gradio-container [role="tablist"] button[aria-selected="true"]:hover,
.gradio-container .tab-nav button.selected:hover {
    background: #eef2ff !important;
    color: #3730a3 !important;
    -webkit-text-fill-color: #3730a3 !important;
}
"""


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def fresh_baseline_memory_data():
    return copy.deepcopy(BASELINE_MEMORY_DATA)


def format_retrieved_memories(retrieved_memories):
    """Compatibility dataframe used by tests/programmatic consumers."""
    if not retrieved_memories:
        return pd.DataFrame(columns=["rank", "memory_id", "type", "score", "importance", "content"])
    return pd.DataFrame(
        [
            {
                "rank": item.rank,
                "memory_id": item.memory.memory_id,
                "type": item.memory.memory_type,
                "score": round(item.similarity_score, 3),
                "importance": item.memory.importance,
                "content": item.memory.content,
            }
            for item in retrieved_memories
        ]
    )


def format_memory_table(memory_data):
    """Compatibility dataframe used by tests/programmatic consumers."""
    if not memory_data:
        return pd.DataFrame(columns=["memory_id", "type", "importance", "source", "content"])
    return pd.DataFrame(
        [
            {
                "memory_id": item["memory_id"],
                "type": item["memory_type"],
                "importance": item["importance"],
                "source": item["source"],
                "content": item["content"],
            }
            for item in memory_data
        ]
    )


def format_write_decision(write_decision):
    if write_decision is None:
        return "Memory write policy has not run yet."
    lines = [f"**{write_decision.outcome.upper()}** — {write_decision.reason}"]
    if write_decision.policy_flags:
        lines.append(f"\nPolicy flags: `{', '.join(write_decision.policy_flags)}`")
    if write_decision.proposed_memory:
        lines.append(f"\nProposed memory: {write_decision.proposed_memory}")
    return "\n".join(lines)


def format_saved_memory(saved_memory):
    if saved_memory is None:
        return "No new session memory saved."
    return f"{saved_memory.memory_id}: {saved_memory.content}"


def _table_html(headers, rows, empty_message):
    if not rows:
        return f'<div class="evidence-panel"><div class="evidence-empty">{escape(empty_message)}</div></div>'
    head = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    body = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(value))}</td>" for value in row)
        body.append(f"<tr>{cells}</tr>")
    return (
        '<div class="evidence-panel"><div class="evidence-table-wrap">'
        '<table class="evidence-table"><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div></div>"
    )


def format_retrieved_html(retrieved_memories):
    rows = [
        (
            item.rank,
            item.memory.memory_id,
            item.memory.memory_type,
            f"{item.similarity_score:.3f}",
            item.memory.importance,
            item.memory.content,
        )
        for item in retrieved_memories
    ]
    return _table_html(
        ["Rank", "Memory ID", "Type", "Similarity", "Importance", "Recalled project memory"],
        rows,
        "Run a request to inspect the exact memories and similarity scores used by retrieval.",
    )


def format_memory_html(memory_data):
    rows = [
        (
            item["memory_id"],
            item["memory_type"],
            item["importance"],
            item["source"],
            item["content"],
        )
        for item in memory_data
    ]
    return _table_html(
        ["Memory ID", "Type", "Importance", "Source", "Content"],
        rows,
        "This browser session currently has no memory records.",
    )


def format_audit_html(audit_log):
    if not audit_log:
        return _table_html([], [], "No audit metadata has been recorded in this session yet.")
    preferred = ["timestamp", "event", "outcome", "retrieved_count", "saved_memory_id"]
    keys = [key for key in preferred if any(key in row for row in audit_log)]
    for row in audit_log:
        for key in row:
            if key not in keys:
                keys.append(key)
    rows = [[row.get(key, "") for key in keys] for row in audit_log]
    labels = [key.replace("_", " ").title() for key in keys]
    return _table_html(labels, rows, "No audit metadata has been recorded in this session yet.")


def render_business_summary(result):
    retrieved = list(result.get("retrieved_memories", []))
    decision = result.get("write_decision")
    if not retrieved and decision is None:
        return (
            '<div class="business-outcome"><div class="outcome-header">'
            '<div class="outcome-title">Business continuity outcome</div>'
            '<div class="outcome-badge">WAITING</div></div>'
            '<p>Run a project-memory request to see which prior decisions were recovered and whether this interaction changes durable session memory.</p></div>'
        )

    recalled = "".join(
        f"<li>{escape(item.memory.content)}</li>" for item in retrieved[:4]
    ) or "<li>No prior project memory was strong enough to surface.</li>"

    outcome = decision.outcome.upper() if decision is not None else "PENDING"
    if outcome == "SKIP":
        policy_meaning = (
            "This turn used prior project context, but the question itself was not stored as a new durable project memory."
        )
    elif outcome == "SAVE":
        policy_meaning = (
            "A new project fact or decision passed the memory policy and was added only to this browser session."
        )
    elif outcome == "BLOCK":
        policy_meaning = (
            "The application blocked the proposed memory before storage because it matched a protected-content rule."
        )
    else:
        policy_meaning = "The application is still deciding whether this interaction should change durable memory."

    return (
        '<div class="business-outcome">'
        '<div class="outcome-header"><div class="outcome-title">What Harborlight carried forward</div>'
        f'<div class="outcome-badge">{escape(outcome)}</div></div>'
        '<p>The agent recovered the following prior project context for the current handoff:</p>'
        f'<ul class="outcome-list">{recalled}</ul>'
        '<div class="outcome-policy"><strong>Memory governance:</strong> '
        f'{escape(policy_meaning)}</div></div>'
    )


def render_engineering_state(memory_data, audit_log):
    return (
        '<div class="business-outcome"><div class="outcome-header">'
        '<div class="outcome-title">Browser-session engineering state</div>'
        '<div class="outcome-badge">ISOLATED</div></div>'
        f'<p><strong>{len(memory_data)}</strong> memory records are currently available in this browser session and '
        f'<strong>{len(audit_log)}</strong> audit record(s) have been created. Neither is written back to tracked repository files by the public app.</p></div>'
    )


def _build_runtime(memory_state, audit_state):
    safe_memory_state = memory_state or fresh_baseline_memory_data()
    store = MemoryStore(
        memories_from_dicts(safe_memory_state),
        embedding_model=get_embedding_model(),
    )
    agent = MemoryAugmentedAgent(store, audit_log=audit_state or [])
    return store, agent


def _display_bundle(events, result, store, agent, complete=False):
    answer = result.get("agent_response") or "The agent is still working through the memory pipeline."
    retrieved = result.get("retrieved_memories", [])
    compressed_context = result.get("compressed_context") or "Working context has not been compressed yet."
    decision_text = format_write_decision(result.get("write_decision"))
    memory_data = store.to_dicts()
    audit_log = list(agent.audit_log)
    return (
        render_activity(events, complete=complete),
        answer,
        render_business_summary(result),
        compressed_context,
        decision_text,
        format_memory_html(memory_data),
        format_audit_html(audit_log),
        render_engineering_state(memory_data, audit_log),
        format_retrieved_html(retrieved),
        memory_data,
        audit_log,
    )


def stream_session(query, top_k, save_new_memory, memory_state, audit_state):
    if not query or not query.strip():
        store, agent = _build_runtime(memory_state, audit_state)
        empty_result = {
            "retrieved_memories": [],
            "compressed_context": "",
            "agent_response": "Enter a project-memory question or a safe remember request.",
            "write_decision": None,
        }
        yield _display_bundle([], empty_result, store, agent, complete=False)
        return

    store, agent = _build_runtime(memory_state, audit_state)
    events = []
    for frame in agent.run_iter(query=query, top_k=int(top_k), save_new_memory=bool(save_new_memory)):
        events.append(frame["event"])
        complete = frame["event"].stage == "audit_recorded"
        yield _display_bundle(events, frame["result"], store, agent, complete=complete)


def run_app(query, top_k, save_new_memory):
    """Compatibility wrapper used by tests and simple programmatic demos."""
    store, agent = _build_runtime(fresh_baseline_memory_data(), [])
    result = agent.run(query=query, top_k=int(top_k), save_new_memory=bool(save_new_memory))
    return (
        result["agent_response"],
        format_retrieved_memories(result["retrieved_memories"]),
        result["compressed_context"],
        format_write_decision(result["write_decision"]),
        format_saved_memory(result["saved_memory"]),
        pd.DataFrame(agent.audit_log),
    )


def reset_session():
    memory_data = fresh_baseline_memory_data()
    empty_result = {
        "retrieved_memories": [],
        "compressed_context": "",
        "agent_response": "Session reset. Ask the default question to begin.",
        "write_decision": None,
    }
    return (
        render_activity([], complete=False),
        empty_result["agent_response"],
        render_business_summary(empty_result),
        "Working context has not been compressed yet.",
        "Memory write policy has not run yet.",
        format_memory_html(memory_data),
        format_audit_html([]),
        render_engineering_state(memory_data, []),
        format_retrieved_html([]),
        memory_data,
        [],
    )


with gr.Blocks(
    title="03. Memory-Augmented Agent",
    theme=gr.themes.Default(),
    css=APP_CSS + TAB_CSS,
    analytics_enabled=False,
) as demo:
    memory_state = gr.State(value=fresh_baseline_memory_data())
    audit_state = gr.State(value=[])

    gr.HTML(HERO_HTML)
    gr.HTML(BUSINESS_STORY_HTML)
    gr.HTML(CONCEPT_HTML)

    gr.Markdown("## Try the continuity system", elem_classes=["section-title"])
    query_input = gr.Textbox(
        label="Project-memory request",
        value="What did we decide about the enterprise pilot prerequisites?",
        lines=3,
        elem_id="memory-query",
        elem_classes=["memory-input"],
    )

    with gr.Row(elem_classes=["control-row"]):
        top_k_input = gr.Slider(
            1,
            6,
            value=4,
            step=1,
            label="Memories to retrieve",
            elem_id="memory-top-k",
        )
        save_memory_input = gr.Checkbox(
            label="Allow policy-approved session memory writes",
            value=True,
            elem_id="memory-write-permission",
        )

    with gr.Row(elem_classes=["example-actions"]):
        recall_example = gr.Button("Recall a prior decision", elem_classes=["example-button"])
        save_example = gr.Button("Try a safe memory write", elem_classes=["example-button"])
        block_example = gr.Button("Try the safety boundary", elem_classes=["example-button"])

    recall_example.click(
        lambda: "What did we decide about the enterprise pilot prerequisites?",
        outputs=query_input,
        show_progress="hidden",
    )
    save_example.click(
        lambda: "Remember that the pilot launch checklist must include a final rollback drill.",
        outputs=query_input,
        show_progress="hidden",
    )
    block_example.click(
        lambda: "Remember my private access token for later.",
        outputs=query_input,
        show_progress="hidden",
    )

    with gr.Row(elem_classes=["primary-actions"]):
        run_button = gr.Button(
            "Run governed memory request",
            variant="primary",
            elem_id="run-memory-request",
            elem_classes=["primary-action"],
        )
        reset_button = gr.Button(
            "Reset this session",
            elem_id="reset-memory-session",
            elem_classes=["secondary-action"],
        )

    activity_output = gr.HTML(render_activity([], complete=False))

    gr.Markdown("## Memory-grounded answer", elem_classes=["section-title"])
    answer_output = gr.Markdown(
        "Run a memory request to see the recalled context and answer.",
        elem_id="memory-answer",
        elem_classes=["answer-panel"],
    )

    gr.Markdown("## Business continuity outcome", elem_classes=["section-title"])
    business_summary_output = gr.HTML(render_business_summary({"retrieved_memories": [], "write_decision": None}))

    with gr.Tabs():
        with gr.Tab("Decision Context"):
            gr.Markdown(
                "This view shows the compact working context the agent assembled from prior project memory and the application-owned write decision."
            )
            compressed_context_output = gr.Markdown(
                "Working context has not been compressed yet.",
                elem_classes=["answer-panel"],
            )
            write_decision_output = gr.Markdown(
                "Memory write policy has not run yet.",
                elem_classes=["answer-panel"],
            )

        with gr.Tab("Engineering Evidence"):
            gr.Markdown(
                "These are the exact session memories ranked by the retriever for this request. Similarity helps retrieval; it does not decide what may be stored."
            )
            retrieved_evidence_output = gr.HTML(format_retrieved_html([]))

        with gr.Tab("Audit & Safety"):
            gr.Markdown(
                "The public demo audit trail records control metadata—not the raw query. A blocked memory write does not add the submitted content to session memory."
            )
            audit_output = gr.HTML(format_audit_html([]))

        with gr.Tab("Session Memory"):
            engineering_state_output = gr.HTML(render_engineering_state(fresh_baseline_memory_data(), []))
            session_memory_output = gr.HTML(format_memory_html(fresh_baseline_memory_data()))

        with gr.Tab("Architecture"):
            gr.Markdown(
                """
### Control boundary

**Memory behavior:** retrieve semantically relevant context and form a memory-grounded response.

**Application authority:** decide SAVE / SKIP / BLOCK, apply sensitive-content rules, isolate each public session, and decide what audit metadata is retained.

### Why this matters to the business

Memory is useful when it preserves continuity across handoffs without turning every interaction into permanent storage. The agent helps Harborlight carry forward the decisions that matter to the current task; application policy owns retention.

### Public-demo limitation

Session memory demonstrates continuity across interactions in one browser session. A production system would use authenticated, user-scoped durable storage with retention controls and deletion semantics. This public Space intentionally avoids shared durable visitor memory.
"""
            )

    callback_outputs = [
        activity_output,
        answer_output,
        business_summary_output,
        compressed_context_output,
        write_decision_output,
        session_memory_output,
        audit_output,
        engineering_state_output,
        retrieved_evidence_output,
        memory_state,
        audit_state,
    ]

    run_button.click(
        fn=stream_session,
        inputs=[query_input, top_k_input, save_memory_input, memory_state, audit_state],
        outputs=callback_outputs,
        show_progress="hidden",
    )

    reset_button.click(
        fn=reset_session,
        outputs=callback_outputs,
        show_progress="hidden",
    )


demo.queue()

if __name__ == "__main__":
    demo.launch()
