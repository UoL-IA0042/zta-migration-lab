#!/usr/bin/env python3
"""Parse work-journal Markdown into CSV for the time-allocation analysis.

Entry header format (journal/README.md):
    ## 2026-09-12 09:40-11:05 | phase-2 | openziti | debugging
(en-dash or hyphen accepted between times; entries may cross midnight,
in which case duration wraps forward.)

Defects are lines in an entry's body that start with "Defect:" (optionally
as a list item), outside fenced code blocks (journal/README.md).

Usage:
    ./parse_journal.py ../journal/ -o journal.csv
    ./parse_journal.py ../journal/ -o journal.csv --defects defects.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime
import glob
import os
import re
import sys

CATEGORIES = {"planning", "coding", "deployment", "debugging",
              "testing", "documentation"}

HEADER_RE = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})[–-](\d{2}:\d{2})"
    r"\s*\|\s*([\w.-]+)\s*\|\s*([\w.-]+)\s*\|\s*([\w-]+)\s*$")

DEFECT_RE = re.compile(r"^\s*(?:[-*]\s+)?Defect:\s*(.+?)\s*$")


def parse_file(path: str) -> tuple[list[dict], list[str]]:
    entries, problems = [], []
    current = None
    in_code = False
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                if current is not None:
                    current["words"] += len(line.split())
                continue
            m = None if in_code else HEADER_RE.match(line)
            if m:
                if current:
                    entries.append(current)
                date, start, end, phase, component, category = m.groups()
                t0 = datetime.datetime.fromisoformat(f"{date}T{start}")
                t1 = datetime.datetime.fromisoformat(f"{date}T{end}")
                if t1 <= t0:
                    t1 += datetime.timedelta(days=1)  # crossed midnight
                if category not in CATEGORIES:
                    problems.append(
                        f"{path}:{lineno}: unknown category '{category}'")
                current = {
                    "file": os.path.basename(path), "date": date,
                    "start": start, "end": end,
                    "minutes": int((t1 - t0).total_seconds() // 60),
                    "phase": phase, "component": component,
                    "category": category, "defects": [], "words": 0,
                }
            elif line.startswith("## ") and not in_code:
                problems.append(f"{path}:{lineno}: malformed header: "
                                f"{line.strip()[:80]}")
            elif current is not None:
                d = None if in_code else DEFECT_RE.match(line)
                if d:
                    current["defects"].append(d.group(1))
                current["words"] += len(line.split())
    if current:
        entries.append(current)
    return entries, problems


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("journal_dir")
    ap.add_argument("-o", "--output", default="journal.csv")
    ap.add_argument("--defects", help="also write one row per Defect: line to this CSV")
    args = ap.parse_args()

    paths = sorted(p for p in glob.glob(os.path.join(args.journal_dir, "*.md"))
                   if os.path.basename(p) != "README.md")
    if not paths:
        sys.exit(f"no journal files in {args.journal_dir}")

    all_entries, all_problems = [], []
    for p in paths:
        entries, problems = parse_file(p)
        all_entries.extend(entries)
        all_problems.extend(problems)

    with open(args.output, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "date", "start", "end", "minutes", "phase",
                    "component", "category", "defects", "note_words"])
        for e in all_entries:
            w.writerow([e["file"], e["date"], e["start"], e["end"],
                        e["minutes"], e["phase"], e["component"],
                        e["category"], len(e["defects"]), e["words"]])

    n_defects = sum(len(e["defects"]) for e in all_entries)
    if args.defects:
        with open(args.defects, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["file", "date", "start", "phase", "component",
                        "category", "defect"])
            for e in all_entries:
                for text in e["defects"]:
                    w.writerow([e["file"], e["date"], e["start"], e["phase"],
                                e["component"], e["category"], text])

    total_min = sum(e["minutes"] for e in all_entries)
    print(f"{len(all_entries)} entries, {total_min/60:.1f} hours, "
          f"{n_defects} defects -> {args.output}"
          + (f", {args.defects}" if args.defects else ""))

    by_cat: dict[str, int] = {}
    for e in all_entries:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["minutes"]
    for cat, minutes in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:14s} {minutes/60:6.1f} h "
              f"({minutes/total_min*100:4.1f}%)")

    if all_problems:
        print("\nproblems:", file=sys.stderr)
        for p in all_problems:
            print(f"  {p}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
