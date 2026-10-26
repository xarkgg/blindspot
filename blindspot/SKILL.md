---
name: blindspot
description: Private, on-device security and hygiene audit of personal files on the NAS, producing a severity-ranked findings report (Critical to Info) with file-level evidence and optional, confirmed fixes. Covers exposed secrets in screenshots and photos, identity and financial documents left in open folders, contracts nearing expiry or auto-renewal, invoices that do not match their contracts, and duplicate bloat. Use when the user says things like "find my blind spots", "audit my NAS", "is anything sensitive lying around", "check my Documents folder for risks", "what contracts are about to renew", or "run Blindspot again and compare with last time".
---

# Goal

Give the user a clear, evidence-backed answer to one question: "What in my files could hurt me, cost me money, or waste my space, and what should I do about it?"

Blindspot borrows the method of a professional security audit and applies it to a household or small-office NAS:

1. Scope and map the attack surface (which folders, how many files, what kinds).
2. Run independent audit passes, one per risk vector, each owned by the expert that is best at it.
3. Verify every Critical and High finding with a second, focused read before it is reported. A finding that cannot be confirmed is dropped, not guessed.
4. Rank findings by severity with a fixed rubric, explain impact in plain language, and propose a fix.
5. Save the report on the NAS and apply only the fixes the user explicitly approves.

All analysis runs through the NAS experts on the user's own device. Blindspot never sends file content outside the NAS, never deletes files, and never changes anything without the user's confirmation.

For a plain-language overview to share with the user, see [user guide](references/user-guide.md).

Supported scope: folders the user can access on this NAS, plus the user's photo library. Out of scope: other users' private spaces, network or account security settings, and anything not covered by the capability evidence below.

# Required input

Collect only what the parent workflow needs:

- Audit scope: one or more folders to audit. If the user does not name a folder, offer the user's own home directory (resolved by file-agent in Step 1) and wait for confirmation.
- Audit vectors: all five by default (V1 to V5, see [audit vectors](references/audit-vectors.md)). The user may choose a subset, for example "only contracts" or "only screenshots".
- Photo library: whether to include the user's photo library for V1 and V2. Default is yes when the user has a photo library; ask once.
- Report folder: where to save the report. Default is a folder named "Blindspot Reports" inside the audited scope root; confirm before the first save.
- House rules (optional): up to five plain-language rules the user wants to stay true, for example "ID scans live only in Vault" or "no screenshots of passwords". These are re-checked on every future run. See [report format](references/report-format.md).

Do not ask for passwords, account details, or any credential. Do not pre-collect parameters that a child expert resolves on its own.

# Generation-time capability evidence

- `ug-filesystem` → `file-agent`
- `ug-filemgr` → `file-agent`
- `file-workflow` → `file-agent`
- `ug-document` → `document-agent`
- `ug-photo` → `photo-agent`
- `ug-knowledge` → `knowledge-agent`

# Capability map

Actions relied on, by step:

- Step 1 scope and map: file-workflow get-user-dir, ug-filesystem ls, find, category, stat (read only).
- V1 exposed secrets: ug-photo search-screen (screen and ocr categories), vision-ocr, meta (read only).
- V2 identity and financial documents: ug-photo search-screen (card category), ug-document qa and extract, ug-filesystem find (read only).
- V3 contract obligations: ug-document extract with the contract schema, qa (read only).
- V4 money leaks: ug-document extract with the invoice schema, reconcile (read only).
- V5 storage bloat: ug-filemgr scan-dedupe, ug-filesystem stat (read only).
- Step 4 verification: ug-photo vision-ocr, ug-document qa (read only).
- Step 6 save report: ug-filesystem mkdir, ug-knowledge save-text (state change, approval required).
- Step 7 fixes: ug-filesystem mkdir, file-workflow batch-move, ug-filemgr tag-add and tag-add-file (state change, approval required).
- Re-run comparison: ug-filesystem find and ug-document qa on the previous report file (read only).

# Workflow

Run the steps in order. Each step uses only the real result returned by the previous step. If a step returns nothing usable, follow the empty-result rule for that step and do not substitute similar or unrelated data.

## Step 1. Confirm scope and map the surface

If the user did not name a folder, resolve the default first:

delegate --target file-agent --instruction 'Return the real home directory path and fileId of the current user. Read only. If no home directory is available, return an empty result and say so.'

Show the resolved path and ask the user to confirm or change the scope. Then map it, passing the exact confirmed folder paths in the instruction:

delegate --target file-agent --instruction 'For each folder path the user confirmed for this Blindspot audit (listed in this instruction by the parent), return a read-only inventory: total file count, total size, counts and sizes by category (documents, images, videos, audio, archives, other), the 20 largest files with real paths and sizes, and the oldest and newest modification dates. Do not open file contents. Do not change anything. If a folder does not exist, is empty, or is not accessible, report that folder as empty or inaccessible and continue with the others.'

