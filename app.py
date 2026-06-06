import pandas as pd
import gradio as gr

from memory_store import MemoryStore, load_memories_from_json
from memory_agent import MemoryAugmentedAgent


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
        lines.append(f"Memory ID: {memory.memory_id}")
        lines.append(f"Type: {memory.memory_type}")
        lines.append(f"Similarity Score: {item.similarity_score:.3f}")
        lines.append(f"Importance: {memory.importance}")
        lines.append(f"Tags: {', '.join(memory.tags)}")
        lines.append("")
        lines.append(memory.content)
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    return "\n".join(lines)


def format_write_decision(write_decision):
    lines = [
        f"Should save: {write_decision.should_save}",
        f"Reason: {write_decision.reason}"
    ]

    if write_decision.memory_type:
        lines.append(f"Memory type: {write_decision.memory_type}")

    if write_decision.importance:
        lines.append(f"Importance: {write_decision.importance}")

    if write_decision.proposed_memory:
        lines.append("")
        lines.append("Proposed memory:")
        lines.append(write_decision.proposed_memory)

    return "\n".join(lines)


def format_saved_memory(saved_memory):
    if saved_memory is None:
        return "No new memory saved."

    lines = [
        f"Memory ID: {saved_memory.memory_id}",
        f"Type: {saved_memory.memory_type}",
        f"Importance: {saved_memory.importance}",
        f"Created at: {saved_memory.created_at}",
        f"Source: {saved_memory.source}",
        f"Tags: {', '.join(saved_memory.tags)}",
        "",
        "Content:",
        saved_memory.content
    ]

    return "\n".join(lines)


def run_app(query, top_k, save_new_memory):
    if not query or not query.strip():
        return (
            "Please enter a query.",
            "No memories retrieved.",
            "No context compressed.",
            "No write decision made.",
            "No memory saved.",
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


force_light_mode_js = """
function() {
    const url = new URL(window.location.href);
    if (url.searchParams.get("__theme") !== "light") {
        url.searchParams.set("__theme", "light");
        window.location.replace(url.toString());
    }
}
"""


custom_css = """
:root {
    --body-background-fill: #f8fafc !important;
    --body-text-color: #111827 !important;
    --background-fill-primary: #ffffff !important;
    --background-fill-secondary: #f8fafc !important;
    --block-background-fill: #ffffff !important;
    --block-border-color: #d1d5db !important;
    --block-label-text-color: #111827 !important;
    --input-background-fill: #ffffff !important;
    --input-border-color: #cbd5e1 !important;
    --input-placeholder-color: #64748b !important;
    --neutral-50: #f8fafc !important;
    --neutral-100: #f1f5f9 !important;
    --neutral-200: #e2e8f0 !important;
    --neutral-300: #cbd5e1 !important;
    --neutral-700: #334155 !important;
    --neutral-800: #1f2937 !important;
    --neutral-900: #111827 !important;
}

html,
body,
gradio-app,
.gradio-container {
    background: #f8fafc !important;
    color: #111827 !important;
}

.gradio-container {
    max-width: 1120px !important;
    margin: 0 auto !important;
    padding: 28px !important;
}

#memory-agent-header {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 18px !important;
    padding: 30px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06) !important;
}

#memory-agent-header h1 {
    color: #111827 !important;
    font-size: 2.2rem !important;
    line-height: 1.15 !important;
    margin-bottom: 10px !important;
}

#memory-agent-header p {
    color: #374151 !important;
    font-size: 1.05rem !important;
    line-height: 1.6 !important;
}

#pattern-box {
    margin-top: 16px !important;
    padding: 14px 16px !important;
    background: #eef2ff !important;
    border: 1px solid #c7d2fe !important;
    border-radius: 12px !important;
    color: #312e81 !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 0.95rem !important;
}

#examples-box {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    padding: 18px !important;
    margin-top: 14px !important;
}

#examples-box h3,
#examples-box li {
    color: #111827 !important;
}

#examples-box li {
    margin-bottom: 8px !important;
}

h1,
h2,
h3,
h4,
p,
li,
label,
span,
.prose,
.markdown,
.gr-markdown {
    color: #111827 !important;
    opacity: 1 !important;
}

.block,
.form,
.gr-box,
.input-container,
.output-container {
    background: #ffffff !important;
    color: #111827 !important;
    border-color: #d1d5db !important;
}

textarea,
input {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #cbd5e1 !important;
    opacity: 1 !important;
    font-size: 0.95rem !important;
    line-height: 1.45 !important;
}

textarea::placeholder,
input::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

button {
    border-radius: 10px !important;
    font-weight: 700 !important;
}

button.primary,
button[variant="primary"] {
    background: #4f46e5 !important;
    color: #ffffff !important;
    border-color: #4f46e5 !important;
}

table,
thead,
tbody,
tr,
td,
th {
    background: #ffffff !important;
    color: #111827 !important;
    border-color: #d1d5db !important;
}

footer {
    color: #475569 !important;
}
"""


with gr.Blocks(
    title="03. Memory-Augmented Agent",
    theme=gr.themes.Default(),
    css=custom_css,
    js=force_light_mode_js
) as demo:

    gr.HTML(
        """
        <div id="memory-agent-header">
            <h1>03. Memory-Augmented Agent</h1>
            <p>
                A personal project memory assistant that retrieves relevant prior context,
                separates semantic and episodic memory, compresses retrieved memories,
                answers the user, and decides whether new information should be saved.
            </p>
            <div id="pattern-box">
                Retrieve memory → compress context → answer → decide whether to save new memory
            </div>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label="User Query",
                placeholder="Ask something like: How should we describe Agent 3 in the README?",
                lines=5
            )

            run_button = gr.Button(
                "Run Memory Agent",
                variant="primary"
            )

        with gr.Column(scale=2):
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

            gr.HTML(
                """
                <div id="examples-box">
                    <h3>Try these</h3>
                    <ul>
                        <li>How is Agent 3 different from Agent 1 and Agent 2?</li>
                        <li>Remember that Agent 3 should be positioned as a continuity system.</li>
                        <li>What did I say Agent 3 should be positioned as?</li>
                    </ul>
                </div>
                """
            )

    gr.Markdown("## Agent Answer")

    agent_answer_output = gr.Textbox(
        label="Memory-informed response",
        lines=14
    )

    gr.Markdown("## Memory Inspection")

    with gr.Row():
        with gr.Column():
            retrieved_output = gr.Textbox(
                label="Retrieved Memories",
                lines=16
            )

        with gr.Column():
            compressed_context_output = gr.Textbox(
                label="Compressed Context",
                lines=16
            )

    with gr.Row():
        with gr.Column():
            write_decision_output = gr.Textbox(
                label="Memory Write Decision",
                lines=10
            )

        with gr.Column():
            saved_memory_output = gr.Textbox(
                label="Saved Memory",
                lines=10
            )

    gr.Markdown("## Audit Log")

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