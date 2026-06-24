"""One-shot LLM candidate generation. Saves frozen output to llm_candidates.json.

Usage:
    export ANTHROPIC_API_KEY=...
    python generate_candidates.py

Does not overwrite an existing file unless --force is passed.
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from corpus import QUERIES

PROMPT = (
    "You are helping a lexical (BM25) search engine. For the user query "
    "below, list 8-12 single words or short phrases likely to appear "
    "verbatim in the one document that answers it. Prefer specific, "
    "discriminative vocabulary (error codes, exact feature names, "
    "domain terms) over generic synonyms. Return one term per line.\n\n"
    "Query: {query}"
)

MODEL = "claude-sonnet-4-6"
OUT = Path(__file__).parent / "llm_candidates.json"


def parse_terms(text: str) -> list[str]:
    terms = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*•\d.)]+\s*", "", line)
        line = line.strip("`\"' ")
        if line:
            terms.append(line)
    return terms


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing llm_candidates.json")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args()

    if OUT.exists() and not args.force:
        print(f"{OUT} already exists; use --force to regenerate")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY")

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    rows = []

    for q in QUERIES:
        msg = client.messages.create(
            model=args.model,
            max_tokens=300,
            messages=[{"role": "user", "content": PROMPT.format(query=q["query"])}],
        )
        raw = msg.content[0].text
        terms = parse_terms(raw)
        rows.append({
            "id": q["id"],
            "query": q["query"],
            "candidates": terms,
            "raw_response": raw,
        })
        print(f"{q['id']}: {len(terms)} terms")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "prompt": PROMPT,
        "queries": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
