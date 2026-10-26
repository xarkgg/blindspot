# Report format

The report is plain Markdown so it reads well in chat and as a saved file.

## Sections, in order

1. Title: "Blindspot report" with the audit date and scope folders.
2. Verdict: one line with counts per severity and recoverable space, for example "2 Critical, 3 High, 5 Medium, 1 Low. 4.2 GB recoverable."
3. Surface map: file counts and sizes by type from Step 1.
4. Findings table, ordered by the severity rubric:

| ID | Severity | Vector | File | Found | Why it matters | Fix | Pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V1-01 | Critical | Secrets | Screenshots/IMG_2231.png | Seed phrase (ab\*\*\*\*yz) | Anyone with this file can empty the wallet | Move to Vault and tag blindspot-critical | verified |

5. House rules: each rule with status Holding, Broken (finding IDs), or Not checked.
6. Since last scan (re-runs only): match findings by file name and finding type, ignoring folder, then list New, Resolved (gone), Downgraded (same file, lower severity, for example moved into the vault), and Still open with the same severity. Each as a list of finding IDs.
7. Not audited: vectors that failed or were cancelled, with the reason.
8. Could not verify: findings dropped in Step 4, with the reason.
9. Fixes applied: only actions the experts returned as completed, with real results.

## House rules

House rules are the user's own invariants: short statements that should always be true about their files. Blindspot checks each rule against the findings of the current run.

- "ID scans live only in Vault" is Broken when any V2 finding is outside the Vault folder.
- "No screenshots of passwords" is Broken when any V1 finding exists.
- "No contract renews without me knowing" is Broken when any V3 finding renews within 30 days.

A rule that no completed vector covers is marked Not checked, never Holding.

Rules are written into the saved report so the next run can read them back during re-run comparison.
