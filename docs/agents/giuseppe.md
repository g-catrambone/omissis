# Personal instructions — Giuseppe's agent

You work for **Giuseppe**, owner of **block 2 · Core completion** and of
**block 5 · Closing**. Read the shared `CLAUDE.md` first; it prevails. At the
gates Giuseppe reviews block 1 (with Andrea) and block 4, both Mattia's; Andrea
reviews block 2; Andrea and Mattia review block 5.

Write code, comments, commit messages and docs in English.

**When told to start or continue, work from `docs/tasks/block-2.md`** after gate
G1 (task 2.1 does not wait for it), and from `docs/tasks/block-5.md` after
gates G3 and G4, as described in
`docs/tasks/README.md`. Between gate G2 and those two it is not your turn:
change nothing, except a `fix/…` branch for a defect in block 2's code that
Giuseppe explicitly asks for, and task 2.7 (the app), which may be finished
beside block 3. After gate G5, task P.1 is yours.

## Your paths

Block 2: `src/omissis/contracts.py`, `config.py`, `vault.py`, `resolve.py`,
`replace/`, `restore.py`, `backends/`, `pipeline.py`, `cli.py`, `app.py`;
`configs/`; `.env.example`; `tests/core/`, `tests/app/`; the `demo` target of
the `Makefile`; `docs/handoff/block-2.md`. The core modules were written in
block 1 by Mattia's agent and are yours from gate G1. You never change the
entries of `configs/models.yaml`: pinning a model is a human edit.
Block 5: `README.md`, `LICENSE`, `docs/cards.md`, the `reproduce` target of the
`Makefile`, the final files in `results/`. After G5: `docs/slides/giuseppe.md`.

## What the blocks deliver

| Block | You produce (code + tests) | Giuseppe verifies or decides |
|---|---|---|
| 2 · Core completion · Mon 16 – Wed 18 Nov | Clean-up of old task ids; detector values `GOLD` and `NONE`, `gold_spans`, named configurations and `omissis mask`; entity resolver; cloud provider; R2 fakes; fuzzy restore; Gradio app; hand-over note | Chooses the cloud-side models with the team and creates the key; approves the name and fake-value lists and the dependencies; reads the ten real restored replies; tags `block-2` |
| 5 · Closing · Mon 23 – Tue 24 Nov | Results, error taxonomy, model and data cards; `make reproduce`; README; licences | Launches `make eval-test` with the team; checks every headline number; clean-clone check; tags `v1.0` |

Block 1 left a pipeline that works with the D0 rules and an interim resolver.
Block 2 makes the three references possible: with detector `GOLD` the pipeline
masks the human annotation, with `NONE` it masks nothing. Nothing in block 2
depends on the detectors D1–D4, which arrive from block 4 in the same days.

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

- **Fake-value lists** live in `src/omissis/replace/data/`. Block 3 builds its
  profile pool to be disjoint from them, so do not change them after G2.
- **Hand-over note:** block 3 starts from it. Include one worked call for
  `mask` with gold spans (with and without `mask_quasi`), `protect_send_restore`
  with gold spans, `complete` on each pinned role, `load_eval_configs` and
  `omissis mask`.
- **The app** runs texts through `pipeline.protect_send_restore` only. Its
  detector selector reads `omissis.detect.supported_detectors()`, so detectors
  merged later by block 4 appear without a change.

## Reviewing blocks 1 and 4

When Giuseppe asks you to help him review Mattia's code (the core modules of
block 1 at gate G1, the detectors at gate G4), read the hand-over note and the
code against `docs/interfaces.md`, run the tests, and give him concrete
findings with file and line. You advise; he reviews.

## Shared duties of your human (support them, do not do them in their place)

- **Text review (during block 3):** 22 of the 66 synthetic texts, on a branch
  `b3/review-<initials>`. The human checks realism, corrects the inline tags
  and confirms the gold fields. You may prepare a checklist or highlight
  suspicious tags; you may not mark a text as reviewed.
- **Double annotation (during block 3):** part of the 13 texts annotated
  independently by two humans. Never show your human the other annotator's
  labels before they finish.
- **Judge validation (during block 3):** rates 40 dev items blind and sends
  the sheet privately to Andrea. Do not show the judge's scores, the other
  rater's sheet or the replacement strategy before the ratings are finished.
- **Final evaluation (block 5):** the three members launch `make eval-test`
  together, once.
- **Slides and rehearsal:** task P.1 of `docs/tasks/block-5.md`. You draft
  content in your member's file under `docs/slides/`; every number must come
  from a file in `results/<split>/metrics/`.

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; the three reviewer questions; a proposed commit message; a proposed line
for `docs/ai_use.md`. Then wait. Do not stage, commit or push (shared rule 1).
