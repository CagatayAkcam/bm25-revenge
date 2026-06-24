"""Compare hand-authored vs frozen LLM candidate lists."""

import json
from copy import deepcopy
from pathlib import Path

import numpy as np

from corpus import QUERIES
from experiment import SYSTEMS, evaluate, ranks_from_scores, run_sira_expansion

LLM_PATH = Path(__file__).parent / "llm_candidates.json"


def main() -> None:
    if not LLM_PATH.exists():
        raise SystemExit(f"Missing {LLM_PATH}; run generate_candidates.py first")

    llm = {row["id"]: row["candidates"]
           for row in json.loads(LLM_PATH.read_text())["queries"]}

    llm_queries = deepcopy(QUERIES)
    for q in llm_queries:
        q["candidates_llm"] = llm[q["id"]]

    hand_results = evaluate()

    def sira_llm(q: dict) -> np.ndarray:
        return run_sira_expansion({**q, "candidates": q["candidates_llm"]})

    llm_per_query = []
    for q in llm_queries:
        ranks = ranks_from_scores(sira_llm(q))
        llm_per_query.append({
            "id": q["id"],
            "gold": q["gold"],
            "candidates_llm": q["candidates_llm"],
            "llm_rank": ranks[q["gold"]],
        })

    llm_ranks = np.array([r["llm_rank"] for r in llm_per_query])
    llm_summary = {
        "MRR": float(np.mean(1.0 / llm_ranks)),
        "Recall@1": float(np.mean(llm_ranks == 1)),
        "Recall@3": float(np.mean(llm_ranks <= 3)),
    }

    hand_sira = hand_results["summary"]["Corpus-aware expansion"]
    print("Corpus-aware expansion, hand-authored candidates:")
    print(f"  MRR={hand_sira['MRR']:.3f}  R@1={hand_sira['Recall@1']:.2f}  "
          f"R@3={hand_sira['Recall@3']:.2f}")
    print("Corpus-aware expansion, LLM-generated candidates:")
    print(f"  MRR={llm_summary['MRR']:.3f}  R@1={llm_summary['Recall@1']:.2f}  "
          f"R@3={llm_summary['Recall@3']:.2f}")

    print("\nPer-query gold rank (corpus-aware only):")
    print(f"{'query':<18} {'hand':>6} {'llm':>6}")
    for hand_row, llm_row in zip(hand_results["per_query"], llm_per_query):
        h = hand_row["ranks"]["Corpus-aware expansion"]
        l = llm_row["llm_rank"]
        flag = "  <--" if h != l else ""
        print(f"{hand_row['id']:<18} {h:>6} {l:>6}{flag}")

    out = Path(__file__).parent / "results_llm_comparison.json"
    out.write_text(json.dumps({
        "hand_authored": hand_sira,
        "llm_generated": llm_summary,
        "per_query": [
            {
                "id": h["id"],
                "hand_rank": h["ranks"]["Corpus-aware expansion"],
                "llm_rank": l["llm_rank"],
                "llm_candidates": l["candidates_llm"],
            }
            for h, l in zip(hand_results["per_query"], llm_per_query)
        ],
    }, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
