import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

from memory_policy import evaluate_memory_write
from memory_store import MemoryStore, load_memories_from_json


ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = json.loads((ROOT / "eval" / "cases.json").read_text(encoding="utf-8"))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    store = MemoryStore(load_memories_from_json(ROOT / "sample_memories.json"), embedding_model=model)

    retrieval_rows = []
    retrieval_failures = []
    reciprocal_ranks = []

    for case in cases["retrieval_cases"]:
        results = store.retrieve(case["query"], top_k=3)
        ranked_ids = [item.memory.memory_id for item in results]
        try:
            rank = ranked_ids.index(case["expected_memory_id"]) + 1
            reciprocal_rank = 1.0 / rank
        except ValueError:
            rank = None
            reciprocal_rank = 0.0
            retrieval_failures.append(case["query"])

        reciprocal_ranks.append(reciprocal_rank)
        retrieval_rows.append(
            {
                "query": case["query"],
                "expected_memory": case["expected_memory_id"],
                "retrieved": ranked_ids,
                "rank": rank,
            }
        )

    policy_rows = []
    policy_failures = []
    for case in cases["write_policy_cases"]:
        decision = evaluate_memory_write(case["query"])
        passed = decision.outcome == case["expected_outcome"]
        policy_rows.append(
            {
                "query": case["query"],
                "expected": case["expected_outcome"],
                "actual": decision.outcome,
                "passed": passed,
            }
        )
        if not passed:
            policy_failures.append(case["query"])

    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
    hit_at_3 = 1.0 - (len(retrieval_failures) / len(cases["retrieval_cases"]))

    print("Memory retrieval evaluation:")
    for row in retrieval_rows:
        print(row)

    print("\nMemory write-policy evaluation:")
    for row in policy_rows:
        print(row)

    print("\nSummary:")
    print({
        "retrieval_cases": len(retrieval_rows),
        "hit_at_3": round(hit_at_3, 3),
        "mrr": round(mrr, 3),
        "write_policy_passed": len(policy_rows) - len(policy_failures),
        "write_policy_cases": len(policy_rows),
    })

    if retrieval_failures or mrr < 0.75 or policy_failures:
        if retrieval_failures:
            print(f"Retrieval failures: {retrieval_failures}", file=sys.stderr)
        if mrr < 0.75:
            print(f"MRR below required threshold: {mrr:.3f}", file=sys.stderr)
        if policy_failures:
            print(f"Write-policy failures: {policy_failures}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
