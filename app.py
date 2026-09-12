import copy
from functools import lru_cache

import gradio as gr
import pandas as pd
from sentence_transformers import SentenceTransformer

from demo_presentation import APP_CSS, CONCEPT_HTML, HERO_HTML, render_activity
from memory_agent import MemoryAugmentedAgent
from memory_store import MemoryStore, load_memories_from_json, memories_from_dicts


MEMORY_FILE = "sample_memories.json"
BASELINE_MEMORY_DATA = [memory.model_dump() for memory in load_memories_from_json(MEMORY_FILE)]


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def fresh_baseline_memory_data():
    return copy.deepcopy(BASELINE_MEMORY_DATA)


def format_retrieved_memories(retrieved_memories):
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
    lines = [
        f"**{write_decision.outcome.upper()}** — {write_decision.reason}",
    ]
    if write_decision.policy_flags:
        lines.append(f"\nPolicy flags: `{', '.join(write_decision.policy_flags)}`")
    if write_decision.proposed_memory:
        lines.append(f"\nProposed memory: {write_decision.proposed_memory}")
    return "\n".join(lines)


def format_saved_memory(saved_memory):
    if saved_memory is None:
        return "No new session memory saved."
    return f"{saved_memory.memory_id}: {saved_memory.content}"


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
    retrieved_df = format_retrieved_memories(result.get("retrieved_memories", []))
    compressed_context = result.get("compressed_context") or "Working context has not been compressed yet."
    decision_text = format_write_decision(result.get("write_decision"))
    memory_data = store.to_dicts()
    audit_df = pd.DataFrame(agent.audit_log)
    return (
        render_activity(events, complete=complete),
        answer,
        retrieved_df,
        compressed_context,
        decision_text,
        format_memory_table(memory_data),
        audit_df,
        memory_data,
        memory_data,
        list(agent.audit_log),
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
    """Compatibility wrapper used by tests and simple programmatic demos.

    It intentionally starts from a fresh synthetic baseline and never writes to tracked files.
    """
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
    return (
        render_activity([], complete=False),
        "Session reset. Ask the default question to begin.",
        format_retrieved_memories([]),
        "Working context has not been compressed yet.",
        "Memory write policy has not run yet.",
        format_memory_table(memory_data),
        pd.DataFrame(),
        memory_data,
        memory_data,
        [],
    )


with gr.Blocks(
    title="03. Memory-Augmented Agent",
    theme=gr.themes.Default(),
    css=APP_CSS,
    analytics_enabled=False,
) as demo:
    memory_state = gr.State(value=fresh_baseline_memory_data())
    audit_state = gr.State(value=[])

    gr.HTML(HERO_HTML)
    gr.HTML(CONCEPT_HTML)

    gr.Markdown("## Try the continuity system")
    query_input = gr.Textbox(
        label="Project-memory request",
        value="What did we decide about the enterprise pilot prerequisites?",
        lines=3,
    )

    with gr.Row():
        top_k_input = gr.Slider(1, 6, value=4, step=1, label="Memories to retrieve")
        save_memory_input = gr.Checkbox(
            label="Allow policy-approved session memory writes",
            value=True,
        )

    with gr.Row():
        recall_example = gr.Button("Recall a prior decision")
        save_example = gr.Button("Try a safe memory write")
        block_example = gr.Button("Try the safety boundary")

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

    with gr.Row():
        run_button = gr.Button("Run governed memory request", variant="primary")
        reset_button = gr.Button("Reset this session")

    activity_output = gr.HTML(render_activity([], complete=False))

    gr.Markdown("## Memory-grounded answer")
    answer_output = gr.Textbox(label="Answer", lines=8, interactive=False)

    with gr.Tabs():
        with gr.Tab("Memory Inspection"):
            retrieved_output = gr.Dataframe(label="Retrieved memories", interactive=False)
            compressed_context_output = gr.Textbox(label="Compressed working context", lines=10, interactive=False)
            write_decision_output = gr.Markdown("Memory write policy has not run yet.")
            session_memory_output = gr.Dataframe(
                value=format_memory_table(fresh_baseline_memory_data()),
                label="This session's memory store",
                interactive=False,
            )

        with gr.Tab("Audit & Safety"):
            gr.Markdown(
                "The public demo audit trail records control metadata—not the raw query. "
                "A blocked memory write does not add the submitted content to session memory."
            )
            audit_output = gr.Dataframe(label="Session audit metadata", interactive=False)

        with gr.Tab("Engineering State"):
            gr.Markdown(
                "This JSON is the current browser-session memory state. It starts from synthetic baseline data "
                "and is never written back into the GitHub repository by the app."
            )
            state_json_output = gr.JSON(value=fresh_baseline_memory_data(), label="Session memory JSON")

        with gr.Tab("Architecture"):
            gr.Markdown(
                """
### Control boundary

**Model-like memory behavior:** retrieve semantically relevant context and form a memory-grounded response.

**Application authority:** decide SAVE / SKIP / BLOCK, apply sensitive-content rules, isolate each public session, and decide what audit metadata is retained.

### Public-demo limitation

Session memory demonstrates continuity across interactions in one browser session. A production system would use authenticated, user-scoped durable storage with retention controls and deletion semantics. This public Space intentionally avoids shared durable visitor memory.
"""
            )

    callback_outputs = [
        activity_output,
        answer_output,
        retrieved_output,
        compressed_context_output,
        write_decision_output,
        session_memory_output,
        audit_output,
        state_json_output,
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
