# Remediation playbook

Fixes are offered per finding group and applied only after the user approves that group. Blindspot never deletes files.

| Finding | Suggested fix | Capability used |
| --- | --- | --- |
| V1 secret in image (Critical, High) | Move the image to a private "Vault" folder chosen by the user and tag it blindspot-critical. Suggest the user change the exposed password or move funds; Blindspot cannot do that for them. | file-workflow batch-move, ug-filemgr tag-add-file |
| V2 identity or financial document (High) | Move to the Vault folder and tag it blindspot-identity. | file-workflow batch-move, ug-filemgr tag-add-file |
| V3 contract deadline (Medium) | Tag the contract blindspot-deadline and list the date in the report so the user can act. | ug-filemgr tag-add-file |
| V4 invoice mismatch (Medium) | Tag both documents blindspot-check-invoice. | ug-filemgr tag-add-file |
| V5 duplicates (Low) | Move extra copies to a "Duplicates to review" folder, keeping the newest copy in place. The user deletes them later if they wish. | file-workflow batch-move |

## Approval wording

Before each group, show:

- The exact files (real paths), the destination folder or tag, and the count.
- "Nothing will be deleted. You can move these back at any time."

Ask for a yes or no for that group only. A yes for one group never approves another group.

## After fixes

- Report the real result from the expert: total, succeeded, failed, new paths.
- If any move failed, list those files and leave them as open findings.
- Offer a re-run of Blindspot to confirm the findings are resolved.
