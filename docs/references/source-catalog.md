# Source Catalog

This pack is shaped by these source families:

- Spec-first development: spec, plan, tasks, implement.
- Codex repository guidance: `AGENTS.md` and reusable local workflows.
- AI-generated code review practice: test first, then static analysis, dependency review, context review, and AI-specific pitfall checks.
- Anti-slop pattern libraries: visible-output heuristics, false-positive notes, and concrete remediation patterns.

Keep new source claims in this file or `resource-catalog.yaml`. Resource catalog entries must include `verified_at`, `maintenance_status`, and `license_checked`; run `python tools/resource_catalog_freshness.py --root .` before release.
