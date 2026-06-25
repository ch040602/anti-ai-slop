from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.validators import check_architecture_boundaries
from tools.validators import check_all
from tools.validators import check_dependency_justification
from tools.validators import check_glossary_terms


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def test_traceability_finds_missing_requirement_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".specify/memory/constitution.md", "# Constitution\n")
            write(root / ".specify/memory/glossary.md", "| Term | Meaning |\n|---|---|\n| AI slop | Quality failure |\n| AI-smell risk | Risk |\n| output contract | Contract |\n| evidence-to-revision | Trace |\n")
            write(root / ".specify/memory/architecture-principles.md", "tools/validators/\n.specify/\ncodex/prompts/\n.agents/skills/\ndocs/process/\n")
            write(root / ".specify/memory/product-principles.md", "# Product\n")
            write(root / "codex/prompts/00-apply-pack-to-existing-repo.md", "# Apply\n")
            write(root / "codex/prompts/01-run-coherence-check.md", "# Check\n")
            write(root / "codex/prompts/02-pr-review.md", "# Review\n")
            write(root / "specs/demo/spec.md", "# Spec\n\n- FR-001: Do a thing.\n\n## Out of Scope\n\n- None.\n")
            write(root / "specs/demo/plan.md", "# Plan\n")
            write(root / "specs/demo/tasks.md", "# Tasks\n\n- [ ] T001 Missing reference.\n")
            findings = check_all.check(root)
            self.assertTrue(any(f.rule == "task-traceability" and f.severity == "HIGH" for f in findings))

    def test_dependency_checker_treats_future_and_importlib_as_stdlib(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "tools/demo.py", "from __future__ import annotations\nimport importlib\nimport json\n")
            findings = check_dependency_justification.check(root)
            self.assertEqual([], [f for f in findings if f.severity == "HIGH"])

    def test_architecture_checker_does_not_flag_read_only_string_literals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".specify/memory/architecture-principles.md", "tools/validators/\n.specify/\ncodex/prompts/\n.agents/skills/\ndocs/process/\n")
            write(root / "tools/validators/demo.py", "MUTATION_TOKENS = ['write_text(', 'unlink(']\n")
            findings = check_architecture_boundaries.check(root)
            self.assertEqual([], [f for f in findings if f.severity == "HIGH"])

    def test_glossary_checker_normalizes_required_term_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".specify/memory/glossary.md", "| Term | Meaning |\n|---|---|\n| AI slop | Quality failure |\n| AI-smell risk | Risk |\n| Output contract | Contract |\n| Evidence-to-revision | Trace |\n")
            findings = check_glossary_terms.check(root)
            self.assertEqual([], [f for f in findings if f.rule == "glossary-terms" and "misses required" in f.message])


if __name__ == "__main__":
    unittest.main()