Empty result: if every confirmed folder is empty or inaccessible, tell the user no files were found in scope, and stop. Do not widen the scope on your own.

Show the user a short map (file counts by type, total size) so they see what will be audited.

## Step 2. Run the audit passes

Run the selected vectors. They are independent, so they may run in parallel. Each pass must return findings in the evidence format described in [audit vectors](references/audit-vectors.md): real file path, what was found, the exact evidence returned by the capability, and the date it was found. Each instruction below is sent with the confirmed folder paths written into it by the parent.

V1. Exposed secrets in images:

delegate --target photo-agent --instruction 'Within the folders confirmed for this Blindspot audit and, if the user agreed, the user photo library, find screenshots and photos whose recognized text contains credentials or recovery material: passwords, one-time codes, PIN codes, card numbers with CVV, bank account and routing numbers, crypto seed or recovery phrases, two-factor backup codes, or Wi-Fi keys. Use screenshot and OCR search first, then run OCR on each candidate to confirm. For each confirmed hit return the real file path, the type of secret, a masked excerpt (for passwords and codes the first two and last two characters around six stars; for seed or recovery phrases only the word count), and the capture date. Never return a full secret value. Read only. If nothing matches, return an empty list and say no exposed secrets were found.'

V2. Identity and financial documents in open folders:

delegate --target document-agent --instruction 'Within the folders confirmed for this Blindspot audit, identify documents that are identity or high-value financial records: passports, national ID cards, driver licences, birth certificates, bank statements, tax returns, payslips, loan agreements, and medical reports. Use document question answering and extraction on candidate documents. For each hit return the real file path, the document type, the holder name if present, any expiry date, and a one-line reason. Do not return full ID numbers or account numbers; mask all but the last four characters. Read only. If nothing matches, return an empty list and say no identity or financial documents were found.'

When the photo library is included, also run:

delegate --target photo-agent --instruction 'In the user photo library and the folders confirmed for this Blindspot audit, find photos recognized as cards or documents, such as ID cards, passports, bank cards, and licences. For each hit return the real file path, the recognized card or document type, and the capture date. Mask any number to its last four characters. Read only. If nothing matches, return an empty list and say no card or document photos were found.'

V3. Contract obligations:

delegate --target document-agent --instruction 'Within the folders confirmed for this Blindspot audit, find contracts, leases, subscriptions, and service agreements. Extract with the contract schema: parties, start date, end date, auto-renewal clause, notice period, renewal price or fee, and termination conditions. Return every contract with its real file path and these fields, and flag contracts that end, renew, or pass their notice deadline within the next 90 days from today. Read only. If no contracts are found, return an empty list and say no contracts were found.'

V4. Money leaks:

delegate --target document-agent --instruction 'Within the folders confirmed for this Blindspot audit, find invoices and receipts and the contracts or quotes they relate to. Extract invoices with the invoice schema, then reconcile each invoice against its matching contract or quote. Report mismatched amounts, duplicate invoices with the same number or amount and date, charges after a contract end date, and invoices with no matching contract. For each finding return the real file paths of both documents, the expected and actual amounts with currency, and the reason. Read only. If there are no invoices, or no mismatches, return an empty result and say so.'

V5. Storage bloat:

delegate --target file-agent --instruction 'Within the folders confirmed for this Blindspot audit, scan for duplicate files across all file types. Return each duplicate group with real file paths, size per copy, modification dates, and the space that would be recovered by keeping one copy. Also return the total recoverable space. Read only; do not delete, move, or rename anything. If no duplicates are found, return an empty result and say no duplicates were found.'

Partial results: if one pass fails or is cancelled, keep the results of the passes that completed, record the failed vector as "not audited" in the report, and continue. Never report a vector as clean when it did not complete.

## Step 3. Triage

Combine the real findings from Step 2. Assign each finding one severity using the fixed rubric in [severity rubric](references/severity-rubric.md), including the vault rule. Merge findings that point to the same file for the same risk, for example a duplicate invoice found by both V4 and V5 is reported once under V4. Do not add findings that no pass returned.

If every completed pass returned an empty result, skip to Step 5 and report a clean result for the vectors that ran.

## Step 4. Verify before reporting

Every Critical and High finding gets a second, focused read of that single file before it appears in the report. Send one instruction per file with its real path from Step 2 written in.

For an image finding:

delegate --target photo-agent --instruction 'Run OCR on the single image file whose real path the parent includes in this instruction and answer only: does the recognized text contain the secret type named in this instruction? Reply yes or no, with a masked excerpt (first two and last two characters around six stars, or only the word count for a seed or recovery phrase). Read only. If the file no longer exists or OCR returns no text, return an empty result and say so.'

