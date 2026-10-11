#!/usr/bin/env python3
"""Access-control test matrix harness.

Executes positive and negative access probes for ONE role against the
resources defined in a matrix file, and records results as CSV. Run it
from a machine holding that role's session (VPN profile or ZTNA
enrollment), once per role, per phase, after every policy change.

Usage:
    ./run_matrix.py --matrix matrix.yaml --role remote-developer
    ./run_matrix.py --matrix matrix.yaml --role remote-admin --dry-run

Dependencies: Python 3.10+, PyYAML (apt install python3-yaml).

Probe types:
    tcp   - TCP connect to host:port. Connect = allow; timeout/refusal/
            unreachable = deny (network-level denial is how both firewalls
            and ZTNA overlays express "no").
    http  - HTTP request. 2xx/3xx = allow; 401/403 = deny; anything else
            (including connection failure, which is deny at network level)
            recorded with detail.
    exec  - Arbitrary command (psql, aws s3api, ssh, ...). Exit 0 = allow.
            A nonzero exit is a deny only if its output matches the
            probe's `deny_pattern` (regex); otherwise it is an ERROR, so a
            missing client, profile or password can never pass as a deny.
            A timeout is a deny only if `deny_on_timeout` is true (a
            network-level drop is a legitimate deny for some resources,
            not for others). Without `deny_pattern`, any nonzero exit is a
            deny (legacy behaviour; set it for every exec probe). `{role}`
            in the command is substituted, and `$VAR` / `${VAR}` are
            expanded from the environment (an unset variable is an ERROR,
            never a silent deny).

Per-probe settings (on the resource, overridable per operation):
    timeout          seconds for this probe (default: defaults.timeout)
    deny_pattern     exec only: regex a genuine deny's output must match
    deny_on_timeout  exec only: whether a timeout counts as deny (default true)

Result semantics:
    PASS  - observed == expected
    FAIL  - observed != expected (policy defect: log an issue)
    ERROR - probe could not produce a determination (fix the probe)
"""

from __future__ import annotations

import argparse
import csv
import datetime
import os
import re
import shlex
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: apt install python3-yaml (or pip install pyyaml)")

ALLOW, DENY, ERROR = "allow", "deny", "error"

CSV_FIELDS = [
    "run_id", "timestamp_utc", "phase", "role", "resource", "operation",
    "probe_type", "expected", "observed", "result", "latency_ms", "detail",
]


def _ms(t0: float) -> int:
    return round((time.monotonic() - t0) * 1000)


def probe_tcp(resource: dict, op_def: dict, timeout: float) -> tuple[str, str, int]:
    host, port = resource["host"], int(resource["port"])
    t0 = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return ALLOW, "connected", _ms(t0)
    except (socket.timeout, TimeoutError):
        return DENY, "timeout", _ms(t0)
    except ConnectionRefusedError:
        return DENY, "connection refused", _ms(t0)
    except OSError as exc:
        return DENY, f"unreachable: {exc}", _ms(t0)


def probe_http(resource: dict, op_def: dict, timeout: float, role: str) -> tuple[str, str, int]:
    url = resource["url"].rstrip("/") + op_def.get("path", "/")
    method = op_def.get("method", "GET").upper()
    body = op_def.get("body")
    req = urllib.request.Request(
        url, method=method,
        data=body.encode() if body else None,
    )
    token_env = resource.get("auth_token_env")
    if token_env:
        token = os.environ.get(token_env, "")
        if not token:
            return ERROR, f"env {token_env} unset", 0
        req.add_header("Authorization", f"Bearer {token}")
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return ALLOW, f"HTTP {resp.status}", _ms(t0)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return DENY, f"HTTP {exc.code}", _ms(t0)
        return ERROR, f"HTTP {exc.code}", _ms(t0)
    except urllib.error.URLError as exc:
        return DENY, f"connection failed: {exc.reason}", _ms(t0)
    except (socket.timeout, TimeoutError):
        return DENY, "timeout", _ms(t0)


# $VAR or ${VAR} references in exec commands (expanded from the environment)
ENV_REF = re.compile(r"\$(?:\{(\w+)\}|(\w+))")


def setting(resource: dict, op_def: dict, key: str, default):
    """Per-operation value, else per-resource value, else default."""
    return op_def.get(key, resource.get(key, default))


