"""Generate the article figures."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

import experiment as E
from corpus import DOCS, QUERIES

FIG_DIR = Path(__file__).parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

INK = "#1f2430"
BLUE = "#3567b3"
ORANGE = "#e07b39"
GREEN = "#2e8b57"
RED = "#c0392b"
GREY = "#9aa3ad"

RESULTS = json.loads((Path(__file__).parent / "results.json").read_text())
SYSTEM_NAMES = list(RESULTS["summary"].keys())


def _box(ax, x, y, w, h, text, fc="#eef2f8", ec=BLUE, fs=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=INK, weight=weight)


def _arrow(ax, xy_from, xy_to, color=INK, style="-|>", conn="arc3,rad=0.0"):
    ax.add_patch(FancyArrowPatch(xy_from, xy_to, arrowstyle=style,
                                 mutation_scale=14, color=color, lw=1.6,
                                 connectionstyle=conn))


def fig_diagram():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

    # Left: agentic loop
    ax = axes[0]
    ax.set_title("Agentic retrieval: the LLM searches more",
                 fontsize=12.5, weight="bold", color=INK, pad=14)
    _box(ax, 0.05, 0.72, 0.28, 0.16, "Query", fc="#fdf3ec", ec=ORANGE)
    _box(ax, 0.36, 0.42, 0.30, 0.18, "LLM agent\n(plan / reflect)", weight="bold")
    _box(ax, 0.05, 0.12, 0.28, 0.16, "Search tool")
    _box(ax, 0.70, 0.12, 0.26, 0.16, "Read / open\ndocs")
    _box(ax, 0.70, 0.72, 0.26, 0.16, "Answer", fc="#edf6ef", ec=GREEN)
    _arrow(ax, (0.26, 0.72), (0.42, 0.60))
    _arrow(ax, (0.42, 0.44), (0.24, 0.28), conn="arc3,rad=0.15")
    _arrow(ax, (0.30, 0.20), (0.44, 0.42), conn="arc3,rad=0.15")
    _arrow(ax, (0.60, 0.44), (0.78, 0.28), conn="arc3,rad=-0.15")
    _arrow(ax, (0.74, 0.24), (0.58, 0.42), conn="arc3,rad=-0.15")
    _arrow(ax, (0.62, 0.56), (0.74, 0.71))
    ax.text(0.51, 0.10, "iterate 3–10×\n(latency & cost multiply)",
            ha="center", fontsize=9.5, color=RED, style="italic")

    # Right: query-side compiler (this experiment)
    ax = axes[1]
    ax.set_title("Query compiler (this experiment): search once, but better",
                 fontsize=12.5, weight="bold", color=INK, pad=14)
    _box(ax, 0.03, 0.72, 0.22, 0.16, "Query", fc="#fdf3ec", ec=ORANGE)
    _box(ax, 0.30, 0.68, 0.34, 0.24,
         "Predict evidence terms\n(hand-authored or LLM)", weight="bold")
    _box(ax, 0.30, 0.36, 0.34, 0.18, "DF filter\n(corpus statistics)")
    _box(ax, 0.30, 0.06, 0.34, 0.18, "One weighted\nBM25 call")
    _box(ax, 0.72, 0.06, 0.24, 0.18, "Answer", fc="#edf6ef", ec=GREEN)
    # Full SIRA enriches docs offline; not part of this experiment (dashed, no arrow).
    _box(ax, 0.03, 0.36, 0.22, 0.18, "Docs enriched\noffline (LLM)\n[full SIRA only]",
         fc="#f4f0fa", ec="#7d5ba6", fs=8.5, weight="normal")
    ax.add_patch(FancyBboxPatch((0.02, 0.34), 0.24, 0.22, boxstyle="round,pad=0.012",
                                fc="none", ec="#7d5ba6", lw=1.2, ls="--"))
    _arrow(ax, (0.25, 0.80), (0.32, 0.80))
    _arrow(ax, (0.47, 0.68), (0.47, 0.55))
    _arrow(ax, (0.47, 0.36), (0.47, 0.25))
    _arrow(ax, (0.64, 0.15), (0.73, 0.15))
    ax.text(0.67, 0.30, "drop absent &\nlow-IDF terms", ha="left",
            fontsize=8.5, color=GREY, style="italic")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_compiler_vs_loop.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def fig_summary():
    metrics = ["MRR", "Recall@1", "Recall@3"]
    colors = [GREY, BLUE, RED, GREEN, ORANGE]
    x = np.arange(len(metrics))
    width = 0.16

    fig, ax = plt.subplots(figsize=(9, 4.4))
    for i, name in enumerate(SYSTEM_NAMES):
        vals = [RESULTS["summary"][name][m] for m in metrics]
        bars = ax.bar(x + (i - 2) * width, vals, width, label=name,
                      color=colors[i], edgecolor="white")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.2f}",
                    ha="center", fontsize=8, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11.5)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("score")
    ax.set_title("Five retrieval systems, 12 queries across 4 regimes, "
                 "36-doc toy corpus", fontsize=12.5, weight="bold", color=INK)
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="lower center",
              bbox_to_anchor=(0.5, -0.32))
    fig.savefig(FIG_DIR / "fig2_summary.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_rank_heatmap():
    per_q = RESULTS["per_query"]
    ranks = np.array([[r["ranks"][s] for s in SYSTEM_NAMES] for r in per_q])
    # color by capped rank: 1 good (green) -> bad (red)
    capped = np.minimum(ranks, 6)

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    im = ax.imshow(capped, cmap="RdYlGn_r", vmin=1, vmax=6, aspect="auto")
    for i in range(ranks.shape[0]):
        for j in range(ranks.shape[1]):
            ax.text(j, i, str(ranks[i, j]), ha="center", va="center",
                    fontsize=10.5, weight="bold",
                    color=INK if capped[i, j] < 4 else "white")
    ax.set_xticks(range(len(SYSTEM_NAMES)))
    ax.set_xticklabels([s.replace(" expansion", "\nexpansion")
                        .replace(" (", "\n(") for s in SYSTEM_NAMES],
                       fontsize=9.5)
    labels = [f"{r['id'].split('-', 1)[1]}  ·  {r['kind']}" for r in per_q]
    ax.set_yticks(range(len(per_q)))
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_title("Rank of the gold document (1 = retrieved first)",
                 fontsize=12.5, weight="bold", color=INK, pad=12)
    fig.colorbar(im, ax=ax, shrink=0.6, label="rank (capped at 6)")
    fig.savefig(FIG_DIR / "fig3_rank_heatmap.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def fig_df_filter():
    q = next(x for x in QUERIES if x["id"] == "q9-2fa-reset")
    _, audit = E.filter_candidates(q["candidates"])
    terms = [a["term"] for a in audit]
    dfs = [a["df"] for a in audit]
    kept = [a["verdict"] == "kept" for a in audit]
    colors = [GREEN if k else RED for k in kept]
    cutoff = E.DF_TAU * E.N_DOCS

    fig, ax = plt.subplots(figsize=(9, 4.6))
    y = np.arange(len(terms))
    ax.barh(y, dfs, color=colors, edgecolor="white", height=0.62)
    for yi, (df, k, a) in enumerate(zip(dfs, kept, audit)):
        note = "" if k else ("  ✗ " + a["verdict"].split("(")[1].rstrip(")"))
        ax.text(df + 0.08, yi, f"{df}{note}", va="center", fontsize=9.5,
                color=INK)
    ax.axvline(cutoff, color=INK, ls="--", lw=1.2)
    ax.text(cutoff + 0.05, len(terms) - 0.4,
            f"DF cutoff = {E.DF_TAU:.0%} of corpus", fontsize=9, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(terms, fontsize=10.5, family="monospace")
    ax.invert_yaxis()
    ax.set_xlabel("document frequency (of 36 docs)")
    ax.set_title('Compiling the query  "reset 2FA for a locked out user"\n'
                 "candidate terms (hand-authored), validated against corpus statistics",
                 fontsize=12, weight="bold", color=INK)
    handles = [mpatches.Patch(color=GREEN, label="kept"),
               mpatches.Patch(color=RED, label="dropped")]
    ax.legend(handles=handles, frameon=False, loc="lower right")
    fig.savefig(FIG_DIR / "fig4_df_filter.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_dense_failure():
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))

    cases = [
        ("q1-error-code", ["pay-err-4032", "pay-err-4031", "pay-general",
                           "pay-retry-policy"],
         '"payment failed with error ERR-4032"'),
        ("q8-version", ["perf-regression", "changelog-2-14", "changelog-2-15",
                        "changelog-2-13"],
         '"what changed in v2.14.0"'),
    ]
    for ax, (qid, doc_ids, title) in zip(axes, cases):
        q = next(x for x in QUERIES if x["id"] == qid)
        dense = E.run_dense(q)
        bm25 = E.run_bm25(q)
        bm25 = bm25 / (bm25.max() or 1)          # normalise for display
        idx = [E.DOC_IDS.index(d) for d in doc_ids]
        y = np.arange(len(doc_ids))
        ax.barh(y - 0.18, [dense[i] for i in idx], height=0.34,
                color=BLUE, label="dense cosine")
        ax.barh(y + 0.18, [bm25[i] for i in idx], height=0.34,
                color=ORANGE, label="BM25 (normalized)")
        labels = [(d + "  ★ gold" if d == q["gold"] else d) for d in doc_ids]
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=10, family="monospace")
        ax.invert_yaxis()
        ax.set_title(title, fontsize=11.5, weight="bold", color=INK)
        ax.set_xlim(0, 1.05)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=10, ncol=2,
               loc="lower center", bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Where embeddings blur: sibling identifiers and nearby "
                 "release context", fontsize=12.5, weight="bold", color=INK, y=1.08)
    fig.text(0.5, 0.99, "BM25 normalized to max = 1; cosine shown raw. "
             "Compare rank order within each method, not magnitude across "
             "methods.", ha="center", fontsize=9.5, color=GREY,
             style="italic")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig5_dense_failure.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


STOPWORDS = {"is", "the", "after", "a", "an", "of", "to", "in", "for", "on",
             "with", "at", "really", "last", "and", "or", "my", "do", "how"}


def fig_term_heatmap():
    q = next(x for x in QUERIES if x["id"] == "q3-slow-app")
    orig_terms = [t for t in E.tokenize(q["query"])
                  if E.DF.get(t, 0) > 0 and t not in STOPWORDS]
    kept, _ = E.filter_candidates(q["candidates"])
    exp_terms = [t for t in dict.fromkeys(kept) if t not in orig_terms]
    terms = orig_terms + exp_terms

    doc_ids = ["perf-regression", "changelog-2-14", "pg-tuning",
               "pay-retry-policy", "redis-cache"]
    idx = [E.DOC_IDS.index(d) for d in doc_ids]
    mat = np.array([[E.bm25_scores([t])[i] for i in idx] for t in terms])

    fig, ax = plt.subplots(figsize=(8.6, 5.8))
    im = ax.imshow(mat, cmap="Blues", aspect="auto")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if v > 0.01:
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        fontsize=9, color="white" if v > mat.max() * 0.6
                        else INK)
    ax.set_xticks(range(len(doc_ids)))
    ax.set_xticklabels([d + ("\n★ gold" if d == q["gold"] else "")
                        for d in doc_ids], fontsize=9.5)
    ax.set_yticks(range(len(terms)))
    ax.set_yticklabels(terms, fontsize=10, family="monospace")
    for spine in ax.spines.values():
        spine.set_visible(False)
    n_orig = len(orig_terms)
    ax.axhline(n_orig - 0.5, color=ORANGE, lw=2)
    ax.text(len(doc_ids) - 0.4, n_orig - 0.68, "original query terms ↑",
            ha="right", fontsize=9, color=ORANGE, style="italic")
    ax.text(len(doc_ids) - 0.4, n_orig - 0.28, "compiled expansion terms ↓",
            ha="right", fontsize=9, color=GREEN, style="italic")
    ax.set_title('BM25 term-weight heatmap: "app is really slow after the '
                 'last update"\nper-term score contribution by document '
                 "(stopword and out-of-vocabulary rows omitted)",
                 fontsize=11.5, weight="bold", color=INK, pad=12)
    ax.set_xlabel("omitted rows: stopwords (near-zero IDF) and query terms "
                  "absent from the corpus, e.g. 'app', 'update' (zero "
                  "contribution everywhere)", fontsize=8.5,
                  color=GREY, style="italic")
    fig.colorbar(im, ax=ax, shrink=0.7, label="BM25 contribution")
    fig.savefig(FIG_DIR / "fig6_term_heatmap.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def fig_llm_comparison():
    """Hand-authored vs frozen Sonnet 4.6 corpus-aware expansion."""
    cmp_path = Path(__file__).parent / "results_llm_comparison.json"
    if not cmp_path.exists():
        return
    cmp = json.loads(cmp_path.read_text())
    hand = cmp["hand_authored"]
    llm = cmp["llm_generated"]
    metrics = ["MRR", "Recall@1", "Recall@3"]
    labels = ["Hand-authored\n(upper bound)",
              "Claude Sonnet 4.6\n(frozen run)"]
    colors = [GREEN, BLUE]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    x = np.arange(len(metrics))
    width = 0.34
    for i, (label, data, color) in enumerate(zip(labels, [hand, llm], colors)):
        vals = [data[m] for m in metrics]
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, vals, width, label=label, color=color,
                      edgecolor="white")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.2f}",
                    ha="center", fontsize=9, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11.5)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("score")
    ax.set_title("Corpus-aware expansion: hand-authored vs real LLM candidates",
                 fontsize=12, weight="bold", color=INK)
    ax.legend(frameon=False, fontsize=9, loc="upper center",
              bbox_to_anchor=(0.5, -0.12), ncol=2)
    ax.text(0.5, -0.30, "Same DF filter and weighted BM25; only the candidate "
            "source differs. Sonnet misses 1/12 queries (paraphrase).",
            transform=ax.transAxes, fontsize=8.5, color=GREY, style="italic",
            ha="center")
    fig.savefig(FIG_DIR / "fig7_llm_comparison.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_diagram()
    fig_summary()
    fig_rank_heatmap()
    fig_df_filter()
    fig_dense_failure()
    fig_term_heatmap()
    fig_llm_comparison()
    print("figures written to", FIG_DIR)