For a document finding:

delegate --target document-agent --instruction 'Read the single document whose real path the parent includes in this instruction and answer only: is this document the type and does it contain the date, amount, or clause named in this instruction? Reply yes or no and quote the shortest supporting passage, masking ID and account numbers to their last four characters. Read only. If the file no longer exists or cannot be read, return an empty result and say so.'

Rules:

- Confirmed: keep the finding and attach the verification excerpt as evidence.
- Not confirmed, file missing, or unreadable: drop the finding from the ranked list and list it under "Could not verify" with the reason. Never upgrade or invent evidence.

Medium, Low, and Info findings are reported with the evidence from Step 2 and labelled "single-pass".

## Step 5. Present the report

Show the report in chat first, using the structure in [report format](references/report-format.md):

- One-line verdict, for example "2 Critical, 3 High, 5 Medium. 4.2 GB recoverable."
- Findings table ordered by severity: ID, severity, vector, file, what was found, why it matters, suggested fix.
- House rules status: each rule as Holding, Broken (with the finding IDs), or Not checked.
- Vectors not audited, and findings that could not be verified.
- If a previous report exists, a "Since last scan" section: new, resolved, downgraded, and still-open findings.

Secrets and ID numbers always stay masked in the report.

## Step 6. Save the report (approval required)

Ask: "Save this report to the report folder?" Show the target folder. Only after the user confirms:

delegate --target file-agent --instruction 'Create the folder named Blindspot Reports inside the scope root path the parent includes in this instruction, if it does not already exist. Return the real folder path. This is a state change and requires user approval through the gateway. If creation is refused or fails, return the reason.'

Then pass the real folder path returned above, and the exact report text shown in Step 5, to:

delegate --target knowledge-agent --instruction 'Save the Markdown report text included in this instruction as a new file in the folder path included in this instruction, using the filename hint blindspot-report followed by the audit date. Do not overwrite an existing file. Return the verified output file path and size. This is a state change and requires user approval.'

If the user declines, do not save, and tell the user the report exists only in this conversation.

## Step 7. Apply fixes (each group approved separately)

Offer fixes from [remediation playbook](references/remediation.md), grouped by finding. Never delete files. For each group the user approves, send one instruction with the real file paths from the verified findings written in:

delegate --target file-agent --instruction 'Move the files whose real paths the parent includes in this instruction into the destination folder included in this instruction, creating the destination folder first if it does not exist. Keep original file names; if a name already exists at the destination, keep both by adding a date prefix. Do not delete anything. Return the real result: total, succeeded, failed, and the new path of each moved file. This is a state change and requires user approval.'

delegate --target file-agent --instruction 'Add the tag named in this instruction to each file whose real path the parent includes in this instruction, creating the tag first if it does not exist. Do not change file contents or locations. Return which files were tagged and any failures. This is a state change and requires user approval.'

After fixes, report exactly what changed, using the real results. Offer to re-run Blindspot on the same scope to confirm the findings are resolved.

## Re-run and compare

When the user asks to run Blindspot again, first look for the most recent previous report:

delegate --target file-agent --instruction 'Find files whose names start with blindspot-report inside the folder named Blindspot Reports under the scope root path the parent includes in this instruction. Return the real path and modification date of the most recent one. Read only. If none is found, return an empty result and say no previous report was found.'

If one is found, read its findings and house rules:

delegate --target document-agent --instruction 'Read the previous Blindspot report at the real path the parent includes in this instruction and return its audit date, house rules, and the list of findings with ID, severity, vector, and file path. Read only. If the file cannot be read, return an empty result and say so.'

Then run Steps 1 to 5 as normal and compare. If no previous report is found, run a fresh audit and say there is nothing to compare against.

# Completion and failure

Handle every delegation state explicitly:

- completed: use only the real data returned. An empty result is a valid outcome; report it plainly ("no exposed secrets were found in the 1,240 images scanned") and stop that branch.
- failed: tell the user which step or vector failed and the reason the expert gave. Keep results from other completed steps. Mark the vector "not audited". Do not retry with a wider or different scope without asking.
- cancelled: stop the cancelled step and every step that depends on it. Report what was completed before cancellation.
- waiting_user: relay the expert question to the user in plain words, wait for the answer, and pass it back unchanged.
- waiting_approval: tell the user exactly what will change (folder created, files moved, tags added, report saved), wait for the gateway decision, and continue only when approved. If approval is denied, report that nothing was changed for that action.

The audit is complete when the report has been shown to the user. Saving and fixes are optional follow-ups. Never claim a file was moved, tagged, or saved unless the expert returned completed with real output for that action. Do not run any command directly; never use cli.invoke from this Skill; all NAS work goes through the experts above.
