"""Build article_bm25_revenge.html from article_bm25_revenge.md."""

from pathlib import Path

try:
    import markdown
except ImportError:
    raise SystemExit("pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "article_bm25_revenge.md"
OUT = ROOT / "article_bm25_revenge.html"

CSS = """
  body { font-family: Georgia, 'Times New Roman', serif; color: #1f2430;
         max-width: 740px; margin: 3em auto; padding: 0 1.2em;
         line-height: 1.65; font-size: 19px; }
  h1 { font-size: 2.1em; line-height: 1.2; }
  h2 { margin-top: 1.6em; }
  h3 { color: #555; font-weight: 500; font-style: italic; }
  img { max-width: 100%; border: 1px solid #eee; border-radius: 6px;
        margin: 1em 0; }
  table { border-collapse: collapse; margin: 1.2em 0; font-size: 0.9em; }
  th, td { border: 1px solid #ddd; padding: 0.5em 0.9em; text-align: left; }
  th { background: #f6f8fa; }
  code { font-family: Menlo, monospace; font-size: 0.82em;
         background: #f4f5f7; padding: 0.1em 0.35em; border-radius: 4px; }
  a { color: #3567b3; }
  hr { border: none; border-top: 1px solid #ddd; margin: 2.2em 0; }
  em.caption { display: block; font-size: 0.88em; color: #555; margin-top: -0.6em; }
"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BM25 Gets Its Revenge</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> None:
    text = MD.read_text()
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    OUT.write_text(HTML.format(css=CSS, body=body))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
