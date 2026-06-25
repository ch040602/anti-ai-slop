from __future__ import annotations

import tempfile
import subprocess
import sys
import unittest
from importlib import import_module
from pathlib import Path

from tools.validators import check_architecture_boundaries
from tools.validators import check_all
from tools.validators import check_dependency_justification
from tools.validators import check_glossary_terms
from tools.validators import check_task_traceability


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
            write(root / "tools/demo.py", "from __future__ import annotations\nimport importlib\nimport json\nimport traceback\n")
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

    def test_check_all_reports_checker_crashes_as_critical_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original_checks = check_all.CHECKS
            check_all.CHECKS = ["validator_that_does_not_exist"]
            try:
                findings = check_all.check(root)
            finally:
                check_all.CHECKS = original_checks

            self.assertTrue(
                any(
                    f.rule == "CHECK_CRASH"
                    and f.severity == "CRITICAL"
                    and "validator_that_does_not_exist" in f.message
                    for f in findings
                )
            )

    def test_check_all_reports_invalid_guardrails_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "config/guardrails.json", "{bad json")
            findings = check_all.check(root)
            self.assertTrue(
                any(
                    f.rule == "config-integrity"
                    and f.severity == "CRITICAL"
                    and "guardrails.json" in f.path
                    for f in findings
                )
            )

    def test_task_traceability_ignores_fenced_task_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "specs/demo/spec.md", "# Spec\n\n- FR-001: Do a thing.\n\n## Out of Scope\n\n- None.\n")
            write(
                root / "specs/demo/tasks.md",
                "# Tasks\n\n"
                "```md\n"
                "- T001 Improve dashboard\n"
                "- T002 Refactor backend\n"
                "```\n\n"
                "- [ ] T003 [FR-001] Implement the thing.\n",
            )
            findings = check_task_traceability.check(root)
            self.assertEqual([], [f for f in findings if f.severity == "HIGH"])

    def test_bootstrap_feature_replaces_path_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".specify/templates/overrides/spec-template.md",
                "Feature: [FEATURE NAME]\nPath: specs/[###-feature-name]/spec.md\nFiles: specs/[feature]/evidence/scan.md\n",
            )
            bootstrap_feature = import_module("tools.bootstrap_feature")
            created = bootstrap_feature.bootstrap(root, "123-demo-feature", "Demo Feature", "Ship the demo")

            spec_text = (root / "specs/123-demo-feature/spec.md").read_text(encoding="utf-8")
            self.assertIn(root / "specs/123-demo-feature/spec.md", created)
            self.assertNotIn("[###-feature-name]", spec_text)
            self.assertNotIn("[feature]", spec_text)
            self.assertIn("specs/123-demo-feature/spec.md", spec_text)
            self.assertIn("specs/123-demo-feature/evidence/scan.md", spec_text)

    def test_template_token_checker_flags_shipped_template_tokens_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".specify/templates/overrides/spec-template.md", "Path: specs/[###-feature-name]/spec.md\n")
            write(root / "specs/demo/spec.md", "Path: specs/[###-feature-name]/spec.md\n")
            check_template_tokens = import_module("tools.validators.check_template_tokens")

            findings = check_template_tokens.check(root)
            self.assertEqual(["specs/demo/spec.md"], [f.path for f in findings])
            self.assertTrue(all(f.rule == "template-tokens" and f.severity == "HIGH" for f in findings))

    def test_evidence_link_checker_flags_missing_paths_and_allows_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "specs/demo/tasks.md",
                "# Tasks\n\n"
                "- [x] T001 [FR-001] Done. Evidence: `specs/demo/evidence/missing.md`\n"
                "- [ ] T002 [FR-001] Later. Evidence: Pending until implementation\n",
            )
            check_evidence_links = import_module("tools.validators.check_evidence_links")

            findings = check_evidence_links.check(root)
            self.assertEqual(1, len(findings))
            self.assertEqual("evidence-links", findings[0].rule)
            self.assertEqual("HIGH", findings[0].severity)
            self.assertIn("missing.md", findings[0].message)

    def test_security_workflows_use_current_examples(self) -> None:
        root = Path(__file__).resolve().parents[1]
        codeql = (root / ".github/workflows/codeql.yml").read_text(encoding="utf-8")
        gitleaks = (root / ".github/workflows/gitleaks.yml").read_text(encoding="utf-8")
        semgrep = (root / ".github/workflows/semgrep.yml").read_text(encoding="utf-8")
        osv = (root / ".github/workflows/osv-scanner.yml").read_text(encoding="utf-8")

        self.assertIn("github/codeql-action/init@v4", codeql)
        self.assertIn("github/codeql-action/analyze@v4", codeql)
        self.assertIn("actions/checkout@v6", gitleaks)
        self.assertIn("gitleaks/gitleaks-action@v3", gitleaks)
        self.assertNotIn("semgrep/semgrep-action", semgrep)
        self.assertIn("semgrep scan --config p/default --error", semgrep)
        self.assertIn("google/osv-scanner-action/.github/workflows/osv-scanner-reusable-pr.yml@v2.3.8", osv)
        self.assertIn("merge_group:", osv)

    def test_apply_guardrails_dry_run_does_not_create_missing_target(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            target = root / "missing-target"
            write(source / ".specify/memory/constitution.md", "# Constitution\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / "tools/apply_guardrails.py"),
                    "--source",
                    str(source),
                    "--target",
                    str(target),
                    "--mode",
                    "dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("copy .specify/memory/constitution.md", result.stdout)
            self.assertFalse(target.exists())

    def test_task_traceability_catches_reverse_orphan_width_and_parallel_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "specs/demo/spec.md",
                "# Spec\n\n"
                "- FR-001: First requirement.\n"
                "- FR-002: Orphan requirement.\n"
                "- US-001: User story.\n"
                "- SC-001: Success criterion.\n"
                "\n## Out of Scope\n\n- None.\n",
            )
            write(root / "specs/demo/plan.md", "# Plan\n\nADR-001: Accepted design.\n")
            write(
                root / "specs/demo/tasks.md",
                "# Tasks\n\n"
                "- [ ] T001 [FR-001] [US-999] [SC-999] [ADR-999] Files: a.py, b.py, c.py, d.py, e.py, f.py\n"
                "- [ ] T002 [P] [FR-001] Files: shared.py\n"
                "- [ ] T003 [P] [FR-001] Files: shared.py\n",
            )

            findings = check_task_traceability.check(root)
            messages = "\n".join(f.message for f in findings)
            self.assertIn("FR-002 is not referenced", messages)
            self.assertIn("missing US references: US-999", messages)
            self.assertIn("missing SC references: SC-999", messages)
            self.assertIn("missing ADR references: ADR-999", messages)
            self.assertIn("touches 6 files without an ADR", messages)
            self.assertIn("Parallel tasks share files", messages)

    def test_resource_catalog_freshness_reports_missing_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "docs/references/resource-catalog.yaml",
                "resources:\n"
                "  - name: example\n"
                "    type: documentation\n"
                "    url: https://example.test/docs\n"
                "    use: example source\n",
            )
            resource_catalog_freshness = import_module("tools.resource_catalog_freshness")

            findings = resource_catalog_freshness.check(root)
            messages = "\n".join(f.message for f in findings)
            self.assertIn("verified_at", messages)
            self.assertIn("maintenance_status", messages)
            self.assertIn("license_checked", messages)


if __name__ == "__main__":
    unittest.main()
