# Decision log

Decisions that change behaviour or scope. One entry per decision, newest last.
Agents propose entries; a human adds them.

| Date | Decision | Reason | Agreed by |
|---|---|---|---|
| 2026-11-11 | Reduced scope: 4 evaluated configurations plus references, 66 texts, T3 and T1 only (see `Linee_Guida_Progetto.pdf`, Appendix A) | Three members, about 40 hours each | Giuseppe (to be confirmed by Mattia and Andrea) |
| 2026-11-11 | Project renamed from "Privacy Shield" to "Omissis" | Clash with the annulled EU–US framework and with an existing tool | Giuseppe (to be confirmed by Mattia and Andrea) |
| 2026-11-11 | Evaluation protocol v1: scenarios and counts, closed answer spaces for attribute inference and extraction, matching rules, judge acceptance rule (`docs/evaluation_protocol.md`) | Definitions fixed before any data is seen, so results cannot steer them | Giuseppe (to be confirmed by Mattia and Andrea) |
| 2026-11-11 | `Span.cls` is derived from `Span.type` instead of being stored | The two can never disagree | Giuseppe (to be confirmed by Mattia and Andrea) |
| 2026-11-11 | All LLM calls, including the local D3 model, go through `backends.complete`; the local runtime is a provider registered by workstream A | One cache, one replay path, clean path ownership | Giuseppe (to be confirmed by Mattia and Andrea) |
