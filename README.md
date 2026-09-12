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

# 03. Memory-Augmented Agent — Governed Project Continuity

## Business Question

> **How can an AI remember useful project context across turns without storing everything forever?**

This project demonstrates a memory layer for a fictional Harborlight Support Portal rollout. The agent retrieves relevant prior context, separates stable facts from prior events, compresses the working context, answers from recalled memory, and then lets deterministic application policy decide whether the new interaction should be **saved, skipped, or blocked**.

All public-demo content is synthetic.

## Core Pattern

```text
Retrieve → Compress → Answer → Evaluate memory write → Save / Skip / Block
```

## Why This Matters

Useful agent memory is not just a vector search problem. A production-quality memory system also needs to answer:

- Which memories are relevant to this turn?
- Which facts are stable versus event-specific?
- What belongs in long-term memory?
- What should be ignored after the current turn?
- What content should never be stored?
- How can memory behavior be audited without retaining unnecessary raw user content?

## Architecture

```text
User request
    ↓
Session-scoped memory store
    ↓
Sentence-transformer retrieval
    ↓
Semantic + episodic separation
    ↓
Compressed working context
    ↓
Memory-grounded response
    ↓
Deterministic write policy
    ├── SAVE  → add to this browser session
    ├── SKIP  → useful now, not durable memory
    └── BLOCK → sensitive-looking content is not stored
    ↓
Metadata-only session audit
```

## Memory Types

### Semantic memory

Stable project context, ownership, and durable preferences.

Example:

```text
Project status updates should be concise and organized into decisions, risks, and next actions.
```

### Episodic memory

Specific prior decisions, meetings, schedules, and events.

Example:

```text
The team scheduled the customer pilot for September 30, 2026 after an internal alpha review.
```

## Memory Governance

The public demo uses application-owned memory policy rather than saving every interaction.

**SAVE**
- explicit remember requests,
- durable decisions,
- project ownership,
- schedules and deadlines,
- durable preferences.

**SKIP**
- ordinary retrieval questions,
- transient requests,
- interactions without a clear durable project fact.

**BLOCK**
- credential-like content,
- identity data,
- financial-account data,
- medical-record content,
- confidential-client content,
- email addresses.

The safety policy is intentionally deterministic and inspectable. It is a demo control boundary, not a comprehensive DLP system.

## Public-Demo Privacy Boundary

The Space is intentionally designed so public users do **not** share a mutable durable memory store.

- The repository contains only synthetic baseline memories.
- Each browser session receives an isolated in-memory copy.
- Visitor-created memories are not written back to tracked files.
- Runtime audit metadata is session-only.
- The audit trail records control metadata rather than the raw user query.
- Resetting the session returns to the synthetic baseline.

A production implementation would use authenticated user-scoped persistence, explicit retention/deletion controls, access control, encryption, and stronger sensitive-data classification.

## Live Observability

The agent exposes the real runtime stages used by the application:

1. request received,
2. memory retrieved,
3. working context compressed,
4. write policy evaluated,
5. memory saved / skipped / blocked,
6. response ready,
7. audit metadata recorded.

The UI consumes the same observable agent loop used by the programmatic `run()` API; there is no separate fake progress workflow.

## Live Demo

[Hugging Face Space](https://huggingface.co/spaces/FlyingNunchucks/03-memory-augmented-agent)

Recommended first question:

```text
What did we decide about the enterprise pilot prerequisites?
```

Then try a safe memory write:

```text
Remember that the pilot launch checklist must include a final rollback drill.
```

The demo also includes a safety-boundary example that asks the application to remember a private access token **without providing any real token value**. The write policy should block it.

## Reusable Primitive

Agent 3 contributes a reusable memory primitive:

> **Retrieve relevant context, compress it for the current turn, and place a governed application boundary around what becomes durable memory.**

This primitive becomes a foundation for later retrieval, document, verification, tool-use, and multi-agent systems.

## Responsible Use

- Use synthetic data in the public demo.
- Do not enter passwords, keys, tokens, personal records, client records, or other sensitive data.
- Memory retrieval relevance does not establish truth.
- A deterministic sensitive-content policy reduces risk but does not replace enterprise privacy/security controls.
- Public demo session state is intentionally ephemeral rather than durable across users or server restarts.

## Tech

Python, Pydantic, sentence-transformers, scikit-learn, pandas, Gradio, pytest, GitHub Actions, Hugging Face Spaces
