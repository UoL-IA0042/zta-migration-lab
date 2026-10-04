#!/usr/bin/env bash
# Produce an anonymous review export of this repository.
# Excludes git history and CITATION.cff, then refuses to export if any
# blocklisted identifier appears in the tree.
#
# Usage:  ./scripts/anonymize_export.sh [output.tar.gz]
# Extend the blocklist with any identifier tied to you.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-/tmp/zta-migration-lab-anonymous.tar.gz}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# --- Blocklist: personal identifiers that must not appear ------------
# Kept in a separate file (excluded from the export) so the scanner
# doesn't flag itself.
mapfile -t BLOCKLIST < <(grep -v '^\s*#' "$REPO_ROOT/scripts/anonymize_blocklist.txt" | sed '/^\s*$/d')
[ "${#BLOCKLIST[@]}" -gt 0 ] || { echo "empty blocklist" >&2; exit 1; }

# --- Stage the tree without .git, identity files, and this tooling ---
rsync -a "$REPO_ROOT/" "$STAGE/repo/" \
  --exclude ".git" \
  --exclude "CITATION.cff" \
  --exclude "scripts/anonymize_export.sh" \
  --exclude "scripts/anonymize_blocklist.txt" \
  --exclude "*.retry" --exclude "__pycache__"

# --- Scan for identifiers -------------------------------------------
FAIL=0
for TERM in "${BLOCKLIST[@]}"; do
  if MATCHES=$(grep -rniI --exclude-dir=.git -- "$TERM" "$STAGE/repo" 2>/dev/null); then
    echo "BLOCKED identifier '$TERM' found:" >&2
    echo "$MATCHES" | head -10 >&2
    FAIL=1
  fi
done
# git author info can also hide in generated files
if MATCHES=$(grep -rlI "Signed-off-by\|Co-authored-by" "$STAGE/repo" 2>/dev/null); then
  [ -n "$MATCHES" ] && { echo "BLOCKED commit trailers found in: $MATCHES" >&2; FAIL=1; }
fi
[ "$FAIL" -eq 1 ] && { echo "Export refused. Scrub the matches and re-run." >&2; exit 1; }

# --- Package ---------------------------------------------------------
tar -czf "$OUT" -C "$STAGE" repo
echo "Anonymous export: $OUT"
echo "Verify by extracting and re-grepping before upload."
