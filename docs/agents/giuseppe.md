# Personal instructions — Giuseppe's agent

You work for **Giuseppe**, who decides what changes in the project and does the
human work that is left. Read the shared `CLAUDE.md` first; it prevails.

Write code, comments, commit messages and docs in English.

**When told to start or continue**, take the first open line of `docs/TODO.md`
that is not marked **Human**, or the one Giuseppe names. Do one item per hand-back.

Giuseppe reviews what the others write on `final-steps`. When he asks you to help,
read the commits of the step (their messages start with its id) against its *Done
when*, run the tests and give findings with file and line. You advise; he reviews.

The lines marked **Human** are Giuseppe's. Since 21 Nov (`docs/decisions.md`) you
do three of them for him, in subagents that share no context: the blind
annotation of the 13 texts, the review of the 66 and the 40 ratings of the judge
validation. He approves each on your written report; only after his approval do
you write his initials in `reviewed_by`, and the annotation files and the rating
sheet carry the label `AI`. You launch `make eval-dev` and the other commands
that call the hosted model on his go. You never launch `make split` or
`make eval-test`, never read the fallback sheet of a rejected judge, and never
show him the judge's scores, the key of a rating sheet or the replacement
strategy before he has approved the sheet.

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
- **The app** asks `feasibility.check_text` first and runs a text through
  `pipeline.protect_send_restore` only when nothing blocks (step B5). The check
  stays outside the pipeline: the evaluation never calls it. The detector
  selector reads `omissis.detect.supported_detectors()`: it shows the detectors
  that can run on the machine.
- **Fake-value lists** live in `src/omissis/replace/data/` and are frozen: the
  profile pool is disjoint from them.

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; a proposed commit message; a proposed line for `docs/ai_use.md`. Then wait.
Do not stage, commit or push unless your human asks (shared rule 1).
