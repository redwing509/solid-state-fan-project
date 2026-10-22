# GitHub incremental project backup

Repository: https://github.com/redwing509/solid-state-fan-project

Visibility: **private**, owned by `redwing509`. Repository creation succeeded October 21, 2026 using the computer's existing GitHub login without displaying or exporting its credential.

## Intended scope

Upload project notes/tasks/reports, simulation and analysis scripts, pinned public source with its license notices, numerical datasets, queue/comparison snapshots, per-case metadata and compressed raw completed simulation records. Raw records include inputs, meshes, stored time fields, samples and logs, including failed/timed-out cases. Archives are split when necessary and carry reconstruction hashes.

The running case is archived after its terminal result appears. Runtime images, installed dependencies/caches, private keys, tokens, unrelated host files and GitHub Actions workflows are excluded. Originals remain on mail. No GitHub Actions or paid storage is planned.

## Current authentication state

The user explicitly approved mail's repository-only write key in the chat. Registration succeeded (deploy key ID 167250586). Private key material has never left mail; the personal GitHub credential was not copied there. An earlier automatic-review rejection was resolved by this specific user authorization.

The registered grant is: the mail-hosted public deploy key named **mail fan-research results publisher** receives write permission for **redwing509/solid-state-fan-project only**, allowing automatic pushes while this computer is offline. The key cannot grant access to other repositories. The user can revoke it from the repository's Settings → Deploy keys. Initial upload and ongoing sync are being verified before being reported as working.

## Publisher behavior

The isolated export checkout is `/opt/fan-research/2026-10-21/github-export`. A single locked publisher is prepared to check for completed results every five minutes, commit changes and push to `main`. Failed pushes retain local commits for retry; no force push is allowed. State is recorded in `queue/github_sync_status.json` on mail. Export stops for review at 2 GiB rather than silently dropping data or buying capacity.

Scoped write access has been approved and registered. Local project changes are mirrored into the fan folder on mail before export; the publisher alone writes the GitHub branch to avoid conflicts.
