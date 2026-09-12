import hashlib
import re

import numpy as np

from memory_agent import MemoryAugmentedAgent
from memory_policy import evaluate_memory_write
from memory_store import MemoryStore, load_memories_from_json, memories_from_dicts
from schemas import Memory


class HashingEmbedder:
    """Small deterministic embedder for unit tests; no network/model download required."""

    dimensions = 128

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        rows = []
        for text in texts:
            vector = np.zeros(self.dimensions, dtype=float)
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                vector[index] += 1.0
            rows.append(vector)
        return np.vstack(rows)


def baseline_store():
    return MemoryStore(load_memories_from_json("sample_memories.json"), embedding_model=HashingEmbedder())


def test_synthetic_baseline_loads_with_expected_memory_types():
    memories = load_memories_from_json("sample_memories.json")
    assert len(memories) == 8
    assert {memory.memory_type for memory in memories} == {"semantic", "episodic"}
    assert all(memory.sensitivity == "public_demo" for memory in memories)


def test_retrieval_surfaces_enterprise_pilot_memory():
    store = baseline_store()
    results = store.retrieve("enterprise pilot single sign-on audit readiness", top_k=3)
    assert any(item.memory.memory_id == "mem_003" for item in results)
    assert [item.rank for item in results] == [1, 2, 3]


def test_empty_store_retrieval_is_safe():
    store = MemoryStore([], embedding_model=HashingEmbedder())
    assert store.retrieve("anything", top_k=4) == []


def test_question_is_skipped_by_write_policy():
    decision = evaluate_memory_write("What did we decide about the pilot?")
    assert decision.outcome == "skip"
    assert decision.should_save is False


def test_explicit_safe_memory_request_is_saved_by_policy():
    decision = evaluate_memory_write("Remember that the launch checklist must include a rollback drill.")
    assert decision.outcome == "save"
    assert decision.should_save is True
    assert decision.proposed_memory == "The launch checklist must include a rollback drill."


def test_credential_like_memory_is_blocked():
    decision = evaluate_memory_write("Remember my private access token for later.")
    assert decision.outcome == "block"
    assert decision.should_save is False
    assert "credential" in decision.policy_flags


def test_email_address_is_blocked():
    decision = evaluate_memory_write("Remember that the owner is demo.user@example.com")
    assert decision.outcome == "block"
    assert "email_address" in decision.policy_flags


def test_blocked_memory_never_enters_store():
    store = baseline_store()
    agent = MemoryAugmentedAgent(store)
    before = len(store.memories)
    result = agent.run("Remember my private access token for later.", top_k=3, save_new_memory=True)
    assert result["write_decision"].outcome == "block"
    assert result["saved_memory"] is None
    assert len(store.memories) == before


def test_safe_memory_write_is_session_local():
    store = baseline_store()
    agent = MemoryAugmentedAgent(store)
    before = len(store.memories)
    result = agent.run(
        "Remember that the pilot launch checklist must include a final rollback drill.",
        top_k=3,
        save_new_memory=True,
    )
    assert result["write_decision"].outcome == "save"
    assert result["saved_memory"] is not None
    assert len(store.memories) == before + 1


def test_disabling_writes_prevents_policy_approved_save():
    store = baseline_store()
    agent = MemoryAugmentedAgent(store)
    before = len(store.memories)
    result = agent.run(
        "Remember that the pilot launch checklist must include a final rollback drill.",
        top_k=3,
        save_new_memory=False,
    )
    assert result["write_decision"].outcome == "save"
    assert result["saved_memory"] is None
    assert len(store.memories) == before


def test_run_iter_exposes_real_memory_stages():
    store = baseline_store()
    agent = MemoryAugmentedAgent(store)
    frames = list(agent.run_iter("What did we decide about enterprise pilot readiness?", top_k=3))
    stages = [frame["event"].stage for frame in frames]
    assert stages[:4] == [
        "query_received",
        "memory_retrieved",
        "context_compressed",
        "write_policy_evaluated",
    ]
    assert "memory_skipped" in stages
    assert stages[-2:] == ["response_ready", "audit_recorded"]


def test_audit_log_does_not_store_raw_query_or_compressed_context():
    store = baseline_store()
    agent = MemoryAugmentedAgent(store)
    raw_query = "What did we decide about enterprise pilot readiness?"
    result = agent.run(raw_query, top_k=3)
    log_entry = result["log_entry"]
    assert "query" not in log_entry
    assert "compressed_context" not in log_entry
    assert raw_query not in str(log_entry)
    assert log_entry["query_length"] == len(raw_query)


def test_two_session_stores_do_not_share_new_memory():
    baseline = [memory.model_dump() for memory in load_memories_from_json("sample_memories.json")]
    first_store = MemoryStore(memories_from_dicts(baseline), embedding_model=HashingEmbedder())
    second_store = MemoryStore(memories_from_dicts(baseline), embedding_model=HashingEmbedder())
    first_agent = MemoryAugmentedAgent(first_store)
    first_agent.run("Remember that the launch checklist must include a rollback drill.", save_new_memory=True)
    assert len(first_store.memories) == len(second_store.memories) + 1


def test_memory_serialization_round_trip_preserves_content():
    store = baseline_store()
    round_trip = memories_from_dicts(store.to_dicts())
    assert [memory.content for memory in round_trip] == [memory.content for memory in store.memories]


def test_no_memory_response_does_not_invent_context():
    store = MemoryStore([], embedding_model=HashingEmbedder())
    agent = MemoryAugmentedAgent(store)
    result = agent.run("What did we decide?", top_k=3)
    assert "do not have enough remembered project context" in result["agent_response"]
