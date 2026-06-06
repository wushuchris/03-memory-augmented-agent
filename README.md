---
title: 03 Memory Augmented Agent
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "5.0.0"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 03. Memory-Augmented Agent — Personal Project Memory Assistant

## Goal

Build an agent that uses persistent memory and context recall to support an ongoing project.

## Approach

The agent stores structured episodic and semantic memories, embeds them into a lightweight vector-style memory store, retrieves relevant prior context, compresses that context, generates a memory-informed response, and decides whether new information should be saved.

The core pattern is:

```text
Retrieve memory → compress context → answer → decide whether to save new memory
```

## Outcome

Delivered a GitHub-ready memory-augmented agent that can recall project history, explain which memories were used, maintain an auditable memory log, and learn new session memories when the write policy recommends saving them.

## Tech

- Python
- Pydantic
- sentence-transformers
- scikit-learn cosine similarity
- pandas
- Gradio

## Focus

- Persistent memory
- Vector-style semantic retrieval
- Episodic memory
- Semantic memory
- Context compression
- Memory retrieval policy
- Memory write policy
- Auditability

## Agent Pattern

This project demonstrates a memory-augmented agent loop:

1. Receive a user query.
2. Embed the query.
3. Retrieve the most relevant memories.
4. Separate semantic memory from episodic memory.
5. Compress retrieved memory into a working context.
6. Generate an answer using that context.
7. Decide whether the interaction should be stored.
8. Save new memory when appropriate.
9. Log the run for auditability.

## Memory Types

### Semantic Memory

Stable facts about the project or user preferences.

Example:

```text
The user is building a portfolio project called 30 Agents for AI Engineers.
```

### Episodic Memory

Specific prior events, decisions, or interactions.

Example:

```text
Agent 1 was an Autonomous Decision-Making Agent using the pattern: Rules decide. The LLM explains. Guardrails review.
```

## Demo Interface

The Gradio interface exposes the agent’s workflow through visible panels:

- Agent Answer
- Retrieved Memories
- Compressed Context
- Memory Write Decision
- Saved Memory
- Audit Log

This makes the memory system inspectable rather than hidden.
## Live Demo

[Hugging Face Space | Your Own HF Login may be required](https://huggingface.co/spaces/FlyingNunchucks/03-memory-augmented-agent)

## Example Queries

```text
How should we describe Agent 3 in the README?
```

```text
How is Agent 3 different from Agent 1 and Agent 2?
```

```text
Remember that Agent 3 should be positioned as a continuity system.
```

```text
What did I say Agent 3 should be positioned as?
```

## Project Structure

```text
03_memory_augmented_agent/
│
├── app.py
├── memory_agent.py
├── memory_store.py
├── schemas.py
├── sample_memories.json
├── memory_agent_audit_log.csv
├── requirements.txt
└── README.md
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

## Portfolio Summary

**03. Memory-Augmented Agent — Personal Project Memory Assistant**

**Goal:** Build an agent with persistent memory and context recall.

**Approach:** Combined structured Pydantic memory schemas, sentence-transformer embeddings, cosine similarity retrieval, semantic/episodic memory separation, context compression, memory write policy, session learning, Gradio demo, and auditable CSV/JSON logs.

**Outcome:** Delivered a GitHub-ready memory-augmented agent that retrieves relevant prior context, explains which memories were used, saves important new memories, and provides visible auditability through the demo interface.

**Tech:** Python, Pydantic, pandas, sentence-transformers, scikit-learn, Gradio

**Focus:** Persistent memory, semantic retrieval, episodic memory, semantic memory, context compression, retrieval policy, memory write policy, auditability
