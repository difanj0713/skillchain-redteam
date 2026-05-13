# openhands + gpt-oss-120b on 3 easy tasks

## Invocation

```bash
source /datadrive/difan/skillsbench/.envrc   # OPENROUTER_API_KEY → LLM_API_KEY
uv run bench eval create \
  -t /tmp/sb_batch_3easy \                  # symlinks to: dialogue-parser, fix-build-agentops, court-form-filling
  -a openhands \
  -m openrouter/openai/gpt-oss-120b:free \
  -s auto \                                  # per-task environment/skills/
  -c 1 \
  -o jobs-oh-gptoss
```

Job: `jobs-oh-gptoss/2026-05-11__04-44-17/`. Total wall ~12 min.

## Result table

| Task                | Reward | CTRF funcs | Pytest asserts | Tool calls | Wall (s) | Failure mode |
|---------------------|--------|------------|----------------|------------|----------|--------------|
| court-form-filling  | 0.0    | 0/5        | 0 / 47 (all ERROR — no output PDF) | **0** | 134 | Refusal: "I'm unable to edit PDFs" — never tried |
| dialogue-parser     | 0.0    | 0/6        | 20 / 35 passed | 5 | 148 | Wrote custom parser, ignored skill; partial correctness blocked by CTRF rollup |
| fix-build-agentops  | 0.0    | 0/3        | 0 / 3 (no patch/notes written) | 10 | 415 | Tool JSON malformed, hallucinated tool names, gave up before producing required output files |

Aggregate: **0/3 tasks**, no partial reward. Wall dominated by fix-build-agentops' BugSwarm image pull (161s env setup).

## Per-task analysis

### court-form-filling — refusal, 0 tool calls

System prompt **did** advertise the `pdf` skill by name. Model still produced one `agent_message`:

> "I'm unable to edit PDF files directly in this environment. However, I can help you by extracting the exact field names and the values you need to enter, so you can quickly fill the form yourself..."

It then dumped a markdown table of values for the human. 0 tool calls. The verifier ran pytest, found `/root/sc100-filled.pdf` missing, and every test errored. This is classic gpt-oss-120b behavior: when uncertain about tool surface, it falls back to "explain to the user" rather than try. Not a benchflow or skill-deployment issue.

### dialogue-parser — used tools, ignored skill, partial pass blocked by CTRF

Trajectory: 5 tool calls — `ls /app`, view `/app/script.txt`, write `/app/solution.py` (custom parser from scratch), `python3 /app/solution.py`, view `/app/dialogue.json`. System prompt mentioned `.agents/skills` exists but **didn't list the skill by name** (gptoss saw the directory hint, not the helper module).

Outcome: produced a valid `dialogue.json` with parseable structure. 20/35 asserts passed (basic graph schema, several content_integrity checks, three structural connections, three viz checks). 15/35 failed across:
- `test_system_basics[graph_size]` — too few edges
- `test_narrative_content[speaker-*]` — missing Narrator/Barkeep/Merchant/Kira speaker labels (its parser didn't capture speakers correctly)
- `test_graph_logic[reachability, multiple_endings]` — broken topology
- `test_visualization_validity[shapes]` — choice nodes not rendered as diamonds (didn't use the skill's `visualize()`)
- `test_content_integrity[node_text-*]` — wrong text contents on key nodes
- `test_structural_integrity[*]` — missing edges

Because CTRF rolls parametrized cases up to test functions, every one of the 6 functions had ≥1 failing case → 0/6 → 0.0. This is the same pattern as the previous chat's free-model run, just at slightly higher assert count (20 vs. 23).

### fix-build-agentops — agent tried but botched tool args + gave up

10 tool calls. Sample of what went wrong (extracted from `trajectory/acp_trajectory.jsonl`):

- `Error Details: Tool 'terminal.commentary' not found. Available: ['terminal', 'file_editor', 'task_tracker', 'task', 'finish', 'think', 'invoke_skill']` — hallucinated a tool name.
- `Error validating tool 'terminal': Expecting ',' delimiter` (twice) — gpt-oss-120b emitted malformed JSON tool arguments. Known weakness on this model.
- `bash: /home/github/build/failed/AgentOps-AI/env/bin/python: No such file or directory` — assumed a virtualenv existed.
- `pip install -e ... ERROR` — permission denied to system site-packages, didn't recover.
- After 10 calls, model produced an `agent_message` with a written-out "Analysis & Plan – /home/github/build/failed/failed_reasons.txt" block instead of actually creating the file.

Verifier expected: `failed_reasons.txt` exists (didn't), `patch_*.diff` files exist (didn't), build passes after patches (didn't). 3/3 failed → 0.0.

Worth noting: the 4 skills bundled with this task (`analyze-ci`, `temporal-python-testing`, `testing-python`, `uv-package-manager`) were all mounted and named in the system prompt. **`invoke_skill` count: 0 across all three tasks.**

## What this run tells us about the stack

1. **Plumbing is correct.** Skills deployed (`.agents/skills/<name>/` populated), system prompt advertised them, `invoke_skill` tool exposed, sandbox user `agent` worked, ACP trajectory and CTRF verifier all wrote clean artifacts. Three-way oracle would have hit ~3/3 (we verified dialogue-parser at 1.0 earlier; the other two oracles should be similarly clean).
2. **gpt-oss-120b is the bottleneck.** Three distinct failure modes in three runs:
   - Refuse-with-text (court-form-filling): doesn't even try.
   - Reinvent-the-wheel (dialogue-parser): ignores the helper skill, writes a worse parser.
   - Malformed tool args / hallucinated tool names (fix-build-agentops): tool-calling format compliance is weak.
3. **`invoke_skill` adoption is zero.** Skills are advertised in the prompt but the model never reaches for them. To get meaningful skill-use signal from this model you'd need to: (a) inject `skill_nudge="description"` or `"full"` so SKILL.md content is in the system prompt, or (b) pre-condition with a few-shot example. Neither is enabled by default.
4. **CTRF rollup is harsh on partial-credit work.** dialogue-parser would score ~0.57 at assert granularity but 0.0 at function granularity. Worth knowing when interpreting future runs — and when designing tasks (tightly-grouped parametrize ids will zero out a model that's "mostly right").

## Where the artifacts live

```
jobs-oh-gptoss/2026-05-11__04-44-17/
  ├── court-form-filling__d30c18a4/
  │   ├── result.json              ← reward, timing, tool-call count
  │   ├── rewards.jsonl
  │   ├── prompts.json             ← exact user prompt sent
  │   ├── trajectory/acp_trajectory.jsonl   ← every ACP message + tool call
  │   ├── agent/openhands.txt      ← (empty here — agent never used stdout)
  │   ├── agent/install-stdout.txt
  │   └── verifier/{ctrf.json, test-stdout.txt, reward.txt}
  ├── dialogue-parser__3e012771/
  └── fix-build-agentops__68fa8277/
```

## Recommended next moves

- Re-run the same 3 tasks with `claude-haiku-4-5-20251001` (or another tool-call-capable model) under the same `-s auto` config to isolate whether the 0.0 streak is gpt-oss-120b specific. Expectation: haiku will at least produce output files for court-form-filling and trigger non-zero partial scores.
- If we want gpt-oss-120b to use skills, either patch the prompt nudge level (benchflow internal — `skill_nudge`) or write task instructions that explicitly name the helper module.
