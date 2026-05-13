# 2026-05-11 — spec authoring + dialogue-parser oracle investigation

## Files touched

- **Added** `model_spec/spec.md` — coding standard for AI edits in this repo.
- **Added** `model_spec/results/2026-05-11_dialogue-parser-oracle.md` — verified oracle run.
- **Added** `model_spec/changelog/2026-05-11_spec-and-oracle-investigation.md` — this file.

No edits to `tasks/`, `experiments/`, `benchflow/`, or any other source.

## Rationale

1. User requested a `spec.md` for this codebase mirroring the conventions used in sibling projects (`verl-tandem`, `skill-adaptation-interp`).
2. User wanted to know whether the `dialogue-parser` oracle failure observed in a prior chat was a repo bug or an operational mistake on our side. Read the benchflow CLI/SDK source, confirmed the latter, verified by running the oracle with `-s`. Reward = 1.0.

## Commands run

```bash
uv run bench eval create -t tasks/dialogue-parser -a oracle \
  -s tasks/dialogue-parser/environment/skills
# → Reward: 1.0
```

## Follow-ups

- Consider opening an upstream benchflow PR to auto-detect `environment/skills/` in `bench eval create`, matching the behavior of `experiments/scripts/run_benchflow_integration.py:208-242`. This would prevent the same operator error for other contributors.
- For the prior free-model run (reward 0.0 with 23/35 asserts), no operational fix exists — model quality drives the score under CTRF per-function rollup.
