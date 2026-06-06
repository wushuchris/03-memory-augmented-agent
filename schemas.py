
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Memory(BaseModel):
    memory_id: str
    memory_type: Literal["episodic", "semantic"]
    content: str
    tags: List[str] = Field(default_factory=list)
    importance: int = Field(ge=1, le=5)
    created_at: str
    source: str = "manual"


class RetrievedMemory(BaseModel):
    memory: Memory
    similarity_score: float


class MemoryWriteDecision(BaseModel):
    should_save: bool
    memory_type: Optional[Literal["episodic", "semantic"]] = None
    importance: Optional[int] = None
    reason: str
    proposed_memory: Optional[str] = None
