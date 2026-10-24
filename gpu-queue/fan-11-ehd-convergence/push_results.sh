#!/bin/bash
# Return path for HF-hosted runs: push a results directory to a NEW git branch.
# Token comes ONLY from the HF Jobs secret env var GH_TOKEN (never in files, URLs, or logs).
# Usage: push_results.sh <repo "owner/name"> <branch> <src_dir> <dest_subdir> "<commit msg>"
set -euo pipefail
REPO="$1"; BRANCH="$2"; SRC="$3"; DEST="$4"; MSG="$5"
export GH_TOKEN; : "${GH_TOKEN:?GH_TOKEN secret not set - pass it with: hf jobs run --secrets GH_TOKEN ...}"
case "$BRANCH" in main|master|simulation-results|wme1-cfd) echo "refusing to push to protected/shared branch $BRANCH" >&2; exit 2;; esac
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
# GIT_ASKPASS helper prints the token from the environment; works on old git (Ubuntu 16.04 git 2.7)
cat > "$W/askpass" <<'EOA'
#!/bin/sh
case "$1" in Username*) echo x-access-token;; *) echo "$GH_TOKEN";; esac
EOA
chmod 700 "$W/askpass"; export GIT_ASKPASS="$W/askpass" GIT_TERMINAL_PROMPT=0
G() { git -c credential.helper= "$@"; }
G clone --quiet --depth 1 "https://github.com/$REPO.git" "$W/r"
cd "$W/r"
if G ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  G fetch --quiet --depth 1 origin "$BRANCH" && git checkout --quiet -B "$BRANCH" FETCH_HEAD
else
  git checkout --quiet -b "$BRANCH"
fi
mkdir -p "$DEST"; cp -a "$SRC"/. "$DEST"/
# refuse to push anything that looks like a credential
if grep -rIlE '(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16})' "$DEST"; then
  echo "credential-like string found in results; NOT pushing" >&2; exit 3
fi
git -c user.name="hf-job-bot" -c user.email="hf-job-bot@users.noreply.github.com" add "$DEST"
git -c user.name="hf-job-bot" -c user.email="hf-job-bot@users.noreply.github.com" commit --quiet -m "$MSG"
G push --quiet origin "HEAD:refs/heads/$BRANCH"   # plain push to a new results branch; never --force
echo "pushed $(git rev-parse --short HEAD) to $REPO:$BRANCH/$DEST"
