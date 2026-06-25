from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


SKIP = {".git", ".codex", "__pycache__", "node_modules", ".venv", "venv"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not any(part in SKIP for part in path.parts):
            yield path


def inventory(root: Path) -> str:
    files = list(iter_files(root))
    suffixes = Counter(path.suffix.lower() or "[none]" for path in files)
    dirs = Counter(path.relative_to(root).parts[0] for path in files if path.relative_to(root).parts)
    lines = [
        "# Existing Code Scan",
        "",
        f"- Root: `{root}`",
        f"- Files: {len(files)}",
        "",
        "## Top Directories",
        "",
    ]
    for name, count in dirs.most_common(20):
        lines.append(f"- `{name}`: {count}")
    lines.extend(["", "## File Types", ""])
    for suffix, count in suffixes.most_common(20):
        lines.append(f"- `{suffix}`: {count}")
    lines.extend(["", "## Priority Files", ""])
    for rel in ["SKILL.md", "README.md", "AGENTS.md", ".specify/memory/constitution.md", "tools/validators/check_all.py"]:
        lines.append(f"- `{rel}`: {'present' if (root / rel).exists() else 'missing'}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a compact repository inventory.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    text = inventory(Path(args.root).resolve())
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
