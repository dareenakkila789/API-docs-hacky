# scripts/build.py
import re
from pathlib import Path
import sys

ROOT = Path.cwd()
DOCS_DIR = ROOT / "docs"
DIST_DIR = ROOT / "dist"

INCLUDE_RE = re.compile(r'\{\{\s*include\s*["\'](.+?)["\']\s*\}\}')

def resolve_snippet_path(base_file: Path, snippet_ref: str) -> Path:
    # try relative to the docs file
    candidate = (base_file.parent / snippet_ref).resolve()
    if candidate.exists():
        return candidate
    # try relative to repo root
    candidate = (ROOT / snippet_ref).resolve()
    if candidate.exists():
        return candidate
    return candidate  # final candidate (may not exist)

def process_file(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    def repl(m):
        ref = m.group(1)
        snippet_path = resolve_snippet_path(md_path, ref)
        if snippet_path.exists():
            return snippet_path.read_text(encoding="utf-8")
        else:
            return f"<!-- Missing snippet: {ref} -->"
    return INCLUDE_RE.sub(repl, text)

def build():
    if not DOCS_DIR.exists():
        print("No docs/ folder found. Exiting.", file=sys.stderr)
        sys.exit(1)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    for md in DOCS_DIR.rglob("*.md"):
        rel = md.relative_to(DOCS_DIR)
        out_path = DIST_DIR / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        output = process_file(md)
        out_path.write_text(output, encoding="utf-8")
        print(f"Built: {md} -> {out_path}")

if __name__ == "__main__":
    build()
