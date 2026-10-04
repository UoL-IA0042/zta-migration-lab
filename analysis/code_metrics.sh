#!/usr/bin/env bash
# Code-volume metrics per phase tag (implementation-complexity proxy, RQ4/RQ5).
# Requires: git repo with phase tags; cloc (apt install cloc).
#
# Usage: ./code_metrics.sh [output.csv]   # run from repo root
set -euo pipefail

OUT="${1:-analysis/code_metrics.csv}"
echo "tag,component,language,files,blank,comment,code" > "$OUT"

for TAG in $(git tag --list 'phase-*' | sort); do
  git -c advice.detachedHead=false checkout -q "$TAG"
  for DIR in ansible-* terraform-* test-matrix calico-policies perf-battery analysis; do
    [ -d "$DIR" ] || continue
    cloc --quiet --csv "$DIR" 2>/dev/null | tail -n +3 | \
      awk -F, -v tag="$TAG" -v dir="$DIR" \
        'NF>=5 && $2!="SUM" {print tag","dir","$2","$1","$3","$4","$5}' >> "$OUT"
  done
done
git checkout -q -   # return to previous ref

echo "wrote $OUT"
echo "Per-tag totals (code lines):"
awk -F, 'NR>1 {sum[$1]+=$7} END {for (t in sum) print "  "t": "sum[t]}' "$OUT" | sort
