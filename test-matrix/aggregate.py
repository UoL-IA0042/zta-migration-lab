#!/usr/bin/env python3
"""Aggregate access-matrix CSV results into a per-phase/role summary.

Usage:
    ./aggregate.py results/           # summary table to stdout
    ./aggregate.py results/ --fails   # also list every FAIL/ERROR row

Exit status is nonzero if any FAIL or ERROR rows exist, so this can gate
a migration wave in CI or a runbook.
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import sys
from collections import defaultdict


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results_dir", help="directory of run_matrix.py CSV output")
    ap.add_argument("--fails", action="store_true", help="list failing rows")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.results_dir, "*.csv")))
    if not paths:
        sys.exit(f"no CSV files in {args.results_dir}")

    counts: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"PASS": 0, "FAIL": 0, "ERROR": 0})
    bad_rows = []

    for path in paths:
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                key = (row["phase"], row["role"])
                counts[key][row["result"]] += 1
                if row["result"] != "PASS":
                    bad_rows.append(row)

    print(f"{'phase':12s} {'role':22s} {'pass':>6s} {'fail':>6s} "
          f"{'error':>6s} {'rate':>7s}")
    for (phase, role), c in sorted(counts.items()):
        total = sum(c.values())
        rate = c["PASS"] / total * 100 if total else 0.0
        print(f"{phase:12s} {role:22s} {c['PASS']:6d} {c['FAIL']:6d} "
              f"{c['ERROR']:6d} {rate:6.1f}%")

    if args.fails and bad_rows:
        print("\nfailing rows:")
        for r in bad_rows:
            print(f"  [{r['result']}] {r['phase']} {r['role']} "
                  f"{r['resource']}/{r['operation']} expected={r['expected']} "
                  f"observed={r['observed']} ({r['detail']}) run={r['run_id']}")

    sys.exit(1 if bad_rows else 0)


if __name__ == "__main__":
    main()
