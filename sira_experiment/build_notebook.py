"""Build the self-contained companion notebook."""

import json
from pathlib import Path

HERE = Path(__file__).parent


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code(source: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "source": source,
            "outputs": [], "execution_count": None}


def strip_module(text: str, drop_lines: list[str]) -> str:
    """Remove the module docstring and any exact lines in drop_lines."""
    if text.startswith('"""'):
        text = text.split('"""', 2)[2].lstrip("\n")
    kept = [ln for ln in text.splitlines()
            if ln.strip() not in {d.strip() for d in drop_lines}]
    return "\n".join(kept).strip() + "\n"


corpus_src = strip_module((HERE / "corpus.py").read_text(), [])

experiment_src = (HERE / "experiment.py").read_text()
experiment_src = strip_module(
    experiment_src,
    ["from corpus import DOCS, QUERIES",
     "import json",
     "from pathlib import Path"],
)
main_marker = 'if __name__ == "__main__":'
assert main_marker in experiment_src
experiment_src = experiment_src.split(main_marker)[0].rstrip() + "\n"

figures_src = (HERE / "figures.py").read_text()
figures_src = strip_module(
    figures_src,
    ["import json",
     "from pathlib import Path",
     "import experiment as E",
     "from corpus import DOCS, QUERIES",
     "import numpy as np"],
)
assert main_marker in figures_src
figures_src = figures_src.split(main_marker)[0].rstrip() + "\n"
replacements = [
    ("E.", ""),
    ('RESULTS = json.loads((Path(__file__).parent / "results.json").read_text())',
     "RESULTS = evaluate()"),
    ('FIG_DIR = Path(__file__).parent / "figures"', 'FIG_DIR = Path("figures")'),
    ('cmp_path = Path(__file__).parent / "results_llm_comparison.json"',
     'cmp_path = FIG_DIR.parent / "results_llm_comparison.json"'),
    ("plt.close(fig)", "plt.show()"),
]
for old, new in replacements:
    assert old in figures_src, old
    figures_src = figures_src.replace(old, new)
figures_src = "import json\nfrom pathlib import Path\n\n" + figures_src

eval_src = '''\
import pandas as pd

results = evaluate()

summary = pd.DataFrame(results["summary"]).T.round(3)
display(summary)

ranks = pd.DataFrame(
    [{"query": r["id"], "kind": r["kind"], **r["ranks"]}
     for r in results["per_query"]]
).set_index("query")
display(ranks)
'''

llm_optional_src = '''\
# OPTIONAL: replace the frozen expansion lists with live LLM output.
# Set ANTHROPIC_API_KEY, run this cell, then rerun the evaluation cells.
#
# import os, anthropic
#
# client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY
#
# PROMPT = (
#     "You are helping a lexical (BM25) search engine. For the user query "
#     "below, list 8-12 single words or short phrases likely to appear "
#     "verbatim in the one document that answers it. Prefer specific, "
#     "discriminative vocabulary (error codes, exact feature names, "
#     "domain terms) over generic synonyms. Return one term per line.\\n\\n"
#     "Query: {query}"
# )
#
# for q in QUERIES:
#     msg = client.messages.create(
#         model="claude-sonnet-4-6",
#         max_tokens=300,
#         messages=[{"role": "user",
#                    "content": PROMPT.format(query=q["query"])}],
#     )
#     q["candidates"] = [t.strip() for t in msg.content[0].text.splitlines()
#                        if t.strip()]
'''

