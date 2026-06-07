# Anti-AI Slop Skill

This package provides a structured Markdown-only skill for reviewing outputs before delivery. It focuses on purpose-fit, specificity, evidence, design quality, and common generic or AI-scented output patterns.

Skill name: `anti-ai-slop`

Description: Detect and improve AI slop, generic-output, template-like, and AI-smell patterns across writing, UI, slides, visuals, code, reports, and other artifacts without making authorship claims.

Tags: `codex-skill`, `anti-ai-slop`, `ai-slop`, `ai-smell`, `generic-output-review`, `output-quality`, `writing-review`, `ui-review`, `code-review`

## Installation

Copy the `anti-ai-slop/` folder into a skill-compatible directory. The root file is `SKILL.md`.

## Intended use

Use this as a review overlay after drafting or generating an output. It can be applied to:

- writing and documentation;
- research and reports;
- marketing and brand copy;
- websites, apps, and UI systems;
- slide decks;
- generated visuals;
- charts, dashboards, and analytics mockups;
- localized, translated, or multilingual outputs;
- roadmaps, implementation plans, and operational specs;
- code and technical outputs.

## Important boundary

This skill does not detect AI authorship. It reviews visible output quality. A pattern is only an issue when it weakens purpose, clarity, credibility, usability, or brand fit.

## Recommended flow

1. Read `SKILL.md`.
2. Use `taxonomies/task_purpose_matrix.md` to classify the work purpose.
3. Use `protocols/output_design_review_gate.md` as the universal review gate.
4. Use the appropriate file in `dimensions/`.
5. Use `templates/review_report_template.md` or `templates/design_review_addendum.md` for the final response.

For AI-smell reduction work, use the evidence-to-revision worksheet in `protocols/review_workflow.md` before writing findings. This keeps the review grounded in visible evidence, false-positive checks, contract impact, concrete fixes, and verification criteria.

## Field-reported AI-smell register

Use `research/field_reported_ai_smell_patterns.md` when the task mentions AI-smell, AI slop, generic-output tells, Reddit/GitHub-reported patterns, detector-like cleanup, code slop, or PR hygiene. Treat it as a pattern register, not an authorship detector.

The register summarizes field-reported pattern families:

- lexical inflation and over-polished diction;
- generic throat-clearing, rhetorical crutches, and repeated transition words;
- structural symmetry, list abuse, and markdown over-formatting;
- tonal flatness, pseudo-depth, generic positive closure, and synthetic social-post cadence;
- proof-shaped unreliability, fake citations, fabricated specificity, and machine artifact leakage;
- technical documentation, commit, PR, security-report, and reproducibility slop;
- Web/UI SaaS-average aesthetics, blinking-dot decoration, copy-paste layout grammar, and generated visual artifacts;
- detector overreach and false-positive risks.

Use the annex after the normal output-design gate:

1. Identify the output purpose and audience.
2. Select the relevant file under `dimensions/`.
3. Check the field-reported register for matching pattern clusters.
4. Apply the false-positive notes before reporting a finding.
5. Convert each accepted finding into a concrete revision rule.
