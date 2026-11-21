# Reviewers

Fixed by seed (`python -m omissis.eval.review assign`). The reviewer reads each
text as tagged text (`python -m omissis.eval.textgen export` and `import`) and
writes their initials in `reviewed_by` by hand. The 13 texts with a name in the
last column are first annotated from plain text, with no tag visible, and
`python -m omissis.eval.review agreement` is run before any of them is reviewed
(`docs/evaluation_protocol.md`, section 3).

Since 21 Nov the review and the blind annotation are done by the AI agent of the
member named here, who approves them on its report: his initials in `reviewed_by`
record the approval, and the annotated copies are `<text_id>.AI.txt`
(`docs/decisions.md`).

| Text | Reviewer | Blind annotation first |
|---|---|---|
| bank-0001 | Giuseppe |  |
| bank-0002 | Giuseppe |  |
| bank-0003 | Giuseppe | Giuseppe |
| bank-0004 | Giuseppe |  |
| bank-0005 | Giuseppe |  |
| bank-0006 | Giuseppe |  |
| bank-0007 | Giuseppe | Giuseppe |
| bank-0008 | Giuseppe |  |
| bank-0009 | Giuseppe | Giuseppe |
| bank-0010 | Giuseppe |  |
| bank-0011 | Giuseppe |  |
| bank-0012 | Giuseppe |  |
| bank-0013 | Giuseppe |  |
| bank-0014 | Giuseppe |  |
| bank-0015 | Giuseppe |  |
| bank-0016 | Giuseppe |  |
| bank-0017 | Giuseppe |  |
| bank-0018 | Giuseppe |  |
| bank-0019 | Giuseppe | Giuseppe |
| bank-0020 | Giuseppe |  |
| bank-0021 | Giuseppe |  |
| bank-0022 | Giuseppe | Giuseppe |
| bank-0023 | Giuseppe |  |
| bank-0024 | Giuseppe |  |
| bank-0025 | Giuseppe |  |
| bank-0026 | Giuseppe | Giuseppe |
| bank-0027 | Giuseppe |  |
| bank-0028 | Giuseppe | Giuseppe |
| bank-0029 | Giuseppe |  |
| bank-0030 | Giuseppe | Giuseppe |
| bank-0031 | Giuseppe |  |
| bank-0032 | Giuseppe |  |
| bank-0033 | Giuseppe |  |
| bank-0034 | Giuseppe |  |
| bank-0035 | Giuseppe |  |
| bank-0036 | Giuseppe |  |
| bank-0037 | Giuseppe |  |
| bank-0038 | Giuseppe |  |
| bank-0039 | Giuseppe |  |
| bank-0040 | Giuseppe |  |
| hr-0001 | Giuseppe |  |
| hr-0002 | Giuseppe |  |
| hr-0003 | Giuseppe |  |
| hr-0004 | Giuseppe |  |
| hr-0005 | Giuseppe | Giuseppe |
| hr-0006 | Giuseppe |  |
| hr-0007 | Giuseppe |  |
| hr-0008 | Giuseppe |  |
| hr-0009 | Giuseppe |  |
| hr-0010 | Giuseppe |  |
| hr-0011 | Giuseppe |  |
| hr-0012 | Giuseppe | Giuseppe |
| hr-0013 | Giuseppe |  |
| hr-0014 | Giuseppe |  |
| hr-0015 | Giuseppe |  |
| hr-0016 | Giuseppe |  |
| hr-0017 | Giuseppe | Giuseppe |
| hr-0018 | Giuseppe |  |
| hr-0019 | Giuseppe | Giuseppe |
| hr-0020 | Giuseppe |  |
| hr-0021 | Giuseppe |  |
| hr-0022 | Giuseppe | Giuseppe |
| hr-0023 | Giuseppe |  |
| hr-0024 | Giuseppe |  |
| hr-0025 | Giuseppe |  |
| hr-0026 | Giuseppe |  |
