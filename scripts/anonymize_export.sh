#!/usr/bin/env bash
# Produce an anonymous review export of this repository.
# Exports the committed tree at HEAD only (git archive): untracked and
# ignored files such as .vault-pass, terraform.tfstate, .gitconfig and
# virtualenvs never reach the export. Excludes git history and
# CITATION.cff, redacts AWS account IDs in ARNs to <account-id> in the
# exported copy, then refuses to export if any blocklisted identifier
# or an unredacted account ID appears in the tree.
#
# Usage:  ./scripts/anonymize_export.sh [output.tar.gz]
# Commit first: uncommitted changes are not exported, and the script
# refuses to run with a dirty tree so the export matches a commit.
# Extend the blocklist with any identifier tied to you.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-/tmp/zta-migration-lab-anonymous.tar.gz}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# --- Blocklist: personal identifiers that must not appear ------------
# Kept in a separate file (excluded from the export) so the scanner
# doesn't flag itself.
# (while-read rather than mapfile: macOS ships bash 3.2)
BLOCKLIST=()
while IFS= read -r line; do
  BLOCKLIST+=("$line")
done < <(grep -v '^[[:space:]]*#' "$REPO_ROOT/scripts/anonymize_blocklist.txt" | sed '/^[[:space:]]*$/d')
[ "${#BLOCKLIST[@]}" -gt 0 ] || { echo "empty blocklist" >&2; exit 1; }

# --- Stage the committed tree without identity files and this tooling ---
if [ -n "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)" ]; then
  echo "Uncommitted changes to tracked files: commit or stash them first." >&2
  exit 1
fi
COMMIT="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
mkdir -p "$STAGE/repo"
git -C "$REPO_ROOT" archive --format=tar HEAD | tar -x -C "$STAGE/repo"
rm -rf "$STAGE/repo/CITATION.cff" \
       "$STAGE/repo/scripts/anonymize_export.sh" \
       "$STAGE/repo/scripts/anonymize_blocklist.txt"

# --- Redact AWS account IDs in ARNs (probe output in matrix CSVs) -----
# The committed data keeps them; only the review copy is redacted, with
# the journal's fixed label. perl -pi works on both macOS and Linux.
ARN_RE='(arn:aws[a-z-]*:[a-z0-9-]*:[a-z0-9-]*:)(?!123456789012:)[0-9]{12}:'
REDACTED=0
while IFS= read -r f; do
  perl -pi -e "s/$ARN_RE/\${1}<account-id>:/g" "$f"
  REDACTED=$((REDACTED + 1))
done < <(grep -rlIE "arn:aws[a-z-]*:[a-z0-9-]*:[a-z0-9-]*:[0-9]{12}:" "$STAGE/repo" 2>/dev/null || true)
echo "Redacted AWS account IDs in the review copy ($REDACTED file(s) contained ARNs)."

# --- Scan for identifiers -------------------------------------------
FAIL=0
for TERM in "${BLOCKLIST[@]}"; do
  if MATCHES=$(grep -rniI --exclude-dir=.git -- "$TERM" "$STAGE/repo" 2>/dev/null); then
    echo "BLOCKED identifier '$TERM' found:" >&2
    echo "$MATCHES" | head -10 >&2
    FAIL=1
  fi
done
# Any AWS account ID left in an ARN after redaction (safety net); AWS's
# documentation placeholder 123456789012 (test mocks) is allowed.
if MATCHES=$(grep -rnIE "arn:aws[a-z-]*:[a-z0-9-]*:[a-z0-9-]*:[0-9]{12}:" "$STAGE/repo" 2>/dev/null \
             | grep -vE ":(123456789012|000000000000):"); then
  echo "BLOCKED AWS account ID in an ARN:" >&2
  echo "$MATCHES" | cut -c1-200 | head -10 >&2
  FAIL=1
fi
# git author info can also hide in generated files
if MATCHES=$(grep -rlI "Signed-off-by\|Co-authored-by" "$STAGE/repo" 2>/dev/null); then
  [ -n "$MATCHES" ] && { echo "BLOCKED commit trailers found in: $MATCHES" >&2; FAIL=1; }
fi
[ "$FAIL" -eq 1 ] && { echo "Export refused. Scrub the matches and re-run." >&2; exit 1; }

# --- Package ---------------------------------------------------------
tar -czf "$OUT" -C "$STAGE" repo
echo "Anonymous export of commit $COMMIT: $OUT"
echo "Verify by extracting and re-grepping before upload."