cells = [
    md(
        "# BM25 Gets Its Revenge: When the LLM Should Compile the Query, "
        "Not Run the Search\n\n"
        "Companion notebook for the article. It rebuilds the core intuition "
        "of Meta's **SIRA** ([arXiv:2605.06647](https://arxiv.org/abs/2605.06647)) "
        "on a small test corpus and compares five retrieval systems:\n\n"
        "1. **BM25** - vanilla lexical retrieval\n"
        "2. **Dense** - `all-MiniLM-L6-v2` embeddings, cosine similarity\n"
        "3. **Naive expansion** - BM25 over the query plus corpus-blind synonyms\n"
        "4. **Corpus-aware expansion** - SIRA-style query-side only: candidate "
        "terms filtered by document frequency, then one weighted BM25 call "
        "(does not include offline document enrichment or reranking)\n"
        "5. **Hybrid** - reciprocal rank fusion of (1) and (2)\n\n"
        "Everything runs locally and deterministically. The `candidates` lists "
        "were **hand-authored** (not model-generated) to simulate well-prompted "
        "LLM output; an optional cell at the end regenerates them with a live "
        "model.\n\n"
        "Requirements: `pip install -r requirements.txt`\n\n"
        "Scope: this notebook implements query-side DF-filtered expansion only. "
        "Full SIRA also enriches documents offline at index time."
    ),
    code(
        "# %pip install -r requirements.txt\n"
        "import re\n"
        "import numpy as np\n"
        "from rank_bm25 import BM25Okapi"
    ),
    md(
        "## 1. A small corpus built to break retrievers\n\n"
        "36 documents from a fictional SaaS company's knowledge base, "
        "deliberately seeded with realistic failure modes: exact identifiers "
        "(`ERR-4032`, `v2.14.0`) that embeddings blur together, vocabulary "
        "mismatch (users say *slow*, docs say *latency degradation*), and "
        "confuser documents that share generic vocabulary with the queries.\n\n"
        "Each query has one gold document and two frozen term lists: `naive` "
        "(corpus-blind synonyms) and `candidates` (hand-authored guesses, "
        "validated by document frequency)."
    ),
    code(corpus_src),
    md(
        "## 2. Index, document frequencies, and the five systems\n\n"
        "The tokenizer keeps joined identifiers (`err-4032`, `v2.14.0`, "
        "`max_connections`) as single tokens. That matters for error codes "
        "and version strings.\n\n"
        "The corpus-aware system implements two SIRA query-side mechanics:\n"
        "- **DF filter**: keep a proposed term only if `0 < DF ≤ τ·N` "
        "(it exists in the corpus and is rare enough to carry IDF weight)\n"
        "- **Weighted combination**: `score = BM25(q_orig) + w · BM25(q_exp)` "
        "so expansion terms can never drown out the original query"
    ),
    code(experiment_src),
    md("## 3. Evaluate: MRR, Recall@1, Recall@3, and per-query gold ranks"),
    code(eval_src),
    md(
        "## 4. Figures\n\n"
        "Seven figures: the compiler-vs-loop diagram (dashed box = full SIRA "
        "only), the metric summary, the per-query rank heatmap, the DF-filter "
        "audit for the expansion-trap query, the dense identifier-blur "
        "examples, the BM25 term-weight heatmap for the compiled paraphrase "
        "query, and the hand-authored vs Sonnet 4.6 comparison."
    ),
    code(figures_src + "\nfig_diagram()\nfig_summary()\nfig_rank_heatmap()\n"
         "fig_df_filter()\nfig_dense_failure()\nfig_term_heatmap()\n"
         "fig_llm_comparison()"),
    md(
        "## 5. Optional: live LLM expansion\n\n"
        "Swap the frozen candidate lists for live model output. Results vary "
        "run to run."
    ),
    code(llm_optional_src),
    md(
        "## Takeaways\n\n"
        "- Vanilla BM25 dies on paraphrase (gold rank 14 on the \"slow app\" "
        "query); dense dies on identifiers (ranks the wrong error code and a "
        "performance retro above the gold changelog).\n"
        "- Naive expansion is worse than no expansion (MRR 0.80 vs 0.84).\n"
        "- Hand-authored candidates score 1.000; frozen Sonnet 4.6 candidates "
        "score 0.922 MRR (11/12 at rank 1). The miss is the paraphrase query: "
        "the model guessed `degraded`/`regression`, the corpus says "
        "`latency`/`p95`/`N+1`.\n"
        "- A 36-doc corpus is a teaching instrument, not a benchmark. For real "
        "numbers see SIRA's BEIR results "
        "([arXiv:2605.06647](https://arxiv.org/abs/2605.06647)) and Pi-Serini "
        "([arXiv:2605.10848](https://arxiv.org/abs/2605.10848))."
    ),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3",
                        "language": "python"},
        "language_info": {"name": "python"},
    },
    "cells": cells,
}

out = HERE / "bm25_revenge.ipynb"
out.write_text(json.dumps(nb, indent=1))
print("wrote", out)
