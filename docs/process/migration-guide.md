# Migration Guide

## From Markdown Skill To Guardrail Pack

1. Keep the existing `SKILL.md` and review dimensions as the human review layer.
2. Add `.specify/memory/*` for persistent principles.
3. Add `tools/validators/*` for executable coherence gates.
4. Add `codex/prompts/*` for repeatable Codex workflows.
5. Add `specs/*` examples that show traceability.

## Rollout Modes

- `dry-run`: inventory and report planned copies.
- `merge`: copy missing guardrail files without deleting target files.
