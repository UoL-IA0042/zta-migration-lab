#!/usr/bin/env python3
"""Performance battery: throughput (iperf3) and HTTP latency (curl).

Run from an emulated remote-worker machine through the access path under
test (VPN tunnel or ZTNA overlay). Emits one CSV row per repetition so
dispersion is computable downstream.

Usage:
    ./run_perf.py --phase phase-1 --path vpn \
        --iperf-server 10.0.0.73 \
        --http-url http://10.0.0.73:8080/ \
        --reps 5

Dependencies: iperf3 and curl on the probing machine (apt install iperf3 curl).
The matching iperf3 server runs on the target: `iperf3 -s`.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import statistics
import subprocess
import sys
import uuid

CSV_FIELDS = ["run_id", "timestamp_utc", "phase", "path", "test", "rep",
              "value", "unit", "detail"]


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def iperf_run(server: str, reverse: bool, duration: int) -> tuple[float, str]:
    cmd = ["iperf3", "-c", server, "-t", str(duration), "-J"]
    if reverse:
        cmd.append("-R")
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip())
    data = json.loads(out.stdout)
    bps = data["end"]["sum_received"]["bits_per_second"]
    return bps / 1e6, "Mbps"


def http_latency(url: str) -> tuple[float, str]:
    out = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{time_total}", url],
        capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError(f"curl exit {out.returncode}")
    return float(out.stdout) * 1000, "ms"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", required=True)
    ap.add_argument("--path", required=True,
                    help="access path label: baseline|vpn|openziti|netbird")
    ap.add_argument("--iperf-server", help="iperf3 server address")
    ap.add_argument("--http-url", help="HTTP endpoint for latency samples")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--iperf-duration", type=int, default=10)
    ap.add_argument("--http-samples", type=int, default=50,
                    help="latency samples per repetition")
    ap.add_argument("--out-dir", default="results")
    args = ap.parse_args()

    if not (args.iperf_server or args.http_url):
        sys.exit("nothing to do: provide --iperf-server and/or --http-url")

    run_id = uuid.uuid4().hex[:12]
    rows = []

    for rep in range(1, args.reps + 1):
        if args.iperf_server:
            for test, reverse in (("throughput_up", False), ("throughput_down", True)):
                try:
                    value, unit = iperf_run(args.iperf_server, reverse,
                                            args.iperf_duration)
                    detail = ""
                except Exception as exc:  # noqa: BLE001 - recorded, not hidden
                    value, unit, detail = float("nan"), "Mbps", str(exc)[:200]
                rows.append(dict(run_id=run_id, timestamp_utc=now(),
                                 phase=args.phase, path=args.path, test=test,
                                 rep=rep, value=f"{value:.2f}", unit=unit,
                                 detail=detail))
                print(f"rep {rep} {test}: {value:.2f} {unit} {detail}")

        if args.http_url:
            samples = []
            for _ in range(args.http_samples):
                try:
                    ms, _ = http_latency(args.http_url)
                    samples.append(ms)
                except Exception as exc:  # noqa: BLE001
                    print(f"  sample error: {exc}", file=sys.stderr)
            if samples:
                for stat, val in (("http_latency_p50", statistics.median(samples)),
                                  ("http_latency_mean", statistics.fmean(samples)),
                                  ("http_latency_max", max(samples))):
                    rows.append(dict(run_id=run_id, timestamp_utc=now(),
                                     phase=args.phase, path=args.path,
                                     test=stat, rep=rep,
                                     value=f"{val:.2f}", unit="ms",
                                     detail=f"n={len(samples)}"))
                print(f"rep {rep} http latency p50="
                      f"{statistics.median(samples):.1f}ms n={len(samples)}")

    os.makedirs(args.out_dir, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(args.out_dir,
                        f"{args.phase}_{args.path}_{stamp}_{run_id}.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} rows -> {path}")


if __name__ == "__main__":
    main()
