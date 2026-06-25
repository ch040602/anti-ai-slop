from __future__ import annotations

import re
from pathlib import Path

try:
    from .common import Finding, extract_ids, read_text, relpath, repo_path, run_cli
except ImportError:
    from common import Finding, extract_ids, read_text, relpath, repo_path, run_cli


TASK_RE = re.compile(r"\bT\d{3,}\b")


def check(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for tasks_path in root.glob("specs/*/tasks.md"):
        text = read_text(tasks_path)
        spec_path = tasks_path.parent / "spec.md"
        spec_text = read_text(spec_path) if spec_path.exists() else ""
        spec_reqs = extract_ids(spec_text, "FR")
        task_lines = [line for line in text.splitlines() if TASK_RE.search(line)]
        if not spec_path.exists():
            findings.append(Finding("HIGH", "task-traceability", relpath(tasks_path, root), "tasks.md has no sibling spec.md.", "Add spec.md with FR-* requirements."))
            continue
        for line in task_lines:
            task_id = TASK_RE.search(line).group(0)
            refs = extract_ids(line, "FR")
            if not refs:
                findings.append(Finding("HIGH", "task-traceability", relpath(tasks_path, root), f"{task_id} does not reference an FR-* requirement.", "Add an FR-* reference in the traceability table or task line.", line.strip()))
            missing = refs - spec_reqs
            if missing:
                findings.append(Finding("HIGH", "task-traceability", relpath(tasks_path, root), f"{task_id} references missing requirements: {', '.join(sorted(missing))}.", "Define the requirement in spec.md or correct the task reference.", line.strip()))
        if not task_lines:
            findings.append(Finding("MEDIUM", "task-traceability", relpath(tasks_path, root), "tasks.md contains no T### tasks.", "Add traceable T### task IDs."))
    if not list(root.glob("specs/*/tasks.md")):
        findings.append(Finding("MEDIUM", "task-traceability", "specs/", "No feature tasks.md files found.", "Add specs/<feature>/tasks.md for traceable implementation work."))
    return findings


if __name__ == "__main__":
    raise SystemExit(run_cli(check, "Task Traceability Check"))
