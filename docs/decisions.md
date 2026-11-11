# Decision log

Decisions that change behaviour or scope. One entry per decision, newest last.
Agents propose entries; a human adds them.

| Date | Decision | Reason | Agreed by |
|---|---|---|---|
| 2026-11-11 | Reduced scope: 4 evaluated configurations plus references, 66 texts, T3 and T1 only (see `Linee_Guida_Progetto.pdf`, Appendix A) | Three members, about 40 hours each | Giuseppe, Mattia, Andrea |
| 2026-11-11 | Project renamed from "Privacy Shield" to "Omissis" | Clash with the annulled EU–US framework and with an existing tool | Giuseppe, Mattia, Andrea |
| 2026-11-11 | Evaluation protocol v1: scenarios and counts, closed answer spaces for attribute inference and extraction, matching rules, judge acceptance rule (`docs/evaluation_protocol.md`) | Definitions fixed before any data is seen, so results cannot steer them | Giuseppe, Mattia, Andrea |
| 2026-11-11 | `Span.cls` is derived from `Span.type` instead of being stored | The two can never disagree | Giuseppe, Mattia, Andrea |
| 2026-11-11 | All LLM calls, including the local D3 model, go through `backends.complete`; the local runtime is a provider registered by workstream A | One cache, one replay path, clean path ownership | Giuseppe, Mattia, Andrea |
| 2026-11-11 | B0 merged as one pull request (about 1600 lines including `uv.lock`), a declared exception to the ~300-line rule | The foundation cannot be split without stacked branches | Giuseppe |
| 2026-11-11 | `run_id` hashes detector, strategy, mask_quasi, seed, fuzzy_threshold, source_priority and the resolved models (provider, id, revision per role); it excludes backend, cache_dir and the models_file path | A run and its replay from the cache must share one run id, so `make reproduce` finds the original results | Giuseppe, Mattia, Andrea |
| 2026-11-11 | `Span` enforces `source` in DetectorId or `GOLD`, and a non-empty `reason` when `source` is D3 | Contract violations fail when the span is built, not later in the pipeline | Giuseppe, Mattia, Andrea |