def probe_exec(resource: dict, op_def: dict, timeout: float, role: str) -> tuple[str, str, int]:
    deny_pattern = setting(resource, op_def, "deny_pattern", None)
    deny_on_timeout = bool(setting(resource, op_def, "deny_on_timeout", True))
    # Expand environment references before str.format, which would
    # otherwise read the braces in ${VAR} as a format field.
    command = op_def["command"]
    missing = sorted({a or b for a, b in ENV_REF.findall(command)} - set(os.environ))
    if missing:
        return ERROR, f"environment variable not set: {', '.join(missing)}", 0
    command = os.path.expandvars(command).format(role=role)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            shlex.split(command), capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        if deny_on_timeout:
            return DENY, "timeout", _ms(t0)
        return ERROR, "timeout (not a deny for this probe)", _ms(t0)
    except FileNotFoundError as exc:
        return ERROR, f"command not found: {exc.filename}", _ms(t0)
    if proc.returncode == 0:
        return ALLOW, "exit 0", _ms(t0)
    output = f"{proc.stderr or ''}\n{proc.stdout or ''}"
    detail = (proc.stderr or proc.stdout or "").strip().replace("\n", " ")[:200]
    if deny_pattern is None or re.search(deny_pattern, output):
        return DENY, f"exit {proc.returncode}: {detail}", _ms(t0)
    return ERROR, f"exit {proc.returncode}, no deny signature: {detail}", _ms(t0)


def run(matrix: dict, role: str, out_dir: str, dry_run: bool) -> int:
    phase = matrix.get("phase", "unspecified")
    timeout = float(matrix.get("defaults", {}).get("timeout", 10))
    resources = matrix["resources"]
    expectations = matrix["expectations"].get(role)
    if expectations is None:
        sys.exit(f"role '{role}' not present in matrix expectations")

    run_id = uuid.uuid4().hex[:12]
    rows, failures, errors = [], 0, 0

    for res_name, ops in expectations.items():
        resource = resources.get(res_name)
        if resource is None:
            sys.exit(f"resource '{res_name}' referenced but not defined")
        for op_name, expected in ops.items():
            if expected not in (ALLOW, DENY):
                sys.exit(f"{role}/{res_name}/{op_name}: expected must be allow|deny")
            op_def = resource.get("operations", {}).get(op_name, {})
            ptype = resource["type"]
            probe_timeout = float(setting(resource, op_def, "timeout", timeout))
            pattern = setting(resource, op_def, "deny_pattern", None)
            if pattern is not None:
                try:
                    re.compile(pattern)
                except re.error as exc:
                    sys.exit(f"{res_name}/{op_name}: invalid deny_pattern: {exc}")
            if dry_run:
                deny_rule = f" deny=/{pattern}/" if pattern else ""
                print(f"DRY  {role:20s} {res_name:20s} {op_name:10s} "
                      f"[{ptype}{deny_rule}] expect {expected}")
                continue
            if ptype == "tcp":
                observed, detail, latency = probe_tcp(resource, op_def, probe_timeout)
            elif ptype == "http":
                observed, detail, latency = probe_http(resource, op_def, probe_timeout, role)
            elif ptype == "exec":
                observed, detail, latency = probe_exec(resource, op_def, probe_timeout, role)
            else:
                sys.exit(f"unknown probe type '{ptype}' for resource '{res_name}'")

            if observed == ERROR:
                result = "ERROR"
                errors += 1
            elif observed == expected:
                result = "PASS"
            else:
                result = "FAIL"
                failures += 1

            rows.append({
                "run_id": run_id,
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc)
                                 .isoformat(timespec="seconds"),
                "phase": phase, "role": role, "resource": res_name,
                "operation": op_name, "probe_type": ptype,
                "expected": expected, "observed": observed, "result": result,
                "latency_ms": latency, "detail": detail,
            })
            print(f"{result:5s} {role:20s} {res_name:20s} {op_name:10s} "
                  f"expect={expected} observed={observed} ({detail})")

    if dry_run:
        return 0

    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join(out_dir, f"{phase}_{role}_{stamp}_{run_id}.csv")
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    print(f"\n{total} probes: {total - failures - errors} pass, "
          f"{failures} fail, {errors} error -> {out_path}")
    return 1 if (failures or errors) else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matrix", required=True, help="matrix YAML file")
    ap.add_argument("--role", required=True, help="role to probe as")
    ap.add_argument("--out-dir", default="results", help="CSV output directory")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate matrix and list planned probes without executing")
    args = ap.parse_args()

    with open(args.matrix) as fh:
        matrix = yaml.safe_load(fh)

    sys.exit(run(matrix, args.role, args.out_dir, args.dry_run))


if __name__ == "__main__":
    main()
