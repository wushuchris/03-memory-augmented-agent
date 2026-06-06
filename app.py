
import pandas as pd
import gradio as gr

from memory_store import MemoryStore, load_memories_from_json
from memory_agent import MemoryAugmentedAgent
from schemas import Memory, RetrievedMemory, MemoryWriteDecision


MEMORY_FILE = "sample_memories.json"
AUDIT_LOG_FILE = "memory_agent_audit_log.csv"


memories = load_memories_from_json(MEMORY_FILE)
memory_store = MemoryStore(memories)
agent = MemoryAugmentedAgent(memory_store)


def format_retrieved_memories(retrieved_memories):
    if not retrieved_memories:
        return "No memories retrieved."

    lines = []

    for item in retrieved_memories:
        memory = item.memory
        lines.append(f"### {memory.memory_id} | {memory.memory_type.upper()} | Score: {item.similarity_score:.3f}")
        lines.append(f"**Content:** {memory.content}")
        lines.append(f"**Tags:** {', '.join(memory.tags)}")
        lines.append(f"**Importance:** {memory.importance}")
        lines.append("---")

    return "\n".join(lines)


def format_write_decision(write_decision):
    lines = [
        f"**Should save:** {write_decision.should_save}",
        f"**Reason:** {write_decision.reason}"
    ]

    if write_decision.memory_type:
        lines.append(f"**Memory type:** {write_decision.memory_type}")

    if write_decision.importance:
        lines.append(f"**Importance:** {write_decision.importance}")

    if write_decision.proposed_memory:
        lines.append(f"**Proposed memory:** {write_decision.proposed_memory}")

    return "\n".join(lines)


def format_saved_memory(saved_memory):
    if saved_memory is None:
        return "No new memory saved."

    return f"""
### {saved_memory.memory_id} | {saved_memory.memory_type.upper()}

**Content:** {saved_memory.content}

**Tags:** {", ".join(saved_memory.tags)}

**Importance:** {saved_memory.importance}

**Created at:** {saved_memory.created_at}

**Source:** {saved_memory.source}
""".strip()


def run_app(query, top_k, save_new_memory):
    if not query or not query.strip():
        return (
            "Please enter a query.",
            "",
            "",
            "",
            "",
            pd.DataFrame(agent.audit_log)
        )

    result = agent.run(
        query=query,
        top_k=int(top_k),
        save_new_memory=save_new_memory
    )

    agent_answer = result["agent_response"]
    retrieved_display = format_retrieved_memories(result["retrieved_memories"])
    compressed_context = result["compressed_context"]
    write_decision_display = format_write_decision(result["write_decision"])
    saved_memory_display = format_saved_memory(result["saved_memory"])
    audit_df = pd.DataFrame(agent.audit_log)

    memory_store.export_to_json(MEMORY_FILE)
    agent.export_audit_log(AUDIT_LOG_FILE)

    return (
        agent_answer,
        retrieved_display,
        compressed_context,
        write_decision_display,
        saved_memory_display,
        audit_df
    )


with gr.Blocks(title="Memory-Augmented Agent") as demo:
    gr.Markdown(
        """
# 03. Memory-Augmented Agent

A personal project memory assistant that retrieves relevant prior context, separates semantic and episodic memory, compresses retrieved memories, answers the user, and decides whether new information should be saved.

**Agent pattern:** Retrieve memory → compress context → answer → decide whether to save new memory.
"""
    )

    with gr.Row():
        with gr.Column(scale=2):
            query_input = gr.Textbox(
                label="User Query",
                placeholder="Ask something like: How should we describe Agent 3 in the README?",
                lines=4
            )

            with gr.Row():
                top_k_input = gr.Slider(
                    minimum=1,
                    maximum=6,
                    value=4,
                    step=1,
                    label="Number of memories to retrieve"
                )

                save_memory_input = gr.Checkbox(
                    label="Save new memory when policy recommends it",
                    value=True
                )

            run_button = gr.Button("Run Memory Agent")

        with gr.Column(scale=2):
            agent_answer_output = gr.Markdown(label="Agent Answer")

    with gr.Tab("Retrieved Memories"):
        retrieved_output = gr.Markdown()

    with gr.Tab("Compressed Context"):
        compressed_context_output = gr.Textbox(
            label="Compressed Context",
            lines=12
        )

    with gr.Tab("Memory Write Decision"):
        write_decision_output = gr.Markdown()

    with gr.Tab("Saved Memory"):
        saved_memory_output = gr.Markdown()

    with gr.Tab("Audit Log"):
        audit_log_output = gr.Dataframe(
            label="Audit Log",
            interactive=False
        )

    run_button.click(
        fn=run_app,
        inputs=[
            query_input,
            top_k_input,
            save_memory_input
        ],
        outputs=[
            agent_answer_output,
            retrieved_output,
            compressed_context_output,
            write_decision_output,
            saved_memory_output,
            audit_log_output
        ]
    )


if __name__ == "__main__":
    demo.launch()
