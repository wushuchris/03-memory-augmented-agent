import json
from datetime import datetime, timezone
from typing import Iterable, List, Optional
from uuid import uuid4

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from schemas import Memory, RetrievedMemory, MemoryWriteDecision


class MemoryStore:
    def __init__(
        self,
        memories: Iterable[Memory],
        model_name: str = "all-MiniLM-L6-v2",
        embedding_model: Optional[SentenceTransformer] = None,
    ):
        self.memories = list(memories)
        self.embedding_model = embedding_model or SentenceTransformer(model_name)
        self.refresh_embeddings()

    def refresh_embeddings(self) -> None:
        self.memory_texts = [memory.content for memory in self.memories]
        if not self.memory_texts:
            self.memory_embeddings = np.empty((0, 0))
            return
        self.memory_embeddings = self.embedding_model.encode(self.memory_texts)

    def retrieve(self, query: str, top_k: int = 4) -> List[RetrievedMemory]:
        if not self.memories or not query.strip():
            return []

        safe_top_k = max(1, min(int(top_k), len(self.memories)))
        query_embedding = self.embedding_model.encode([query])
        similarities = cosine_similarity(query_embedding, self.memory_embeddings)[0]
        ranked_indices = similarities.argsort()[::-1][:safe_top_k]

        return [
            RetrievedMemory(
                memory=self.memories[index],
                similarity_score=float(similarities[index]),
                rank=rank,
            )
            for rank, index in enumerate(ranked_indices, start=1)
        ]

    def save_memory_from_decision(self, write_decision: MemoryWriteDecision) -> Optional[Memory]:
        if write_decision.outcome != "save" or not write_decision.should_save:
            return None
        if not write_decision.proposed_memory:
            return None

        new_memory = Memory(
            memory_id=f"session_{uuid4().hex[:10]}",
            memory_type=write_decision.memory_type or "episodic",
            content=write_decision.proposed_memory,
            tags=["session_memory", "policy_approved"],
            importance=write_decision.importance or 3,
            created_at=datetime.now(timezone.utc).date().isoformat(),
            source="session_write_policy",
        )
        self.memories.append(new_memory)
        self.refresh_embeddings()
        return new_memory

    def to_dicts(self) -> List[dict]:
        return [memory.model_dump() for memory in self.memories]

    def export_to_json(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(self.to_dicts(), file, indent=2)


def memories_from_dicts(memory_data: Iterable[dict]) -> List[Memory]:
    return [Memory(**item) for item in memory_data]


def load_memories_from_json(filepath: str) -> List[Memory]:
    with open(filepath, "r", encoding="utf-8") as file:
        memory_data = json.load(file)
    return memories_from_dicts(memory_data)
