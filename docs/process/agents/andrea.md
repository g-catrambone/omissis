# Personal instructions — Andrea's agent

You work for **Andrea**. Read the shared `CLAUDE.md` first; it prevails.

Write code, comments, commit messages and docs in English.

The project is closed: the test split was evaluated once on 22 Nov 2026 and code,
data and results are frozen (`CLAUDE.md`, rule 6). What is left is in
`docs/process/TODO.md`, under *What is left*. A defect found now goes to Giuseppe
and, if he agrees, on a `fix/…` branch.

**When told to start or continue**, take the line of *What is left* that Andrea names.
Do one line per hand-back.

## Component notes and known traps

These notes were written for the blocks. Where they disagree with
`docs/decisions.md`, the decisions prevail.

- **Profiles:** name, gender, age, city, employer, role, bank, branch city,
  financial facts, optional special-category fact. Cohort members share at least
  two quasi-identifiers, so no single clue identifies the author. All values
  invented; names and cities come from lists disjoint from the R2 fake lists.
- **Text generation:** the generator model writes an Italian email from one
  profile and one scenario, marking sensitive spans inline as `[[TYPE|text]]`. A
  script strips the tags and computes character offsets. About 60% bank
  correspondence, 40% HR and health administration; about 30% with
  special-category data; every text has at least one direct identifier.
  **The generator must not be the D3 model or the attacker model**, otherwise
  detection and attack results are inflated. In the hand-over
  note, propose the `docs/cards.md` lines for the generator, the attacker and
  the judge.
- **Annotation policy:** tag *all* direct identifiers, quasi-identifiers and
  special-category spans by type. Do not decide in the annotation whether a
  quasi-identifier "should" be masked; that is a configuration switch.
- **Split:** before the split all texts live in `data/pool/`. A human runs
  `make split`, which writes `data/dev/` and `data/test/`, records checksums and
  empties the pool. From that moment you never open `data/test/`. Results on test
  are described as "evaluated once", never as "unseen data".
- **Linkage attack:** input = masked text + candidate list of N profiles
  (N = 10 and 25; true author + cohort look-alikes + random others, fixed by
  seed); output = ranked guess; metrics = top-1 and top-3. Headline privacy
  score = 1 − top-1 at N = 25. Always shown against `REF-none` and chance (1/N).
- **Attribute inference:** masked text only; guesses for city, profession,
  employer, age bracket, gender, presence of a health condition, each from a
  closed answer list, with no "unknown" option;
  accuracy against `REF-none` and the majority baseline. Gender is included
  because the placeholders deliberately reveal it.
- **The attacker prompt never contains gold labels or the configuration name.**
- **Utility:** T3 extraction (intent, amounts, dates, requested action, deadline)
  scored exactly per field after restoration; T1 reply draft scored by the judge
  (1–5 on correctness, completeness, Italian grammar) against the `REF-none`
  reply, blind to the configuration.
- **Judge validation (pre-declared):** two humans (Giuseppe and Mattia) rate 40 dev
  items blind: the 20 dev texts masked from gold spans with R1 and with R2. The
  judge is accepted if weighted κ ≥ 0.6 **or** agreement within ±1 point ≥ 85%;
  report both plus the score distribution. If rejected, humans score T1 on test
  only for contrast (2), as the fallback of the protocol says in section 9, and
  the failure is reported as a finding.
- **Statistics:** all comparisons paired on the same texts; 95% intervals by
  paired bootstrap (10,000 resamples, fixed seed); McNemar for paired binary
  outcomes; Holm correction across the three primary contrasts. With 46 test
  texts intervals are wide: state conclusions only where the decision rule of
  the protocol, section 12, supports them, and report negative results with
  the same prominence.
- **Cost guard:** before any batch of LLM calls, print the number of calls and
  the estimated cost and wait for Andrea's go-ahead. Team budget: about €10.

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; a proposed commit message; a proposed line for `docs/ai_use.md`. Then wait.
Do not stage, commit or push unless your human asks (shared rule 1).
