# Blindspot

**Find what your files are hiding.**

Blindspot is an Uliya Skill for the UGREEN AI NAS. It runs a private, on-device audit of your NAS files and returns one report, ranked Critical to Info:

- **V1 Secrets in images**: seed phrases, passwords and Wi-Fi keys in screenshots and photos
- **V2 Identity and financial documents**: passports, ID cards and bank records left in open folders
- **V3 Contract deadlines**: leases and subscriptions about to auto-renew or expire
- **V4 Invoice mismatches**: invoices that overcharge against their contract, plus duplicate invoices
- **V5 Duplicate bloat**: copies wasting space

Every Critical and High finding is re-checked with a second read before it is reported; anything that can't be confirmed is dropped. Fixes (move to Vault, tag) run only after you approve them. Blindspot never deletes files and never sends file content off the NAS.

Built for the [UGREEN Hackathon 2026 on AI NAS](https://ugreenhackathon.devpost.com/), Open Innovation track.

## Repository

| Path | What it is |
|---|---|
| `blindspot/` | The Skill package: `SKILL.md` plus `references/` (audit vectors, severity rubric, report format, remediation, user guide) |
| `test/` | Local dry run: a seeded fixture NAS with planted risks and decoys, a harness that stands in for the NAS experts, and the test runner |
| `docs/` | Round 1 proposal (Markdown source and PDF) |

## Validate the Skill

With the official Uliya skill kit:

```bash
node uliya-skill-kit/scripts/check-skill.mjs blindspot
```

Expected: `static-pass`, 0 errors, 0 warnings.

## Dry run

Needs Python 3, `tesseract` and `pdftotext`.

```bash
cd test
python3 run_tests.py
```

Covers a full audit, an empty or missing scope, a failed expert, a finding dropped by verification, and a re-run after fixes. Output goes to `test/test-results.md`.

## Package for upload

```bash
zip -r blindspot.zip blindspot
```

Test data is synthetic. No real personal files are included.
