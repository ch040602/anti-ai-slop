from __future__ import annotations

import argparse
import importlib
from pathlib import Path

try:
    from .common import SEVERITIES, Finding, json_report, markdown_report, write_or_print
except ImportError:
    from common import SEVERITIES, Finding, json_report, markdown_report, write_or_print


CHECKS = [
    "check_task_traceability",
    "check_spec_coverage",
    "check_glossary_terms",
    "check_architecture_boundaries",
    "check_dependency_justification",
    "check_vague_language",
    "check_placeholders",
]


def load_check(name: str):
    try:
        return importlib.import_module(f"tools.validators.{name}")
    except ModuleNotFoundError:
        return importlib.import_module(name)


def check(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for name in CHECKS:
        module = load_check(name)
        findings.extend(module.check(root))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all anti-ai-slop coherence validators.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    findings = check(Path(args.root).resolve())
    report = json_report(findings) if args.format == "json" else markdown_report(findings, "Anti-AI Slop Coherence Report")
    write_or_print(report, args.out)
    return 1 if any(SEVERITIES[f.severity] >= SEVERITIES["HIGH"] for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
