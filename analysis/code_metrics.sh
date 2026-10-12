#!/usr/bin/env bash
# Code-volume metrics per phase tag (implementation-complexity proxy, RQ4/RQ5).
# Requires: git repo with phase tags; cloc (brew install cloc / apt install cloc).
#
# Each tag is unpacked into a temporary directory with `git archive`, so
# the working tree, the current branch and any uncommitted changes are
# never touched (an earlier version checked tags out and returned with
# `git checkout -`, which left the repo detached at the second-to-last tag).
#
# Usage: ./analysis/code_metrics.sh [output.csv]   # run from repo root
set -euo pipefail

OUT="${1:-analysis/code_metrics.csv}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
TMP_OUT="$WORK/code_metrics.csv"
echo "tag,component,language,files,blank,comment,code" > "$TMP_OUT"

for TAG in $(git tag --list 'phase-*' | sort); do
  SRC="$WORK/$TAG"
  mkdir -p "$SRC"
  git archive --format=tar "$TAG" | tar -x -C "$SRC"
  for DIR in "$SRC"/ansible-* "$SRC"/terraform-* "$SRC"/test-matrix \
             "$SRC"/calico-policies "$SRC"/perf-battery "$SRC"/analysis; do
    [ -d "$DIR" ] || continue
    NAME="$(basename "$DIR")"
    # Keep only data rows (first field numeric): cloc's header and any
    # leading blank line vary by version, so no fixed line offset.
    cloc --quiet --csv "$DIR" 2>/dev/null | \
      awk -F, -v tag="$TAG" -v dir="$NAME" \
        '$1 ~ /^[0-9]+$/ && NF>=5 && $2!="SUM" {print tag","dir","$2","$1","$3","$4","$5}' >> "$TMP_OUT"
  done
done

mv "$TMP_OUT" "$OUT"
echo "wrote $OUT"
echo "Per-tag totals (code lines):"
awk -F, 'NR>1 {sum[$1]+=$7} END {for (t in sum) print "  "t": "sum[t]}' "$OUT" | sort
