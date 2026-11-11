# AI-use register

One line per task, added by the human who did the task (agents propose the line).
Newest last. If two branches both add lines, keep both when merging.

| Date | Human | Task | Produced by the agent | Changed or decided by the human |
|---|---|---|---|---|
| 2026-11-11 | Giuseppe | Project plan and agent instructions | Critical review of the original specification, reduced scope, guidelines PDF, `CLAUDE.md`, personal files | Scope decisions, team split, git rule, project name |
| 2026-11-11 | Giuseppe | Specifications and task lists | `docs/interfaces.md`, `docs/evaluation_protocol.md`, `docs/tasks/` | Required planning only (code draft removed); asked for a simpler, stepwise process with gates; kept the AI-use register separate; removed language preferences from personal files; reviewed the specifications and task lists before committing |
| 2026-11-11 | Giuseppe | B0 Foundation | Scaffold, `contracts.py`, `config.py`, `vault.py`, backends types, boundary stubs, 205 tests, `interfaces.md` edits (run_id scope, Span validation, entity_id format, placeholder rejections, CacheMissError base, required config keys, string model fields) | Decided a single pull request, the run_id scope and the Span validation rules; approved the eight implementation choices; reviewed the diff and committed without AI co-author |
