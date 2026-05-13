# SkillsBench Code Editing Spec

Authoritative coding standard for any AI edits in this repository.

## 1. Minimal Executable Code

- No `#` comments. No docstrings. No banners, no section headers in comments.
- No AI fluff: no "this function does X", no "now we will Y", no apologies, no celebratory text in code or commit messages.
- Names must self-document. If a name needs a comment to be readable, rename the thing.
- One responsibility per function. No defensive try/except wrapping that swallows errors. No fallback paths for situations that cannot occur.
- Only validate at system boundaries (CLI args, network, file I/O). Inside the module, trust your own invariants.
- Do not add new abstractions, base classes, or config flags unless the current task requires them.

## 2. Source Preservation

- Never delete code from existing source files. Comment it out instead using the marker:
  ```
  # [MODIFIED YYYY-MM-DD reason]
  ```
- Replacements are written as: comment the old line(s) with the marker on the line above, then write the new line(s) below.
- This applies to task files (`tasks/<id>/...`), the bench CLI, and any benchflow integration code we touch. New scratch files we author are not subject to this rule.

## 3. Test Before Declaring Done

- For any added or modified module, write a unit/smoke test that exercises:
  1. The golden path with realistic inputs.
  2. At least one edge case (empty input, missing optional dep, etc.).
  3. At least one failure case the code must reject or recover from.
- Tests live under `model_spec/tests/` during development. They are temporary and may be deleted once results are recorded.
- After tests pass, write a result file:
  ```
  model_spec/results/YYYY-MM-DD_<slug>.md
  ```
  Contents: what was changed, command(s) used to verify, test output summary, follow-ups.
- Every session that touches code also writes:
  ```
  model_spec/changelog/YYYY-MM-DD_<slug>.md
  ```
  Contents: one-line summary, files touched, rationale, links to result files.

## 4. Complexity Budget

- Cyclomatic complexity ceiling: **CC ≤ 10** per function. Verify with:
  ```
  radon cc -s -n C <file>
  ```
  Any function flagged at grade D or worse must be split or simplified before the change is considered complete.
- Module-level: prefer pure functions and small helpers over long imperative blocks.

## 5. Task-File Rules (SkillsBench-specific)

- `Dockerfile`: do **not** bake skills into the image. Skills are injected at runtime via `bench eval create -s tasks/<id>/environment/skills/`. Baking inflates the no-skills baseline.
- `solve.sh`: must run end-to-end inside the container with skills mounted at `/app/environment/skills/<skill>/` or `/root/.claude/skills/<skill>/`. Set `PYTHONPATH` accordingly.
- `test.sh`: writes `/logs/verifier/reward.txt` and is the sole source of the reward signal. CTRF rolls up parametrized cases per test function; design tests with that in mind.
- `instruction.md`: outcome-focused, no skill names mentioned.

## 6. Commit Hygiene

- One logical change per commit. Commit messages state the why, not the what.
- Never amend pushed commits. Never `--no-verify`.
- Never modify `uv.lock` by hand; regenerate with `uv lock`.

## 7. Long-Running Commands

- Use `nohup ... &` for anything expected to take longer than ~30s, with output redirected to a logfile under `/tmp/` or `experiments/logs/`.

## 8. When in Doubt

- Read the existing task next door before inventing a new pattern.
- If a task in `tasks/` already solves a similar problem, copy its structure verbatim and adapt.
- If unsure whether to delete vs. comment-out, comment out.
