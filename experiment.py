"""Compare five retrieval systems on the toy corpus."""

import json
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from corpus import DOCS, QUERIES

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_.+][a-z0-9]+)*")

DF_TAU = 0.1          # expansion terms must appear in <= 10% of docs
EXPANSION_WEIGHT = 0.5  # w in score = BM25(q_orig) + w * BM25(q_exp)
RRF_K = 60


def tokenize(text: str) -> list[str]:
    """Lowercase tokens; keeps joined identifiers like err-4032, v2.14.0."""
    return TOKEN_RE.findall(text.lower())


DOC_IDS = list(DOCS.keys())
DOC_TOKENS = [tokenize(DOCS[d]) for d in DOC_IDS]
N_DOCS = len(DOC_IDS)

BM25_INDEX = BM25Okapi(DOC_TOKENS)

DF = {}
for toks in DOC_TOKENS:
    for t in set(toks):
        DF[t] = DF.get(t, 0) + 1


def bm25_scores(tokens: list[str]) -> np.ndarray:
    return np.asarray(BM25_INDEX.get_scores(tokens))


def ranks_from_scores(scores: np.ndarray) -> dict[str, int]:
    """doc id -> 1-based rank (stable for ties)."""
    order = np.argsort(-scores, kind="stable")
    return {DOC_IDS[i]: r + 1 for r, i in enumerate(order)}


def run_bm25(q: dict) -> np.ndarray:
    return bm25_scores(tokenize(q["query"]))


_DENSE = None
_DOC_EMB = None


def _dense_model():
    global _DENSE, _DOC_EMB
    if _DENSE is None:
        from sentence_transformers import SentenceTransformer
        _DENSE = SentenceTransformer("all-MiniLM-L6-v2")
        _DOC_EMB = _DENSE.encode(
            [DOCS[d] for d in DOC_IDS], normalize_embeddings=True
        )
    return _DENSE, _DOC_EMB


def run_dense(q: dict) -> np.ndarray:
    model, doc_emb = _dense_model()
    q_emb = model.encode([q["query"]], normalize_embeddings=True)
    return (doc_emb @ q_emb.T).ravel()


def run_naive_expansion(q: dict) -> np.ndarray:
    """Append corpus-blind synonyms to the query, single BM25 call."""
    expanded = tokenize(q["query"]) + [t for s in q["naive"] for t in tokenize(s)]
    return bm25_scores(expanded)


def filter_candidates(candidates: list[str]) -> tuple[list[str], list[dict]]:
    """SIRA-style DF filter: keep terms with 0 < DF <= tau * N."""
    kept, audit = [], []
    max_df = DF_TAU * N_DOCS
    for term in candidates:
        toks = tokenize(term)
        for t in toks:
            df = DF.get(t, 0)
            if df == 0:
                verdict = "dropped (not in corpus)"
            elif df > max_df:
                verdict = "dropped (too common)"
            else:
                verdict = "kept"
                kept.append(t)
            audit.append({"term": t, "df": df, "verdict": verdict})
    return kept, audit


def run_sira_expansion(q: dict) -> np.ndarray:
    kept, _ = filter_candidates(q["candidates"])
    score = bm25_scores(tokenize(q["query"]))
    if kept:
        score = score + EXPANSION_WEIGHT * bm25_scores(kept)
    return score


def run_hybrid(q: dict) -> np.ndarray:
    """Reciprocal rank fusion of vanilla BM25 and dense."""
    fused = np.zeros(N_DOCS)
    for scores in (run_bm25(q), run_dense(q)):
        order = np.argsort(-scores, kind="stable")
        for rank, i in enumerate(order):
            fused[i] += 1.0 / (RRF_K + rank + 1)
    return fused


SYSTEMS = {
    "BM25": run_bm25,
    "Dense (MiniLM)": run_dense,
    "Naive expansion": run_naive_expansion,
    "Corpus-aware expansion": run_sira_expansion,
    "Hybrid (RRF)": run_hybrid,
}


def evaluate() -> dict:
    per_query = []
    for q in QUERIES:
        row = {"id": q["id"], "query": q["query"], "kind": q["kind"],
               "gold": q["gold"], "ranks": {}}
        for name, fn in SYSTEMS.items():
            ranks = ranks_from_scores(fn(q))
            row["ranks"][name] = ranks[q["gold"]]
        per_query.append(row)

    summary = {}
    for name in SYSTEMS:
        gold_ranks = np.array([r["ranks"][name] for r in per_query])
        summary[name] = {
            "MRR": float(np.mean(1.0 / gold_ranks)),
            "Recall@1": float(np.mean(gold_ranks == 1)),
            "Recall@3": float(np.mean(gold_ranks <= 3)),
        }
    return {"per_query": per_query, "summary": summary}


if __name__ == "__main__":
    results = evaluate()

    name_w = max(len(n) for n in SYSTEMS) + 2
    print(f"{'system':<{name_w}} {'MRR':>6} {'R@1':>6} {'R@3':>6}")
    for name, m in results["summary"].items():
        print(f"{name:<{name_w}} {m['MRR']:>6.3f} {m['Recall@1']:>6.2f} "
              f"{m['Recall@3']:>6.2f}")

    print("\nGold-document rank per query (1 = best):")
    print(f"{'query':<18} {'kind':<20}" + "".join(f"{n[:14]:>16}" for n in SYSTEMS))
    for row in results["per_query"]:
        print(f"{row['id']:<18} {row['kind']:<20}"
              + "".join(f"{row['ranks'][n]:>16}" for n in SYSTEMS))

    out = Path(__file__).parent / "results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")
