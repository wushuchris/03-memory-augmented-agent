from typing import List, Literal, Optional

from pydantic import BaseModel, Field


MemoryType = Literal["episodic", "semantic"]
MemoryWriteOutcome = Literal["save", "skip", "block"]
MemoryStage = Literal[
    "query_received",
    "memory_retrieved",
    "context_compressed",
    "write_policy_evaluated",
    "memory_saved",
    "memory_skipped",
    "memory_blocked",
    "response_ready",
    "audit_recorded",
]


class Memory(BaseModel):
    memory_id: str
    memory_type: MemoryType
    content: str
    tags: List[str] = Field(default_factory=list)
    importance: int = Field(ge=1, le=5)
    created_at: str
    source: str = "manual"
    sensitivity: Literal["public_demo"] = "public_demo"


class RetrievedMemory(BaseModel):
    memory: Memory
    similarity_score: float
    rank: int = Field(ge=1)


class MemoryWriteDecision(BaseModel):
    outcome: MemoryWriteOutcome
    should_save: bool
    reason: str
    memory_type: Optional[MemoryType] = None
    importance: Optional[int] = Field(default=None, ge=1, le=5)
    proposed_memory: Optional[str] = None
    policy_flags: List[str] = Field(default_factory=list)


class MemoryEvent(BaseModel):
    stage: MemoryStage
    message: str
    memory_ids: List[str] = Field(default_factory=list)
    decision: Optional[MemoryWriteOutcome] = None
