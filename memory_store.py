
import json
from datetime import datetime
from typing import List, Optional

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from schemas import Memory, RetrievedMemory, MemoryWriteDecision


class MemoryStore:
    def __init__(self, memories: List[Memory], model_name: str = "all-MiniLM-L6-v2"):
        self.memories = memories
        self.embedding_model = SentenceTransformer(model_name)
        self.refresh_embeddings()

    def refresh_embeddings(self):
        self.memory_texts = [memory.content for memory in self.memories]
        self.memory_embeddings = self.embedding_model.encode(self.memory_texts)

    def retrieve(self, query: str, top_k: int = 4) -> List[RetrievedMemory]:
        query_embedding = self.embedding_model.encode([query])
        similarities = cosine_similarity(query_embedding, self.memory_embeddings)[0]

        ranked_indices = similarities.argsort()[::-1][:top_k]

        retrieved = []
        for index in ranked_indices:
            retrieved.append(
                RetrievedMemory(
                    memory=self.memories[index],
                    similarity_score=float(similarities[index])
                )
            )

        return retrieved

    def save_memory_from_decision(
        self,
        write_decision: MemoryWriteDecision
    ) -> Optional[Memory]:
        if not write_decision.should_save:
            return None

        if not write_decision.proposed_memory:
            return None

        new_memory_id = f"mem_{len(self.memories) + 1:03d}"

        new_memory = Memory(
            memory_id=new_memory_id,
            memory_type=write_decision.memory_type or "episodic",
            content=write_decision.proposed_memory,
            tags=["session_memory", "agent_generated"],
            importance=write_decision.importance or 3,
            created_at=datetime.now().date().isoformat(),
            source="agent_write_policy"
        )

        self.memories.append(new_memory)
        self.refresh_embeddings()

        return new_memory

    def export_to_json(self, filepath: str):
        memory_dicts = [memory.model_dump() for memory in self.memories]

        with open(filepath, "w") as file:
            json.dump(memory_dicts, file, indent=2)


def load_memories_from_json(filepath: str) -> List[Memory]:
    with open(filepath, "r") as file:
        memory_data = json.load(file)

    return [Memory(**item) for item in memory_data]
