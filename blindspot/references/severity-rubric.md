# Severity rubric

One fixed rubric so that two runs on the same files give the same ranking. Pick the highest level whose condition is met.

| Severity | Condition | Examples |
| --- | --- | --- |
| Critical | A secret that gives direct access to money or accounts is readable in a file. | Crypto seed phrase screenshot; photo of a bank card with CVV; screenshot of a password manager master password; two-factor backup codes. |
| High | Identity or financial records in a folder that is not covered by a vault house rule, or a secret that gives access to a non-financial account. | Passport or national ID scan in Downloads; bank statements in a shared folder; Wi-Fi or email password screenshot. |
| Medium | A money or deadline risk with a date or amount attached. | Lease auto-renews in 21 days; invoice is higher than the contract amount; notice deadline already missed; duplicate invoice. |
| Low | A housekeeping issue with no direct harm. | Duplicate photos using 3 GB; expired ID kept in an open folder; currency mismatch not compared. |
| Info | Noted for completeness; no action needed. | Passport scan correctly stored inside the vault folder; contract with no renewal clause. |

## Ordering inside a level

1. Verified before single-pass.
2. Earlier deadline first (V3, V4).
3. Larger recoverable space first (V5).

## Vault rule

When the user named a vault folder in house rules, a V1 or V2 finding inside that folder is deliberate storage, not exposure:

- V2 inside the vault: Info.
- V1 inside the vault: Low, with the advice to keep secrets in a password manager instead of images.

## One finding per file and risk

If V4 and V5 both point at the same duplicate invoice, keep the V4 finding and mention the recoverable space in its evidence. Do not list the same file twice for the same problem.

## What never changes severity

- File size or age does not raise severity on its own.
- The number of copies raises severity only for V1 and V2 (two copies of a seed phrase is still Critical, and both files are listed).
