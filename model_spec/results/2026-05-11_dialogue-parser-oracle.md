# dialogue-parser oracle — root cause and verified fix

## Summary

The previous run reported the oracle failed with `ModuleNotFoundError: dialogue_graph`. After reading the benchflow CLI / SDK source, the cause is **operator error, not a repo bug**. The fix is the `-s` flag, not a code change.

## Verification

Command:

```bash
cd /datadrive/difan/skillsbench
uv run bench eval create \
  -t tasks/dialogue-parser \
  -a oracle \
  -s tasks/dialogue-parser/environment/skills
```

Result:

```
Task: dialogue-parser
Agent: oracle (no model)
Reward: 1.0
Tool calls: 0
```

Verifier (`jobs/2026-05-11__04-31-31/dialogue-parser__aee1b456/verifier/test-stdout.txt`):

```
============================== 35 passed in 0.07s ==============================
TEST SUMMARY: 6 / 6 tests passed
REWARD SCORE: 1.0
```

All 35 parametrized cases pass → all 6 CTRF test functions green → reward 1.0.

## Why the previous run failed

Walking the source:

1. `benchflow/cli/eval.py:149` — `-s / --skills-dir` is a CLI option, **not** auto-detected from `environment/skills/`.
2. `benchflow/_agent_setup.py:212-264` — `deploy_skills()` distributes skills to `~/.claude/skills/`, `~/.codex/skills/`, etc., **only if** either:
   - the CLI `--skills-dir` was passed (runtime upload to `/skills`), or
   - `task.toml` declares `[environment] skills_dir = "..."` (it does not for dialogue-parser).
3. `tasks/dialogue-parser/environment/Dockerfile` — by convention (see `CONTRIBUTING.md`), the Dockerfile does **not** `COPY` skills. This avoids inflating no-skills baselines.
4. `tasks/dialogue-parser/solution/solve.sh` — sets `PYTHONPATH` to include `/app/environment/skills/dialogue_graph/scripts:/root/.claude/skills/dialogue_graph/scripts`. The latter is what gets populated when `deploy_skills()` runs.

So when the operator invokes `bench eval create -t tasks/dialogue-parser -a oracle` **without** `-s`, no skills are mounted, `/root/.claude/skills/dialogue_graph/` does not exist, `import dialogue_graph` raises `ModuleNotFoundError`, and the oracle exits non-zero with no `dialogue.json` produced. Verifier then scores 0.

The benchflow integration runner (`experiments/scripts/run_benchflow_integration.py:208-242`) auto-passes `--skills-dir` when `environment/skills/` exists. Hand-rolled `bench eval create` invocations do not.

## Conclusion

- Not a repo bug. Repo design is intentional: skills are runtime-mounted, never image-baked.
- Operational rule: **for any task with `environment/skills/`, pass `-s tasks/<id>/environment/skills`**.
- For the free-tier model run (run #2 reward 0.0), reward is still meaningful: 23/35 asserts is partial signal, but CTRF rolls up per-function so a single failing case per function zeros the function. To raise the free-model reward, no operational change helps — the model itself needs to produce a more faithful `dialogue.json`. Re-running with `-s` flag also distributes the skill to the model at `~/.claude/skills/dialogue_graph/`, giving it the helper API the oracle uses.

## Recommended invocations going forward

Oracle sanity check:

```bash
uv run bench eval create -t tasks/<id> -a oracle -s tasks/<id>/environment/skills
```

Free-model run (e.g. claude-haiku):

```bash
uv run bench eval create -t tasks/<id> -a claude-agent-acp -m claude-haiku-4-5-20251001 -s tasks/<id>/environment/skills
```

Or use the integration runner which auto-detects.

## No code edits were needed

Confirmed by reading and not modifying:

- `tasks/dialogue-parser/environment/Dockerfile`
- `tasks/dialogue-parser/solution/solve.sh`
- `tasks/dialogue-parser/solution/solution.py`
- `tasks/dialogue-parser/tests/test.sh`
- `tasks/dialogue-parser/tests/test_outputs.py`
