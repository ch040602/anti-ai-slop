from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


GUARDRAIL_DIRS = [".specify", ".agents", "codex", "docs/process", "docs/references", "checklists", "tools", "specs"]


def copy_missing(source_root: Path, target_root: Path, mode: str) -> list[str]:
    actions: list[str] = []
    for dirname in GUARDRAIL_DIRS:
        source_dir = source_root / dirname
        if not source_dir.exists():
            continue
        for source in source_dir.rglob("*"):
            if not source.is_file():
                continue
            rel = source.relative_to(source_root)
            target = target_root / rel
            if target.exists():
                actions.append(f"skip existing {rel.as_posix()}")
                continue
            actions.append(f"copy {rel.as_posix()}")
            if mode == "merge":
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    return actions


def build_report(source: Path, target: Path, mode: str, actions: list[str]) -> dict[str, object]:
    return {
        "mode": mode,
        "source": str(source),
        "target": str(target),
        "target_exists": target.exists(),
        "changed": mode == "merge" and any(action.startswith("copy ") for action in actions),
        "actions": actions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply anti-ai-slop guardrail files to another repository.")
    parser.add_argument("--source", default=".", help="Pack source root")
    parser.add_argument("--target", required=True, help="Target repository")
    parser.add_argument("--mode", choices=["dry-run", "merge"], default="dry-run")
    parser.add_argument("--json-out", default=None, help="Optional path for a machine-readable apply report")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    target = Path(args.target).resolve()
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"Source is not a directory: {source}")
    if args.mode == "merge" and (not target.exists() or not target.is_dir()):
        raise SystemExit(f"Target is not a directory: {target}")
    if args.mode == "dry-run" and target.exists() and not target.is_dir():
        raise SystemExit(f"Target exists but is not a directory: {target}")
    actions = copy_missing(source, target, args.mode)
    report = build_report(source, target, args.mode, actions)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for action in actions:
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
