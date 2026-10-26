---
title: "Blindspot — Proposal"
subtitle: "UGREEN Hackathon 2026 on AI NAS · Track: Explore Your Imagination (Open Innovation)"
---

**Entrant:** Manass Kusko (individual) · **Skill package:** blindspot.zip

**1. What does the Skill do?**
Blindspot runs a private security and hygiene audit of your NAS files and returns a severity-ranked findings report with file-level evidence and one-tap, approval-gated fixes.

**2. Target user and problem**
Households, freelancers and small offices whose NAS has become a dumping ground. Seed-phrase screenshots, passport scans in Downloads, leases that silently auto-renew and invoices that overcharge sit unnoticed until they cost money. Nobody audits their own files.

**3. Proposed solution**
Apply a professional security-audit method to personal data: scope the surface, run independent expert passes per risk vector, verify every serious finding with a second read, rank by a fixed rubric, then fix only what the user approves.

**4. Core user flow**
"Check my Documents folder for blind spots" → confirm scope → surface map → five audit passes → verification of Critical/High findings → ranked report in chat → save report (approval) → approve fixes per group (move to Vault, tag) → later "run Blindspot again" shows new, resolved and still-open findings.

**5. Difference from existing tools**
Dedupe tools find copies; AI chat answers questions. Neither audits. Blindspot borrows smart-contract audit practice: attack vectors, a severity rubric, false-positive filtering by re-verification, user-defined invariants ("house rules") checked every run, and regression diffs between runs. Secrets are masked and nothing leaves the device.

**6. NAS capabilities and where**
Scope: file-workflow get-user-dir, ug-filesystem ls/find/category. V1 secrets: ug-photo search-screen, vision-ocr. V2 IDs/finance: ug-document qa/extract, ug-photo card search. V3 contracts: ug-document extract (contract schema). V4 money leaks: ug-document extract (invoice) and reconcile. V5 bloat: ug-filemgr scan-dedupe. Report: ug-knowledge save-text. Fixes: ug-filesystem mkdir, file-workflow batch-move, ug-filemgr tag-add-file.

**7. Technical approach**
Pure orchestration Skill (SKILL.md plus four references) delegating to file-agent, document-agent, photo-agent and knowledge-agent. Passes are independent and parallelisable; each returns a fixed evidence format (real path, masked excerpt, date). Downstream steps use only real upstream results. All five delegation states are handled; empty results are reported and stopped, never substituted. All writes require approval; nothing is ever deleted. Uses the NAS local AI only; no external services or data transfer.

**8. Development status**
Implemented: complete Skill package, severity rubric, audit-vector spec, report format, remediation playbook. Passes the official kit checker with zero errors and warnings. A local dry run on a seeded test folder caught all 8 planted risks with 0 false positives on 4 decoys. Pending: on-device accuracy of UGREEN OCR and extraction.

**9. Validation plan**
Test 1: seeded folder with a seed-phrase screenshot, passport scan and duplicate photos; expect two Critical/High verified findings and correct recoverable space. Test 2: lease plus three invoices, one overcharged; expect V3 renewal flag and V4 mismatch. Edge case: empty or inaccessible folder; expect a clear "no files in scope" stop with no changes.

**10. Known limitations**
Detection quality depends on on-device OCR and document extraction accuracy. Cannot rotate passwords or change sharing permissions, only advise. Very large scopes may take long; users can audit a subset of vectors. Non-Latin documents untested.

---

**Data flows and third parties:** None. The Skill uses only UGOS capabilities and the NAS local AI; no file content leaves the device. Testing used synthetic files only.

**AI tools used:** Hark (AI assistant) helped draft and debug the Skill files and proposal text, run the official checker, and build synthetic test files. I chose the idea and design and reviewed everything.

**Declaration:** This Skill and its materials are my original work, developed during the Hackathon period.
