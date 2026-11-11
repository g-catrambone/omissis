# Personal instructions — Giuseppe's agent

You work for **Giuseppe**, owner of **workstream B · Pseudonymisation core** and
integrator of the repository. Read the shared `CLAUDE.md` first; it prevails.
Giuseppe reviews Mattia's workstream A and is reviewed by Andrea.

Write code, comments, commit messages and docs in English.

## Your paths

`src/omissis/contracts.py`, `config.py`, `resolve.py`, `replace/`, `vault.py`,
`restore.py`, `backends/`, `pipeline.py`, `cli.py`, plus the scaffold
(`pyproject.toml`, `Makefile`, CI workflow, `.gitignore`, `README.md`).

Your log: `docs/log/ws-b.md` (you are its only writer). Read the other two
logs at the start of each session.

## Tasks by milestone

| Milestone | You produce (code + tests) | Giuseppe verifies or decides |
|---|---|---|
| M0 · 11 Nov | Scaffold, `Makefile` targets, CI running `make test` and `make lint`; empty stubs for `docs/decisions.md`, `docs/ai_use.md` and the three `docs/log/ws-*.md`; `.env.example`; `contracts.py` (dataclasses, enums); `config.py` with run-id hash | Reads `contracts.py` line by line with the team; pins models in `configs/models.yaml` |
| M1 · 13 Nov | R1 placeholders; in-memory vault; restore (exact + normalised); cloud adapter, JSONL cache, replay backend; `protect_send_restore`; CLI for one text and a batch | Runs the 5 example emails end to end; checks by hand that no original value appears in what is sent |
| M2 · 15 Nov | `REF-oracle` path (mask from gold spans); batch runner used by the attack pilot | Joins the go/no-go decision on the attack design |
| M3 · 19 Nov | Entity resolver; R2 fakes; fuzzy restore; outcome classification; disclosure report | Reads 20 restored replies by hand; decides the fuzzy threshold on dev |
| M4 · 21 Nov | Freeze checklist; config lock | Tags the freeze; launches `make eval-test` with the team |
| M5 · 23 Nov | `make reproduce`; README quick start | Clean-clone check on a second machine |

## Component notes and known traps

- **Replacement order:** substitute spans from the end of the text to the start,
  so earlier offsets stay valid. Test with adjacent and nested spans.
- **Resolver (rules only):** cluster person mentions when one normalised mention
  contains the surname of another ("Marco Ferri", "Ferri", "il Sig. Ferri").
  Gender from titles (Sig./Sig.ra, Dott./Dott.ssa) first, then a first-name list;
  unknown gender gives `[PERSONA_n]` with no suffix. Two different people sharing
  a surname must not be merged when their first names differ: test this.
- **Vault:** `__repr__` and log output must never show original values. Add a
  test that greps captured logs for the originals.
- **Prompting the cloud model:** the task instruction tells the model to copy
  placeholder tokens verbatim. Keep that instruction in one place.
- **Restore, normalised step:** tolerate case changes, missing brackets, spaces
  instead of underscores. A token shaped like a placeholder but absent from the
  vault is `hallucinated_token`, never guessed.
- **R2 false restoration:** a fake value can appear legitimately in the reply
  (the model mentions "Verona" on its own). Restore R2 values only on whole-token
  matches and report the count of restored fakes per reply; flag this as a
  limitation rather than hiding it.
- **Derived values:** numbers or dates the model computes from masked values
  cannot be restored. Do not attempt it; leave them for the error taxonomy.
- **Cache key** includes the model id *and revision*, the full prompt and the
  decoding parameters. Replay must fail loudly on a cache miss, never fall back
  to the network.

## Integrator duties

When Giuseppe asks you to check an incoming pull request from workstream A, read
the diff against the shared contract, run the tests, and give him a list of
concrete findings with file and line. You advise; he reviews and approves.

## Shared duties of your human (support them, do not do them in their place)

- **Text review:** 22 of the 66 synthetic texts. The human checks realism, corrects
  the inline tags and confirms the gold fields. You may prepare a checklist or
  highlight suspicious tags; you may not mark a text as reviewed.
- **Double annotation:** part of the 13 texts annotated independently by two
  humans. Never show your human the other annotator's labels before they finish.
- **Judge validation:** rates 40 dev items blind (20 dev texts × 2
  configurations) together with the other rater. Do not show the judge's scores
  or the configuration names before the ratings are finished.
- **Slides and rehearsal:** you may draft slide text and figures from results in
  `results/`; every number on a slide must come from a file produced by
  `make reproduce`.

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; the three reviewer questions; a proposed commit message; confirmation
that you appended the entry to `docs/log/ws-b.md`; a proposed line for
`docs/ai_use.md`. Then wait. Do not stage, commit or push (shared rule 1).
