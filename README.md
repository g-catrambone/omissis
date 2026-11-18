# Omissis

A local tool that sits between a user and a cloud LLM. For Italian text it detects
sensitive spans, replaces them with pseudonyms, sends the pseudonymised text to the
model, restores the real values in the reply and reports what was disclosed.

The contribution is the measurement: what each configuration costs in privacy
(re-identification risk against an attacker LLM) and in answer quality.
Omissis pseudonymises; it does not make text anonymous. All data in this
repository is synthetic.

Team project for *AI Frontiers: Large Language Models* (LUISS, fall 2026).

## Status

The whole pipeline, the five detectors, the app and the evaluation code are on
`main` (18 Nov 2026). No result is reported yet: the 66 synthetic texts are being
reviewed and the evaluation has not run. What is left is in `docs/TODO.md`.

## Quick start

Requires [`uv`](https://docs.astral.sh/uv/). Python 3.11 is installed by `uv`.

```
make setup   # create the environment from uv.lock
make test    # run the tests
make lint    # ruff check and format check
```

Specifications: `docs/interfaces.md` (contracts, functions, files) and
`docs/evaluation_protocol.md` (data and reported numbers).

## AI assistance

Code, tests and first drafts of documents are produced with AI coding agents
(Claude Code); every change is reviewed and merged by a team member.
Each task's AI use is recorded in `docs/ai_use.md`.
