
from datetime import datetime
from typing import List

import pandas as pd

from schemas import RetrievedMemory, MemoryWriteDecision
from memory_store import MemoryStore


class MemoryAugmentedAgent:
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.audit_log = []

    def compress_context(self, retrieved_memories: List[RetrievedMemory]) -> str:
        if not retrieved_memories:
            return "No relevant memories were retrieved."

        episodic = []
        semantic = []

        for item in retrieved_memories:
            memory = item.memory
            if memory.memory_type == "episodic":
                episodic.append(memory.content)
            elif memory.memory_type == "semantic":
                semantic.append(memory.content)

        summary_parts = []

        if semantic:
            summary_parts.append("Stable project context:")
            for memory in semantic:
                summary_parts.append(f"- {memory}")

        if episodic:
            summary_parts.append("Relevant prior events:")
            for memory in episodic:
                summary_parts.append(f"- {memory}")

        return "\n".join(summary_parts)

    def generate_response(self, query: str, compressed_context: str) -> str:
        response = f"""
Based on the retrieved project memory, here is the recommended response.

User query:
{query}

Relevant memory context:
{compressed_context}

Agent answer:
Agent 3 should be implemented as a Memory-Augmented Project Assistant. Its job is to retrieve relevant prior project context, separate semantic memory from episodic memory, compress that context, and use it to answer the user's current request.

The agent demonstrates the following pattern:

1. Receive a user query.
2. Retrieve relevant memories.
3. Separate stable facts from prior events.
4. Compress the retrieved memories into a short working context.
5. Generate an answer using that context.
6. Decide whether the new interaction should be saved as memory.

This makes Agent 3 a strong continuation of the first two agents:
- Agent 1 demonstrated bounded decision-making.
- Agent 2 demonstrated structured planning.
- Agent 3 demonstrates persistent context and recall.
"""
        return response.strip()

    def decide_memory_write(self, user_query: str, agent_response: str) -> MemoryWriteDecision:
        important_keywords = [
            "decide",
            "decided",
            "prefer",
            "preference",
            "agent",
            "project",
            "readme",
            "github",
            "portfolio",
            "final",
            "change",
            "update",
            "remember"
        ]

        query_lower = user_query.lower()
        should_save = any(keyword in query_lower for keyword in important_keywords)

        if should_save:
            return MemoryWriteDecision(
                should_save=True,
                memory_type="episodic",
                importance=4,
                reason="The query appears related to an important project decision or preference.",
                proposed_memory=f"The user asked: '{user_query}'. The agent responded with guidance related to the memory-augmented agent project."
            )

        return MemoryWriteDecision(
            should_save=False,
            reason="The interaction does not appear important enough to store as long-term memory."
        )

    def log_run(self, result):
        retrieved_memory_ids = [
            item.memory.memory_id for item in result["retrieved_memories"]
        ]

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": result["query"],
            "retrieved_memory_ids": retrieved_memory_ids,
            "compressed_context": result["compressed_context"],
            "write_decision": result["write_decision"].should_save,
            "write_reason": result["write_decision"].reason
        }

        self.audit_log.append(log_entry)
        return log_entry

    def run(self, query: str, top_k: int = 4, save_new_memory: bool = True):
        retrieved = self.memory_store.retrieve(query, top_k=top_k)
        compressed_context = self.compress_context(retrieved)
        agent_response = self.generate_response(query, compressed_context)
        write_decision = self.decide_memory_write(query, agent_response)

        result = {
            "query": query,
            "retrieved_memories": retrieved,
            "compressed_context": compressed_context,
            "agent_response": agent_response,
            "write_decision": write_decision
        }

        log_entry = self.log_run(result)

        saved_memory = None
        if save_new_memory:
            saved_memory = self.memory_store.save_memory_from_decision(write_decision)

        result["log_entry"] = log_entry
        result["saved_memory"] = saved_memory

        return result

    def export_audit_log(self, filepath: str):
        audit_df = pd.DataFrame(self.audit_log)
        audit_df.to_csv(filepath, index=False)
        return audit_df
