#!/usr/bin/env python3
"""Every table for the Results chapter, from committed data, in one run.

Writes results/results-tables.md (Markdown tables to paste or adapt) from:
  test-matrix/results/*.csv          verification: access test matrix
  perf-battery/results/*.csv         verification: performance per path
  journal/*.md (parse_journal.py)    effort: hours by phase and category; defects
  analysis/code_metrics.csv          size: code lines per component and tag
  git diff --numstat between tags    churn per top-level directory
  results/translation-summary.md     rule-to-policy translation (translation.py)

Runs that were excluded (results/excluded/, test-matrix/results/phase-1-rebuild/)
are counted, not used. Re-run after any change to the data; the output
must then be committed with it.

Usage (from analysis/):  ./results_tables.py [--repo ..] [--out results/results-tables.md]
Standard library only (plus the sibling parse_journal.py).
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse_journal  # noqa: E402

PHASE_ORDER = ["phase-0", "phase-1", "phase-2", "phase-3"]
CATEGORIES = ["planning", "coding", "deployment", "debugging", "testing", "documentation"]
TAGS = ["phase-0-infrastructure", "phase-1-baseline", "phase-2-openziti",
        "phase-2-netbird", "phase-3-translation"]
PRODUCT_DIRS = {"phase-1-baseline": "ansible-openvpn", "phase-2-openziti": "ansible-openziti",
                "phase-2-netbird": "ansible-netbird"}
PERF_TESTS = [("throughput_up", "Mbps"), ("throughput_down", "Mbps"),
              ("http_latency_p50", "ms"), ("http_latency_mean", "ms"), ("http_latency_max", "ms")]
PATH_ORDER = ["baseline", "vpn", "openziti", "netbird", "vpn-aws", "openziti-aws", "netbird-aws"]


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def h(x):
    return f"{x:.1f}"


def read_csvs(pattern):
    rows = []
    for path in sorted(glob.glob(pattern)):
        with open(path, newline="") as fh:
            for r in csv.DictReader(fh):
                r["_file"] = os.path.basename(path)
                rows.append(r)
    return rows


# --- verification ---------------------------------------------------------------

def matrix_section(repo):
    rows = read_csvs(os.path.join(repo, "test-matrix/results/*.csv"))
    runs = collections.defaultdict(set)
    counts = collections.defaultdict(collections.Counter)
    for r in rows:
        key = (r["phase"], r["role"])
        counts[key][r["result"]] += 1
        runs[key].add(r["run_id"])
    body = []
    for (phase, role) in sorted(counts):
        c = counts[(phase, role)]
        total = sum(c.values())
        body.append([phase, role, len(runs[(phase, role)]), c["PASS"], c["FAIL"], c["ERROR"],
                     f"{100 * c['PASS'] / total:.1f}%"])
    fails = [[r["phase"], r["role"], f"{r['resource']}/{r['operation']}", r["expected"],
              r["observed"], r["detail"][:60]] for r in rows if r["result"] != "PASS"]
    excluded = collections.Counter(
        os.path.basename(p).split("_")[0]
        for p in glob.glob(os.path.join(repo, "test-matrix/results/excluded/*.csv")))
    rebuild = len(glob.glob(os.path.join(repo, "test-matrix/results/phase-1-rebuild/*.csv")))
    out = ["## Verification: access test matrix", "",
           "Runs in `test-matrix/results/` (excluded and Phase 1 rebuild runs not counted).", "",
           table(["phase", "role", "runs", "pass", "fail", "error", "pass rate"], body), ""]
    if fails:
        out += ["Failing probes:", "",
                table(["phase", "role", "probe", "expected", "observed", "detail"], fails), ""]
    out += ["Runs not used: " + ", ".join(f"{n} excluded ({p})" for p, n in sorted(excluded.items()))
            + f"; {rebuild} Phase 1 rebuild runs (baseline re-check before NetBird, all roles).", ""]
    return out


def perf_section(repo):
    rows = read_csvs(os.path.join(repo, "perf-battery/results/*.csv"))
    vals = collections.defaultdict(list)
    files = collections.defaultdict(set)
    nan = collections.Counter()
    for r in rows:
        try:
            v = float(r["value"])
        except ValueError:
            v = float("nan")
        if v != v:
            nan[(r["phase"], r["path"], r["test"])] += 1
            continue
        vals[(r["phase"], r["path"], r["test"])].append(v)
        files[(r["phase"], r["path"])].add(r["_file"])
    paths = sorted({(k[0], k[1]) for k in vals}, key=lambda pp: PATH_ORDER.index(pp[1]) if pp[1] in PATH_ORDER else 99)
    body = []
    for phase, path in paths:
        row = [path, phase]
        for test, _unit in PERF_TESTS:
            v = vals.get((phase, path, test))
            if not v:
                row.append("-")
                continue
            sd = statistics.stdev(v) if len(v) > 1 else 0.0
            row.append(f"{statistics.mean(v):.1f} ({sd:.1f})")
        body.append(row)
    rng = []
    for phase, path in paths:
        v = vals.get((phase, path, "http_latency_p50"))
        if v:
            rng.append([path, f"{min(v):.1f}-{max(v):.1f}", len(v)])
    excluded = sorted(os.path.basename(p) for p in glob.glob(os.path.join(repo, "perf-battery/results/excluded/*.csv")))
    out = ["## Verification: performance per access path", "",
           "Mean (standard deviation) over repetitions; throughput in Mbps, latency in ms. "
           "The `-aws` paths are HTTP latency only (perf-battery README: no iperf3 test on the AWS path).", "",
           table(["path", "phase"] + [f"{t} ({u})" for t, u in PERF_TESTS], body), "",
           "Range of the per-repetition median latency (p50):", "",
           table(["path", "p50 min-max (ms)", "reps"], rng), ""]
    if nan:
        out += ["Failed repetitions (NaN): " + ", ".join(f"{k[1]}/{k[2]} x{n}" for k, n in sorted(nan.items())), ""]
    if excluded:
        out += ["Excluded runs: " + ", ".join(f"`{e}`" for e in excluded), ""]
    return out


# --- effort ---------------------------------------------------------------------

def journal_entries(repo):
    entries, problems = [], []
    for p in sorted(glob.glob(os.path.join(repo, "journal/*.md"))):
        if os.path.basename(p) == "README.md":
            continue
        e, pr = parse_journal.parse_file(p)
        entries += e
        problems += pr
    return entries, problems


def effort_section(entries, problems, repo):
    mins = collections.defaultdict(int)
    comp = collections.defaultdict(int)
    for e in entries:
        mins[(e["phase"], e["category"])] += e["minutes"]
        comp[(e["phase"], e["component"])] += e["minutes"]
    phases = [p for p in PHASE_ORDER if any(k[0] == p for k in mins)]
    body = []
    for p in phases:
        tot = sum(mins[(p, c)] for c in CATEGORIES)
        body.append([p] + [h(mins[(p, c)] / 60) for c in CATEGORIES] + [h(tot / 60)])
    grand = sum(mins.values())
    body.append(["total"] + [h(sum(mins[(p, c)] for p in phases) / 60) for c in CATEGORIES] + [h(grand / 60)])
    share = [[c, h(sum(mins[(p, c)] for p in phases) / 60),
              f"{100 * sum(mins[(p, c)] for p in phases) / grand:.1f}%"] for c in CATEGORIES]
    comp_rows = [[p, c, h(m / 60)] for (p, c), m in sorted(comp.items())]
    out = ["## Effort: journal hours", "",
           f"{len(entries)} journal entries, {h(grand / 60)} hours. Deployment order: Phase 0, Phase 1, "
           "OpenZiti, Phase 1 rebuild, NetBird, Phase 3 (single operator; later work benefits from earlier).", "",
           "Hours by phase and category:", "",
           table(["phase"] + CATEGORIES + ["total"], body), "",
           "Share of all hours by category:", "",
           table(["category", "hours", "share"], share), "",
           "Hours by phase and component (journal header field):", "",
           table(["phase", "component", "hours"], comp_rows), ""]
    if problems:
        out += ["Journal entries the parser could not read (not counted):", ""]
        out += [f"- `{os.path.relpath(p.split(':')[0], repo)}:{p.split(':', 1)[1]}`" for p in problems] + [""]
    return out


def defects_section(entries):
    by = collections.Counter()
    rows = []
    for e in entries:
        for d in e["defects"]:
            by[(e["phase"], e["component"])] += 1
            rows.append([e["phase"], e["component"], e["category"], e["date"] + " " + e["start"],
                         d.split(". Cause:")[0][:110]])
    out = ["## Defects and unplanned work (journal `Defect:` lines)", "",
           f"{len(rows)} defects.", "",
           table(["phase", "component", "defects"], [[p, c, n] for (p, c), n in sorted(by.items())]), "",
           table(["phase", "component", "entry category", "entry", "what failed"], rows), ""]
    phases_without = [p for p in PHASE_ORDER if p not in {r[0] for r in rows}
                      and any(e["phase"] == p for e in entries)]
    if phases_without:
        out += ["Phases with journal entries but no `Defect:` lines: " + ", ".join(phases_without) + ".", ""]
    return out


# --- size -------------------------------------------------------------------------

def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def size_section(repo):
    path = os.path.join(repo, "analysis/code_metrics.csv")
    code = collections.defaultdict(int)
    langs = collections.defaultdict(collections.Counter)
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            code[(r["tag"], r["component"])] += int(r["code"])
            langs[(r["tag"], r["component"])][r["language"]] += int(r["code"])
    tags = [t for t in TAGS if any(k[0] == t for k in code)]
    comps = sorted({k[1] for k in code})
    body = [[c] + [code.get((t, c), "-") for t in tags] for c in comps]
    prod = []
    for tag, d in PRODUCT_DIRS.items():
        if (tag, d) in code:
            mix = ", ".join(f"{l} {n}" for l, n in langs[(tag, d)].most_common())
            prod.append([tag, d, code[(tag, d)], mix])
    out = ["## Size: code lines per component and tag (`code_metrics.sh`, cloc)", "",
           "Code lines (excluding blanks and comments), all languages. A component appears at a tag "
           "if its directory exists there; `ansible-k3s` and `calico-policies` were never deployed.", "",
           table(["component"] + tags, body), "",
           "Each access product's own directory at its own tag:", "",
           table(["tag", "directory", "code lines", "by language"], prod), ""]
    have = set(git(repo, "tag", "--list", "phase-*").split())
    pairs = [(a, b) for a, b in zip(tags, tags[1:]) if a in have and b in have]
    churn_rows = []
    for a, b in pairs:
        agg = collections.defaultdict(lambda: [0, 0])
        for line in git(repo, "diff", "--numstat", f"{a}..{b}").splitlines():
            add, dele, name = line.split("\t", 2)
            if add == "-":
                continue                                # binary
            top = name.split("/")[0]
            agg[top][0] += int(add)
            agg[top][1] += int(dele)
        for top, (ad, de) in sorted(agg.items()):
            churn_rows.append([f"{a} -> {b}", top, ad, de])
    out += ["Churn between successive tags (lines added / deleted per top-level path, `git diff --numstat`). "
            "NetBird's experiment started from the Phase 1 baseline in the lab, but in the repository it "
            "follows the OpenZiti tag, so its row shows only what the NetBird experiment changed:", "",
            table(["tags", "path", "added", "deleted"], churn_rows), ""]
    return out


# --- translation ------------------------------------------------------------------

def translation_section(repo):
    path = os.path.join(repo, "analysis/results/translation-summary.md")
    with open(path) as fh:
        text = fh.read().split("\n## ")
    keep = ("Consistency checks", "Changes from Phase 1", "Breadth at the network layer",
            "Size of the access-control artifacts", "Expected denies by enforcement layer")
    out = ["## Rule-to-policy translation (from `translation-summary.md`)", ""]
    for sec in text[1:]:
        title, _, body = sec.partition("\n")
        if title.startswith(keep):
            if title.startswith("Changes from Phase 1"):
                body = body.split("\n\n| product | role")[0]          # counts only, not the long list
            out += [f"### {title}", "", body.strip(), ""]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.path.join(HERE, ".."))
    ap.add_argument("--out", default=os.path.join(HERE, "results", "results-tables.md"))
    args = ap.parse_args()
    entries, problems = journal_entries(args.repo)
    lines = ["# Results tables", "",
             "Generated by `analysis/results_tables.py` from committed data; do not edit by hand.", ""]
    lines += matrix_section(args.repo)
    lines += perf_section(args.repo)
    lines += effort_section(entries, problems, args.repo)
    lines += defects_section(entries)
    lines += size_section(args.repo)
    lines += translation_section(args.repo)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write("\n".join(lines))
    print(f"wrote {os.path.relpath(args.out)}")


if __name__ == "__main__":
    main()
