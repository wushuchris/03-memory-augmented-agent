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

This project demonstrates a governed memory layer for a fictional **Harborlight Support Portal** enterprise rollout. Support, Operations, and Engineering have already made decisions about launch prerequisites, ownership, timing, and readiness reviews across multiple meetings. The operational risk is losing those decisions during a handoff—or forcing every new interaction to reload the entire project history just to stay consistent.

Agent 3 retrieves only the prior project context relevant to the current request, compresses that context, produces a memory-grounded response, and then lets deterministic application policy decide whether the new interaction should be **saved, skipped, or blocked**.

All public-demo content is synthetic.

## Core Pattern

```text
Retrieve → Compress → Answer → Evaluate memory write → Save / Skip / Block
```

The central control principle is:

> **The agent can recall context. Application code owns retention.**

## Why This Matters

Useful agent memory is not just a vector-search problem. A production-quality memory system also needs to answer:

- Which memories are relevant to this turn?
- Which facts are stable versus event-specific?
- What belongs in durable memory?
- What should be useful for the current turn but discarded afterward?
- What content should never be stored?
- How can memory behavior be audited without retaining unnecessary raw user content?
- How do we prevent public demo visitors from mutating one another's state?

In the Harborlight scenario, memory creates **business continuity across handoffs** while application policy prevents “remember everything” from becoming the default.

## Architecture

```text
User request
    ↓
Session-scoped synthetic memory store
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
    └── BLOCK → protected-looking content is not stored
    ↓
Metadata-only session audit
```

## Memory Types

### Semantic memory

Stable project context, ownership, and durable working preferences.

Example:

```text
Operations owns the onboarding checklist and coordinates pilot-readiness updates with Support and Engineering.
```

### Episodic memory

Specific prior decisions, meetings, schedules, and events.

Example:

```text
The enterprise pilot may not begin until single sign-on and audit logging have both passed the readiness checklist.
```

## Memory Governance

The public demo uses application-owned memory policy rather than saving every interaction.

### SAVE

Used for explicit durable project facts or decisions such as:

- project ownership,
- schedules and deadlines,
- durable preferences,
- explicit remember requests that pass policy.

### SKIP

Used for information that is useful now but should not become a new memory, such as:

- ordinary retrieval questions,
- transient requests,
- interactions without a clear durable project fact.

### BLOCK

Used before storage when content matches protected patterns such as:

- credential-like content,
- identity data,
- financial-account data,
- medical-record content,
- confidential-client content,
- email addresses.

The policy is intentionally deterministic and inspectable. It is a demo control boundary, not a comprehensive enterprise DLP system.

## Public-Demo Privacy and Hygiene Boundary

Agent 3 received a full public-safety retrofit before final deployment.

- The repository contains only synthetic Harborlight baseline memories.
- Each browser session receives an isolated in-memory copy.
- Visitor-created memories are never written back to tracked repository files.
- Runtime audit metadata is session-only.
- The audit trail records control metadata rather than the raw user query.
- A blocked memory write does not add the submitted content to session memory.
- Resetting the session returns to the same synthetic baseline.
- Public-repo hygiene tests scan the checkout for private-source markers and common credential patterns.
- The public Git history was rewritten from a sanitized clean root before the upgraded Space was deployed, removing the previously reachable portfolio-derived demo memories and audit log from normal branch history.

A production implementation would additionally require authenticated user-scoped durable storage, explicit retention/deletion controls, access control, encryption, tenant isolation, and stronger sensitive-data classification.

## Live Observability

The agent exposes its real runtime stages through the same governed execution path used by the application:

1. request received,
2. relevant memories retrieved,
3. working context compressed,
4. write policy evaluated,
5. memory saved / skipped / blocked,
6. response ready,
7. audit metadata recorded.

The UI consumes these real events. There is no separate fake progress workflow.

## Business-First Live Demo

The approved live experience is centered around the fictional Harborlight enterprise-pilot handoff.

Recommended first question:

```text
What did we decide about the enterprise pilot prerequisites?
```

The demo then shows:

- the real Live Memory Activity stream,
- the memory-grounded answer,
- a **Business continuity outcome** summarizing what Harborlight carried forward,
- the memory-policy result for the current turn,
- compact decision context,
- exact retrieved memories and similarity scores under Engineering Evidence,
- metadata-only Audit & Safety output,
- the isolated session memory store,
- and the architecture / public-demo limitation underneath.

The main public tables use controlled light HTML rendering rather than native Gradio dataframes so the engineering evidence remains readable inside the Hugging Face theme. Tab default, hover, focus, and selected states are also explicitly styled to prevent theme drift.

Try a safe memory write:

```text
Remember that the pilot launch checklist must include a final rollback drill.
```

Then try the synthetic safety-boundary example:

```text
Remember my private access token for later.
```

No real token value is provided; the policy should return **BLOCK**.

## Evaluation and Production Gate

Final approved production validation:

- **26 automated tests passed**
- **5/5 retrieval benchmark cases ranked the expected memory at #1**
- **Hit@3 = 100%**
- **MRR = 1.0**
- **3/3 memory-write policy cases passed** for SAVE / SKIP / BLOCK
- public-repository hygiene checks passed
- GitHub → Hugging Face deployment succeeded
- final live presentation was reviewed and approved by the project owner

Deployment is gated on both pytest and the deterministic memory evaluation before Hugging Face synchronization.

## Reusable Primitive

Agent 3 contributes:

> **Retrieve relevant prior context, compress it for the current turn, and place an application-owned governance boundary around what becomes durable memory.**

This becomes a foundation for later retrieval, document, verification, tool-use, workflow, and multi-agent systems.

## Relationship to Agent 4

Agent 3 answers:

> **What prior project context should this agent carry forward, and should this new interaction change memory?**

Agent 4 adds a separate knowledge-access boundary:

> **What approved external evidence is most relevant, and is it strong enough to answer from?**

Memory continuity and approved-corpus retrieval are related but distinct responsibilities.

## Responsible Use

- Use synthetic data in the public demo.
- Do not enter passwords, keys, tokens, personal records, client records, or other sensitive data.
- Memory retrieval relevance does not establish truth.
- A deterministic sensitive-content policy reduces risk but does not replace enterprise privacy/security controls.
- Public demo session state is intentionally ephemeral rather than durable across users or server restarts.
- Public safety reviews must inspect both current files and reachable repository/deployment history.

## Tech

Python, Pydantic, sentence-transformers, scikit-learn, pandas, Gradio, pytest, GitHub Actions, Hugging Face Spaces
