

========== T1 full audit ==========
{"V1": "completed", "V2": "completed", "V3": "completed", "V4": "completed", "V5": "completed"}

# Blindspot report — 2026-10-24
Scope: xark

**Verdict:** 1 Critical, 2 High, 3 Medium, 1 Low, 1 Info. 452 KB recoverable.

| ID | Severity | File | Found | Evidence | Pass |
|---|---|---|---|---|---|
| V1-01 | Critical | Screenshots/IMG_2231.png | crypto recovery phrase | 12-word phrase | verified |
| V1-02 | High | Screenshots/IMG_2290.png | Wi-Fi password | Ch******4! | verified |
| V2-01 | High | Downloads/passport_scan.png | passport | number *****5678, expires 14 MAR 2031 | verified |
| V3-01 | Medium | Documents/lease_agreement.pdf | auto-renews 2026-11-30 at NGN 300,000/month | notice deadline 2026-10-31 (7 days left) | single-pass |
| V4-01 | Medium | Documents/invoices/INV-0092 (copy).pdf | duplicate invoice INV-0092 | same number and amount as INV-0092.pdf; 52 KB recoverable | single-pass |
| V4-02 | Medium | Documents/invoices/INV-0092.pdf | overcharge vs lease_agreement.pdf | expected NGN 250,000, invoiced NGN 275,000 | single-pass |
| V5-01 | Low | Photos/beach.jpg | 3 identical copies | 400 KB recoverable; copies: Photos/beach (1).jpg, Downloads/IMG_beach_copy.jpg | single-pass |
| V2-02 | Info | Vault/national_id.png | national ID card | number *******2101 | single-pass |

**House rules**
- ID scans live only in Vault: Broken (V2-01)
- No screenshots of passwords: Broken (V1-01, V1-02)

========== T2 empty/inaccessible scope ==========
STOP: no files found in scope (/workspace/projects/224119b7-4107-4b18-ae8f-164605e2f42a/ugreen/test/work/xark/Music: empty, /workspace/projects/224119b7-4107-4b18-ae8f-164605e2f42a/ugreen/test/work/xark/DoesNotExist: inaccessible). Nothing changed.

========== T3 V4 failed ==========
{"V1": "completed", "V2": "completed", "V3": "completed", "V4": "failed", "V5": "completed"}
**Not audited:** V4 (expert returned failed)

========== T4 unverified finding dropped ==========
# Blindspot report — 2026-10-24
Scope: xark

**Verdict:** 1 Critical. 0 KB recoverable.

| ID | Severity | File | Found | Evidence | Pass |
|---|---|---|---|---|---|
| V1-01 | Critical | Screenshots/IMG_2231.png | crypto recovery phrase | 12-word phrase | verified |

**Could not verify:** Screenshots/IMG_2290.png (file missing)

========== T5 re-run after approved fixes ==========
# Blindspot report — 2026-10-24
Scope: xark

**Verdict:** 3 Medium, 3 Low, 2 Info. 452 KB recoverable.

| ID | Severity | File | Found | Evidence | Pass |
|---|---|---|---|---|---|
| V3-01 | Medium | Documents/lease_agreement.pdf | auto-renews 2026-11-30 at NGN 300,000/month | notice deadline 2026-10-31 (7 days left) | single-pass |
| V4-01 | Medium | Documents/invoices/INV-0092 (copy).pdf | duplicate invoice INV-0092 | same number and amount as INV-0092.pdf; 52 KB recoverable | single-pass |
| V4-02 | Medium | Documents/invoices/INV-0092.pdf | overcharge vs lease_agreement.pdf | expected NGN 250,000, invoiced NGN 275,000 | single-pass |
| V5-01 | Low | Photos/beach.jpg | 3 identical copies | 400 KB recoverable; copies: Photos/beach (1).jpg, Downloads/IMG_beach_copy.jpg | single-pass |
| V1-01 | Low | Vault/IMG_2231.png | crypto recovery phrase | 12-word phrase | single-pass |
| V1-02 | Low | Vault/IMG_2290.png | Wi-Fi password | Ch******4! | single-pass |
| V2-01 | Info | Vault/national_id.png | national ID card | number *******2101 | single-pass |
| V2-02 | Info | Vault/passport_scan.png | passport | number *****5678, expires 14 MAR 2031 | single-pass |

**House rules**
- ID scans live only in Vault: Holding
- No screenshots of passwords: Broken (V1-01, V1-02)

**Since last scan**
- New: none
- Resolved: none
- Downgraded: V1-01 (Critical to Low), V1-02 (High to Low), V2-02 (High to Info)
- Still open: V3-01, V4-01, V4-02, V5-01, V2-01