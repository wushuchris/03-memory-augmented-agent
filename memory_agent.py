from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

from memory_policy import evaluate_memory_write
from memory_store import MemoryStore
from schemas import MemoryEvent, RetrievedMemory


class MemoryAugmentedAgent:
    def __init__(self, memory_store: MemoryStore, audit_log: Optional[Iterable[dict]] = None):
        self.memory_store = memory_store
        self.audit_log = list(audit_log or [])

    def compress_context(self, retrieved_memories: List[RetrievedMemory]) -> str:
        if not retrieved_memories:
            return "No relevant project memories were retrieved."

        semantic = [item.memory.content for item in retrieved_memories if item.memory.memory_type == "semantic"]
        episodic = [item.memory.content for item in retrieved_memories if item.memory.memory_type == "episodic"]
        parts: List[str] = []

        if semantic:
            parts.append("Stable project context:")
            parts.extend(f"- {memory}" for memory in semantic)
        if episodic:
            if parts:
                parts.append("")
            parts.append("Relevant prior decisions and events:")
            parts.extend(f"- {memory}" for memory in episodic)

        return "\n".join(parts)

    def generate_response(self, query: str, retrieved_memories: List[RetrievedMemory]) -> str:
        if not retrieved_memories:
            return (
                "I do not have enough remembered project context to answer this from memory. "
                "The demo will not invent a project memory that was not retrieved."
            )

        lines = [
            "Here is the most relevant remembered project context for this request:",
            "",
        ]
        for item in retrieved_memories[:4]:
            lines.append(f"- {item.memory.content}")

        lines.extend(
            [
                "",
                "Memory boundary: this answer is derived only from the session memories shown in the inspection panel.",
            ]
        )
        return "\n".join(lines)

    def log_run(self, result: Dict) -> dict:
        retrieved_memory_ids = [item.memory.memory_id for item in result["retrieved_memories"]]
        decision = result["write_decision"]
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_length": len(result["query"]),
            "retrieved_memory_ids": retrieved_memory_ids,
            "write_outcome": decision.outcome,
            "write_reason": decision.reason,
            "policy_flags": decision.policy_flags,
            "memory_count_after_run": len(self.memory_store.memories),
        }
        self.audit_log.append(log_entry)
        return log_entry

    @staticmethod
    def _frame(event: MemoryEvent, result: Dict) -> Dict:
        return {"event": event, "result": dict(result)}

    def run_iter(self, query: str, top_k: int = 4, save_new_memory: bool = True):
        clean_query = (query or "").strip()
        result: Dict = {
            "query": clean_query,
            "retrieved_memories": [],
            "compressed_context": "",
            "agent_response": "",
            "write_decision": None,
            "saved_memory": None,
            "log_entry": None,
        }

        yield self._frame(
            MemoryEvent(stage="query_received", message="Request received. The agent is deciding which memories are relevant."),
            result,
        )

        retrieved = self.memory_store.retrieve(clean_query, top_k=top_k)
        result["retrieved_memories"] = retrieved
        yield self._frame(
            MemoryEvent(
                stage="memory_retrieved",
                message=f"Retrieved {len(retrieved)} ranked memories from this session's memory store.",
                memory_ids=[item.memory.memory_id for item in retrieved],
            ),
            result,
        )

        compressed_context = self.compress_context(retrieved)
        result["compressed_context"] = compressed_context
        yield self._frame(
            MemoryEvent(stage="context_compressed", message="Separated stable context from prior events and compressed the working context."),
            result,
        )

        write_decision = evaluate_memory_write(clean_query)
        result["write_decision"] = write_decision
        yield self._frame(
            MemoryEvent(
                stage="write_policy_evaluated",
                message=f"Memory write policy returned: {write_decision.outcome.upper()}.",
                decision=write_decision.outcome,
            ),
            result,
        )

        saved_memory = None
        if save_new_memory and write_decision.outcome == "save":
            saved_memory = self.memory_store.save_memory_from_decision(write_decision)
            result["saved_memory"] = saved_memory
            yield self._frame(
                MemoryEvent(
                    stage="memory_saved",
                    message="The approved project memory was added to this browser session only.",
                    memory_ids=[saved_memory.memory_id] if saved_memory else [],
                    decision="save",
                ),
                result,
            )
        elif write_decision.outcome == "block":
            yield self._frame(
                MemoryEvent(
                    stage="memory_blocked",
                    message="The application blocked this content from becoming long-term memory.",
                    decision="block",
                ),
                result,
            )
        else:
            yield self._frame(
                MemoryEvent(
                    stage="memory_skipped",
                    message=(
                        "Memory storage is disabled for this run."
                        if not save_new_memory and write_decision.outcome == "save"
                        else "The interaction was useful for this turn but was not saved as durable memory."
                    ),
                    decision="skip",
                ),
                result,
            )

        result["agent_response"] = self.generate_response(clean_query, retrieved)
        yield self._frame(
            MemoryEvent(stage="response_ready", message="Memory-grounded response is ready."),
            result,
        )

        result["log_entry"] = self.log_run(result)
        yield self._frame(
            MemoryEvent(stage="audit_recorded", message="Recorded control metadata without storing the raw query in the audit log."),
            result,
        )

    def run(self, query: str, top_k: int = 4, save_new_memory: bool = True):
        last_frame = None
        for frame in self.run_iter(query=query, top_k=top_k, save_new_memory=save_new_memory):
            last_frame = frame
        return last_frame["result"] if last_frame else None
