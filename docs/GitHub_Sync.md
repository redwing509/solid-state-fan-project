# Solid State Fan Project — GitHub sync

Repository: https://github.com/redwing509/solid-state-fan-project

Visibility: **public** (at the user’s explicit request), owned by `redwing509`. Repository creation succeeded October 21, 2026 using the computer's existing GitHub login without displaying or exporting its credential.

## Intended scope

Upload project notes/tasks/reports, simulation and analysis scripts, pinned public source with its license notices, numerical datasets, queue/comparison snapshots, per-case metadata and compressed raw completed simulation records. Raw records include inputs, meshes, stored time fields, samples and logs, including failed/timed-out cases. Archives are split when necessary and carry reconstruction hashes.

The running case is archived after its terminal result appears. Runtime images, installed dependencies/caches, private keys, tokens, unrelated host files and GitHub Actions workflows are excluded. Originals remain on mail. No GitHub Actions or paid storage is planned.

## Current authentication state

The user explicitly approved mail's repository-only write key in the chat. Registration succeeded (deploy key ID 167250586). Private key material has never left mail; the personal GitHub credential was not copied there. An earlier automatic-review rejection was resolved by this specific user authorization.

The registered grant is: the mail-hosted public deploy key named **mail fan-research results publisher** receives write permission for **redwing509/solid-state-fan-project only**, allowing automatic pushes while this computer is offline. The key cannot grant access to other repositories. The user can revoke it from the repository's Settings → Deploy keys. Initial upload succeeded: 205 completed queue cases plus the original baseline and project records, commit `ce5dd97e6f7f9559cd01831dac96dc73c539c73c`, verified against GitHub main at 2026-10-22 01:18 UTC. New results continue to accumulate.

## Publisher behavior

The isolated export checkout is `/opt/fan-research/2026-10-21/github-export`. A single locked publisher is running and checks for completed results every five minutes, commit changes and push to `simulation-results`. Failed pushes retain local commits for retry; no force push is allowed. State is recorded in `queue/github_sync_status.json` on mail. Export stops for review at 2 GiB rather than silently dropping data or buying capacity.

Scoped write access has been approved and registered. Local project changes are mirrored into the fan folder on mail before export; the publisher alone writes the GitHub branch to avoid conflicts.

The recurring publisher checks every five minutes and survives chat/SSH closure or this PC going offline. It is not installed to start after a VPS reboot; the hourly monitor checks for unexpected stops. The repository was renamed at the user’s request to **Solid State Fan Project**, slug `solid-state-fan-project`; its repository ID and scoped deploy key were preserved. Existing computer authentication supports repository management, and mail has repository-only push access. No broader server credential was granted.

## Public contributions

The user requested public participation with validation before inclusion. Outside contributions use issues or fork pull requests. Protected main requires an approving owner review, dismisses stale approvals and requires resolved discussions. CODEOWNERS names @redwing509 for all files. No bypass is granted to the mail deploy key; the uploader instead writes the separate simulation-results evidence branch. Submitted code is never executed automatically. CONTRIBUTING.md and VALIDATION.md define the intake and evidence review. Previously uploaded snapshots remain labeled research evidence rather than experimentally validated designs.

Verified October 21, 2026 (Pacific): repository API reports public visibility; main ruleset 25606775 is active, has no bypass actors, requires one approving code-owner review, dismisses stale approvals, resolves review threads, and blocks branch deletion and non-fast-forward updates. The existing server publisher was moved to simulation-results. Historical main snapshots include earlier research evidence and do not retroactively acquire validation.

## Batch terminal backup

All 314 terminal queue records were backed up, verified against remote simulation-results commit 334f55e2990c4e2a8ed1f029aae7ecf8bd541e66 before this note update. The publisher completed its three terminal refreshes and exited normally. A one-off final documentation refresh may advance the branch. It will not run continuously after this completed batch. The hourly batch monitor is paused once that final backup is verified. No main promotion or protection change is authorized by a result upload.
