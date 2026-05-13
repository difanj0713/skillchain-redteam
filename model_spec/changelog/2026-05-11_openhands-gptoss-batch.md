# 2026-05-11 — openhands + gpt-oss-120b on 3 easy tasks

## Files touched

- **Added** `model_spec/results/2026-05-11_openhands-gptoss120b-3easy.md` — full run breakdown.
- **Added** `jobs-oh-gptoss/2026-05-11__04-44-17/` — raw trial artifacts (kept for re-parsing / comparison).
- **Added** `/tmp/sb_batch_3easy/` — staging dir with symlinks to dialogue-parser, fix-build-agentops, court-form-filling (transient).

No source code edits.

## Outcome

3/3 tasks → reward 0.0. Plumbing healthy (skills mounted, prompts include skill paths, ACP trajectory captured). Model is the bottleneck:

- court-form-filling: 0 tool calls (refusal).
- dialogue-parser: 5 tool calls, 20/35 asserts pass, 0/6 CTRF functions clean.
- fix-build-agentops: 10 tool calls with malformed JSON args + tool hallucinations; required output files never written.

`invoke_skill` calls across all 3 trials: 0. The skill files were correctly deployed and named in the system prompt — model just never reached for them.

## Commands run

```bash
source /datadrive/difan/skillsbench/.envrc
mkdir -p /tmp/sb_batch_3easy
ln -sfn $PWD/tasks/dialogue-parser    /tmp/sb_batch_3easy/dialogue-parser
ln -sfn $PWD/tasks/fix-build-agentops /tmp/sb_batch_3easy/fix-build-agentops
ln -sfn $PWD/tasks/court-form-filling /tmp/sb_batch_3easy/court-form-filling

nohup uv run bench eval create \
  -t /tmp/sb_batch_3easy -a openhands \
  -m openrouter/openai/gpt-oss-120b:free \
  -s auto -c 1 -o jobs-oh-gptoss \
  > /tmp/oh_gptoss_3easy.log 2>&1 &
```

## Follow-ups

- Run the same 3 tasks with a stronger free model (e.g. `claude-haiku-4-5-20251001` or `gpt-5.2-codex`) for comparison signal.
- Investigate `skill_nudge` in `benchflow/sdk.py` if we want to force gpt-oss-120b to actually invoke skills.
