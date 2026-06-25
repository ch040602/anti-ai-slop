# Anti-AI Slop

[![Spec coherence](https://github.com/ch040602/anti-ai-slop/actions/workflows/spec-coherence.yml/badge.svg)](https://github.com/ch040602/anti-ai-slop/actions/workflows/spec-coherence.yml)
[![No AI slop](https://github.com/ch040602/anti-ai-slop/actions/workflows/no-ai-slop.yml/badge.svg)](https://github.com/ch040602/anti-ai-slop/actions/workflows/no-ai-slop.yml)

Anti-AI Slop is a Codex skill and Spec Kit guardrail pack for turning vague "this feels generic" feedback into evidence-backed review, rewrite, and validation work.

It is not an AI detector. It does not decide whether a person used AI. It reviews visible quality signals: weak specificity, unsupported claims, template residue, decorative UI, proof-shaped citations, unowned generated code, chart noise, and localization mismatch.

## GitHub About Metadata

Description:

```text
Evidence-backed Codex skill and Spec Kit guardrail pack for reviewing generic, template-like, or low-specificity outputs without making AI-authorship claims.
```

Tags:

```text
codex-skill, spec-kit, guardrails, ai-slop, output-quality, prompt-engineering, code-review, documentation-review, validation, agent-workflows
```

## Highlights

- A Codex skill for reviewing generic or template-like artifacts with evidence, fixes, and verification.
- Spec Kit memory files, prompts, checklists, and CI examples for repository-level guardrails.
- Standard-library Python validators for specs, tasks, evidence links, glossary terms, placeholders, and dependency justification.
- A migration helper that can dry-run or merge the guardrail surface into another repository without overwriting existing files.

## Demo

![Anti-AI Slop validator, migration, and review demo](assets/readme-demo.gif)

The demo is generated from `tools/generate_readme_demo_gif.py` by executing real repository commands and rendering their stdout. It currently captures the coherence gate, repository inventory, and a dry-run guardrail apply against a temporary target repository.

Regenerate it with:

```powershell
python tools\generate_readme_demo_gif.py
```

## Quick Start

Install the skill into your Codex skills directory:

```powershell
git clone https://github.com/ch040602/anti-ai-slop.git C:\Users\%USERNAME%\.codex\skills\anti-ai-slop
```

Start a new Codex session so the skill list refreshes, then invoke it directly:

```text
$anti-ai-slop Review this README for generic claims, missing proof, and concrete fixes.
```

Run the repository self-check:

```powershell
python tools\validators\check_all.py --root . --profile pack-self --format markdown
python -m unittest discover -s tests
```

Expected healthy output:

```text
# Anti-AI Slop Coherence Report (pack-self)

Score: 100
CRITICAL: 0
HIGH: 0
MEDIUM: 0
LOW: 0

No findings.
```

## Use It Two Ways

| Mode | Use it for | Entry point |
|---|---|---|
| Review skill | Critique or rewrite one artifact: README, report, UI, deck, PR, chart, image prompt, or product copy. | `$anti-ai-slop Review ...` |
| Guardrail pack | Add spec-first anti-slop gates to a repository with prompts, memory files, validators, and CI examples. | `python tools\apply_guardrails.py ...` |

## Review Skill

The review skill converts broad critique into repairable findings:

```text
visible evidence
-> signal category
-> false-positive check
-> contract impact
-> missing specificity input
-> concrete fix
-> verification criterion
```

Example prompt:

```text
$anti-ai-slop Audit this product page for template-like claims and rewrite the weak sections.
```

Example finding shape:

```md
### P1 - Generic value proposition
- Evidence: The hero says "Supercharge your workflow" without naming the user task.
- Why it matters: The sentence could fit almost any SaaS product.
- Fix: Name the workflow, input, output, and measurable result.
- Example revision: "Turn support-call transcripts into QA-ready coaching notes in under 3 minutes."
- Verification: A reader can identify the user, input, transformation, and output from the first screen.
```

The skill covers:

- writing, documentation, explainers, and README files;
- reports, policy notes, research summaries, and executive analysis;
- landing pages, product pages, sales copy, and brand language;
- websites, SaaS screens, dashboards, and design systems;
- slide decks and presentation narratives;
- generated images, thumbnails, mockups, and hero visuals;
- code snippets, generated frontend, PR descriptions, and technical docs;
- charts, KPI cards, analytics screenshots, and BI mockups;
- localization, translated copy, and region-specific messaging;
- roadmaps, launch plans, implementation plans, and operational specs.

## Guardrail Pack

The guardrail pack applies the same discipline to a whole repository. It ships:

- durable project memory in `.specify/memory/`;
- Spec Kit override templates in `.specify/templates/overrides/`;
- Codex prompts in `codex/prompts/`;
- local agent skills in `.agents/skills/`;
- Markdown checklists for requirements, PR review, dependency review, release, security, and AI-slop review;
- standard-library Python validators under `tools/validators/`;
- CI examples under `.github/workflows/`.

Apply it to another repository:

```powershell
git clone https://github.com/ch040602/anti-ai-slop.git C:\tmp\anti-ai-slop

python C:\tmp\anti-ai-slop\tools\apply_guardrails.py `
  --source C:\tmp\anti-ai-slop `
  --target C:\path\to\repo `
  --mode dry-run

python C:\tmp\anti-ai-slop\tools\apply_guardrails.py `
  --source C:\tmp\anti-ai-slop `
  --target C:\path\to\repo `
  --mode merge `
  --manifest-out C:\path\to\repo\.anti-ai-slop-apply-manifest.json
```

Apply behavior:

- `dry-run` reports planned copies and does not write inside the target repository.
- `merge` copies missing guardrail files from `manifest.txt`.
- Existing target files are preserved.
- Test-only files and generated cache artifacts are excluded from apply plans.

## Validator Profiles

| Profile | Scope |
|---|---|
| `pack-self` | Full self-check for this repository. |
| `target-repo` | Service-code-oriented checks for a repository that adopted the pack. |
| `feature --feature 123-feature-name` | Checks scoped to one feature directory under `specs/`. |
| `ci-strict` | CI gate using the full pack scope. |

Core command:

```powershell
python tools\validators\check_all.py --root . --profile pack-self --format markdown
```

The validator suite checks task traceability, spec coverage, evidence links, glossary terms, architecture boundaries, dependency justification, manifest integrity, resource-catalog freshness, workflow integrity, vague language, placeholders, and template tokens.

## Validator Surface

- `tools/validators/check_config_integrity.py`
- `tools/validators/check_task_traceability.py`
- `tools/validators/check_spec_coverage.py`
- `tools/validators/check_evidence_links.py`
- `tools/validators/check_glossary_terms.py`
- `tools/validators/check_architecture_boundaries.py`
- `tools/validators/check_dependency_justification.py`
- `tools/validators/check_manifest_integrity.py`
- `tools/validators/check_resource_catalog_freshness.py`
- `tools/validators/check_template_tokens.py`
- `tools/validators/check_workflow_integrity.py`
- `tools/validators/check_vague_language.py`
- `tools/validators/check_placeholders.py`
- `tools/resource_catalog_freshness.py`
- `dependency-baseline.json`

## Workflow

Repository work follows this path:

```text
inventory
-> constitution / glossary / architecture principles
-> spec
-> clarify
-> checklist
-> plan
-> tasks
-> analyze
-> implementation
-> validation evidence
-> PR review
```

The pack is designed around traceability: requirements should map to tasks, tasks should map to validation, and findings should include evidence, impact, fix, and verification.

## Installation In Other Runtimes

### Claude Code

Use this repository as a skill:

```powershell
mkdir .claude\skills
git clone https://github.com/ch040602/anti-ai-slop.git .claude\skills\anti-ai-slop
```

Or apply it as a guardrail pack with `tools\apply_guardrails.py`. This repository includes both `AGENTS.md` for Codex-style agents and `CLAUDE.md` for Claude Code project guidance.

### Other Agent Runtimes

Use `SKILL.md` as the primary instruction file, keep `AGENTS.md` or `CLAUDE.md` when the runtime understands them, and run the validators directly in scripts or CI:

```powershell
python tools\validators\check_all.py --root C:\path\to\repo --profile target-repo --format markdown
```

### Manual Copy

Copy the repository folder into any Codex-compatible skills directory:

```text
<codex-home>/skills/anti-ai-slop/
```

Keep `SKILL.md` at the skill root.

## Configuration

Most behavior is configured by editing Markdown files:

| Need | Edit |
|---|---|
| Skill routing and invocation behavior | `SKILL.md` |
| Universal review gates | `protocols/output_design_review_gate.md` |
| Finding format and severity | `protocols/finding_format.md` |
| Modality-specific review rules | `dimensions/*.md` |
| Recurring field-reported patterns | `research/field_reported_ai_smell_patterns.md` |
| Final report shapes | `templates/*.md` |
| Spec Kit memory | `.specify/memory/*.md` |
| Validator behavior | `tools/validators/*.py` |
| File inventory for guardrail application | `manifest.txt` |

Optional shared validator config may live at `config/guardrails.json`, `config/guardrails.yaml`, or `config/guardrails.yml`. Local overlays such as `config/guardrails.local.json` are rejected until merge semantics are implemented.

Add a pattern only when it can be paired with visible evidence, a false-positive note, and a concrete repair.

## Repository Layout

```text
anti-ai-slop/
+-- SKILL.md
+-- AGENTS.md
+-- CLAUDE.md
+-- PROMPTS.md
+-- .specify/
+-- .agents/
+-- codex/prompts/
+-- protocols/
+-- dimensions/
+-- checklists/
+-- research/
+-- templates/
+-- tools/
+-- tests/
+-- specs/
+-- docs/
+-- assets/
+-- manifest.txt
```

## Safety Boundaries

Anti-AI Slop does not:

- make forensic authorship claims;
- accuse a person or organization of using AI;
- optimize artifacts to evade AI detectors;
- replace factual verification, legal review, security review, accessibility review, or domain expert review;
- remove useful structure only because it resembles a common AI pattern.

Good structure, clean grammar, common fonts, cards, bullets, and polished visuals are not defects by themselves. They become issues only when they weaken purpose, credibility, specificity, usability, or brand fit.

## Development

Run the full local check before shipping changes:

```powershell
python tools\validators\check_all.py --root . --profile pack-self --format markdown
python -m unittest discover -s tests
python -m compileall tools tests
```

For pack-level validator, workflow, migration-tool, or guardrail behavior changes:

1. Update `VERSION` and `CHANGELOG.md`.
2. Keep `SKILL.md`, `README.md`, and `manifest.txt` aligned.
3. Preserve the rule against AI-authorship claims.
4. Keep validators actionable: severity, path, rule, evidence, and fix.
