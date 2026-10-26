# Audit vectors

Blindspot splits the audit into five independent vectors, the way a security review splits a codebase into attack surfaces. Each vector has one owner expert, a fixed question, and a fixed evidence format.

| ID | Vector | Owner | Question it answers |
| --- | --- | --- | --- |
| V1 | Exposed secrets in images | photo-agent | Is any password, code, seed phrase, or card number visible in a screenshot or photo? |
| V2 | Identity and financial documents | document-agent, photo-agent | Are ID, bank, tax, payslip, or medical records sitting in open folders? |
| V3 | Contract obligations | document-agent | Which contracts end, renew, or pass a notice deadline in the next 90 days? |
| V4 | Money leaks | document-agent | Do invoices match their contracts? Any duplicates or charges after the end date? |
| V5 | Storage bloat | file-agent | How much space is lost to duplicate copies? |

## Evidence format

Every finding returned by a pass must contain:

- Finding ID: vector plus a running number, for example V1-03.
- File: the real path returned by the expert. Never a guessed or shortened path.
- What: the type of item found (for example "Wi-Fi key in screenshot", "passport scan", "lease auto-renews").
- Evidence: the exact excerpt or field values returned by the capability, with secrets and ID numbers masked.
- Date: capture date, document date, or deadline, as returned.
- Pass: single-pass or verified (after Step 4).

A finding without a real file path and real evidence is not a finding and must not be reported.

## Masking rules

- Passwords, codes, Wi-Fi keys: first two and last two characters with a fixed run of six stars, for example "hu\*\*\*\*\*\*42", so the mask never reveals the length.
- Seed or recovery phrases: word count only, for example "12-word phrase". Never show any word.
- ID, passport, card, and account numbers: last four characters only, for example "\*\*\*\*\*\*7731".
- Names of the document holder may be shown, because the user needs them to recognise the file.

## Vector notes

- V1 searches screenshots and OCR text first, then confirms each candidate with OCR on the single file. Photos of whiteboards or notes count when they contain credentials.
- V2 reports location risk, not the document's existence. A passport scan inside a folder the user marked as a vault in house rules is reported as Info, not High.
- V3 uses today's date as the reference. Deadlines already passed are reported as Medium with "missed" in the reason.
- V4 treats a duplicate invoice as a money risk (it could be paid twice) and reports it in V4, not V5. When two files are identical, the oldest file or the one without "copy" in its name is the original; findings about content (such as an overcharge) point to the original, and the duplicate finding points to the extra copy.
- V4 compares amounts in the same currency only. If currencies differ, report the pair as Low with "currency mismatch, not compared".
- V5 never recommends which copy to delete. It only recommends moving extra copies to a review folder.
