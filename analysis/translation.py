#!/usr/bin/env python3
"""Phase 3 rule-to-policy translation analysis (docs/phase-3-translation.md).

Normalises the three access-control artifacts into network-layer
entitlements per role and destination, classifies each change from the
Phase 1 perimeter ruleset to each ZTNA access model, and joins the access
test matrix for effective access and the enforcement layer of each deny.

Inputs are committed files only (paths relative to the repo root):
  ansible-openvpn/openvpn.yaml              declared perimeter ruleset
  journal/phase-1.md                        live ruleset (ufw status)
  ansible-openziti/group_vars/all/vars.yaml OpenZiti service/dial table
  journal/phase-2.md                        objects the bootstraps created
  ansible-netbird/group_vars/all/vars.yaml  NetBird service table, networks
  ansible-netbird/policies-export.json      deployed NetBird policies
  test-matrix/matrix*.yaml, results/*.csv   intended and observed access

Usage (from analysis/):
    ./translation.py                 # writes results/, prints the checks
    ./translation.py --repo .. --out results

Exit status is nonzero if a consistency check fails. Requires PyYAML.
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import ipaddress
import json
import os
import re
import sys

import yaml

PHASES = ("phase-1", "phase-2-openziti", "phase-2-netbird")
PRODUCTS = ("phase-2-openziti", "phase-2-netbird")
JINJA_VAR = re.compile(r"\{\{\s*(\w+)\s*\}\}")


# --- inputs --------------------------------------------------------------------

def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def resolve(value, env):
    """Substitute simple {{ var }} references from the play's vars."""
    if isinstance(value, str):
        return JINJA_VAR.sub(lambda m: str(env[m.group(1)]), value)
    return value


def perimeter(repo):
    """Declared Phase 1 ruleset: rules, group ranges, role -> group."""
    plays = load_yaml(os.path.join(repo, "ansible-openvpn/openvpn.yaml"))
    play = next(p for p in plays if "perimeter_ruleset" in (p.get("vars") or {}))
    env = play["vars"]
    ranges = {g: ipaddress.ip_network(c) for g, c in env["vpn_group_ranges"].items()}
    rules = []
    for i, r in enumerate(env["perimeter_ruleset"], 1):
        rules.append({
            "id": f"P1-R{i}",
            "group": r["group"],
            "to": ipaddress.ip_network(resolve(r["to"], env), strict=False),
            "port": int(r["port"]) if "port" in r else None,
            "proto": r.get("proto", "any"),
            "comment": r["comment"],
        })
    role_params = next(x for x in play["roles"] if x.get("role") == "kyl191.openvpn")
    role_group = {}
    for role, opts in role_params["openvpn_client_configs"].items():
        addr = ipaddress.ip_address(opts[0].split()[1])          # ifconfig-push <addr> <mask>
        role_group[role] = next(g for g, net in ranges.items() if addr in net)
    return {"rules": rules, "ranges": ranges, "role_group": role_group,
            "dns": env["lab_dns_server"]}


UFW_FWD = re.compile(
    r'"(?P<to>[\d./]+)(?: (?P<port>\d+)/(?P<proto>tcp|udp))?\s+ALLOW FWD\s+'
    r'(?P<src>[\d./]+) on tun0\s+# (?P<comment>[^"]*?)\s*",?$')


def live_ruleset(repo):
    """The last `ufw status verbose` recorded in the Phase 1 journal."""
    runs, cur = [], []
    with open(os.path.join(repo, "journal/phase-1.md")) as fh:
        for line in fh:
            m = UFW_FWD.search(line.strip())
            if m:
                cur.append(m.groupdict())
            elif cur:
                runs.append(cur)
                cur = []
    if cur:
        runs.append(cur)
    return runs[-1] if runs else []


def ziti(repo):
    v = load_yaml(os.path.join(repo, "ansible-openziti/group_vars/all/vars.yaml"))
    return {"services": v["ziti_services"], "roles": v["lab_roles"]}


def netbird(repo):
    v = load_yaml(os.path.join(repo, "ansible-netbird/group_vars/all/vars.yaml"))
    with open(os.path.join(repo, "ansible-netbird/policies-export.json")) as fh:
        export = json.load(fh)
    return {"services": v["netbird_services"], "networks": v["netbird_networks"],
            "roles": v["lab_roles"], "export": export}


ZITI_KINDS = ("edge-router", "ext-jwt-signer", "auth-policy", "identity", "config",
              "service-policy", "service-edge-router-policy", "edge-router-policy", "service")


def journal_created(repo):
    """Ziti objects named in the bootstrap output journaled in Phase 2."""
    seen = set()
    pat = re.compile(r'"created (' + "|".join(ZITI_KINDS) + r') ([\w.-]+)"')
    with open(os.path.join(repo, "journal/phase-2.md")) as fh:
        for line in fh:
            m = pat.search(line)
            if m:
                seen.add((m.group(1), m.group(2)))
    return seen


NB_CREATED = re.compile(r'"created (identity-provider|network|group|resource|router for|policy) ([\w.-]+)')


def journal_created_netbird(repo):
    """NetBird objects named in the bootstrap and access-model output (Phase 2 journal)."""
    seen = set()
    with open(os.path.join(repo, "journal/phase-2.md")) as fh:
        for line in fh:
            m = NB_CREATED.search(line)
            if m:
                seen.add((m.group(1).replace(" for", ""), m.group(2)))
    return seen


def matrices(repo):
    out = {}
    for path in glob.glob(os.path.join(repo, "test-matrix/matrix*.yaml")):
        m = load_yaml(path)
        out[m["phase"]] = m
    return out


def observed(repo):
    """Matrix results, top-level results/ only (excluded and rebuild runs left out)."""
    rows = []
    for path in sorted(glob.glob(os.path.join(repo, "test-matrix/results/*.csv"))):
        with open(path, newline="") as fh:
            rows.extend(csv.DictReader(fh))
    return rows


# --- normalisation ---------------------------------------------------------------

def catalogue(z, p1):
    dests = [{"name": s["name"], "host": s["host"], "port": int(s["port"]), "protos": ("tcp",)}
             for s in z["services"]]
    dests.append({"name": "lab-dns", "host": p1["dns"], "port": 53, "protos": ("udp", "tcp")})
    return dests


def addr(d):
    return f"{d['host']}:{d['port']}/{'+'.join(d['protos'])}"


def p1_rule_matches(rule, dest):
    return (ipaddress.ip_address(dest["host"]) in rule["to"]
            and (rule["port"] is None or rule["port"] == dest["port"])
            and (rule["proto"] == "any" or rule["proto"] in dest["protos"]))


def p1_entitlement(p1, role, dest):
    group = p1["role_group"][role]
    hits = [r["id"] for r in p1["rules"] if r["group"] == group and p1_rule_matches(r, dest)]
    return ("allow", "+".join(hits)) if hits else ("deny", "default deny (routed)")


def ziti_entitlement(z, role, dest):
    svc = next((s for s in z["services"] if s["host"] == dest["host"]
                and int(s["port"]) == dest["port"] and "tcp" in dest["protos"]), None)
    if svc and role in svc["dial_roles"]:
        return "allow", f"{svc['name']}-dial"
    return "deny", "no dial policy" if svc else "no service"


def netbird_index(nb):
    """policy name -> (host, port, proto, source groups) from the deployed export."""
    res_addr = {n["resource"]: n["address"].split("/")[0] for n in nb["networks"]}
    svc_res = {s["name"]: s["resource"] for s in nb["services"]}
    idx = {}
    for pol in nb["export"]:
        if not pol.get("enabled"):
            continue
        for rule in pol["rules"]:
            if not rule.get("enabled") or rule.get("action") != "accept":
                continue
            host = res_addr[svc_res[pol["name"]]]
            for port in rule["ports"]:
                idx[(host, int(port), rule["protocol"])] = (
                    pol["name"], sorted(s["name"] for s in rule["sources"]), rule)
    return idx


def netbird_entitlement(idx, role, dest):
    hit = next((idx[(dest["host"], dest["port"], p)] for p in dest["protos"]
                if (dest["host"], dest["port"], p) in idx), None)
    if hit and role in hit[1]:
        return "allow", hit[0]
    return "deny", "no policy source" if hit else "no policy"


# --- classification ---------------------------------------------------------------

def phase1_effective_deny(mx, role, dest_name):
    """True when Phase 1 lets the role reach the destination but every matrix
    operation on it is expected to be denied (a workload control decides)."""
    exp = mx["phase-1"]["expectations"].get(role, {}).get(dest_name)
    return bool(exp) and all(v == "deny" for v in exp.values())


MEASUREMENT_ONLY = {"perf-iperf3"}   # perf battery target, not a workload in the matrix


def classify(p1_dec, z_dec, dest_name, effective_deny, product_has_dest):
    if p1_dec == z_dec:
        return f"kept ({p1_dec})"
    if p1_dec == "allow":
        if not product_has_dest:
            return "dropped (no counterpart)"
        if effective_deny:
            return "enforcement moved (workload -> network)"
        return "narrowed (allow -> deny)"
    return "widened (deny -> allow)"


DENY_LAYERS = (("database", re.compile(r"permission denied for")),
               ("iam", re.compile(r"AccessDenied")),
               ("network", re.compile(r"timeout|timed out|Connection refused|connection refused|"
                                      r"No route to host|Network is unreachable", re.I)))


def deny_layer(detail):
    for name, pat in DENY_LAYERS:
        if pat.search(detail):
            return name
    return "other"


def breadth_p1(p1, role):
    rules = [r for r in p1["rules"] if r["group"] == p1["role_group"][role]]
    nets = list(ipaddress.collapse_addresses(r["to"] for r in rules))
    addrs = sum(n.num_addresses for n in nets)
    if any(r["port"] is None for r in rules):
        ports = "all"
    else:
        ports = str(len({(str(r["to"]), r["port"]) for r in rules}))
    return addrs, ports


def breadth_granted(ents):
    hosts = {d["host"] for d, dec in ents if dec == "allow"}
    pairs = {(d["host"], d["port"]) for d, dec in ents if dec == "allow"}
    return len(hosts), str(len(pairs))


# --- report -------------------------------------------------------------------------

def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"))
    args = ap.parse_args()
    repo = args.repo
    os.makedirs(args.out, exist_ok=True)

    p1, z, nb, mx = perimeter(repo), ziti(repo), netbird(repo), matrices(repo)
    roles = z["roles"]
    dests = catalogue(z, p1)
    nb_idx = netbird_index(nb)
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, ok, detail))

    # entitlements and changes
    ent_rows, change_rows = [], []
    grants = {ph: collections.defaultdict(list) for ph in PHASES}
    for role in roles:
        for d in dests:
            e = {"phase-1": p1_entitlement(p1, role, d),
                 "phase-2-openziti": ziti_entitlement(z, role, d),
                 "phase-2-netbird": netbird_entitlement(nb_idx, role, d)}
            for ph in PHASES:
                ent_rows.append([ph, role, d["name"], addr(d),
                                 e[ph][0], e[ph][1]])
                grants[ph][role].append((d, e[ph][0]))
            eff = phase1_effective_deny(mx, role, d["name"])
            for ph in PRODUCTS:
                has_dest = e[ph][1] != "no service" and e[ph][1] != "no policy"
                note = "measurement service (perf battery), not a workload" if d["name"] in MEASUREMENT_ONLY else ""
                change_rows.append([ph, role, d["name"], e["phase-1"][0], e[ph][0],
                                    classify(e["phase-1"][0], e[ph][0], d["name"], eff, has_dest), note])

    # effective access from the matrix
    obs = collections.defaultdict(collections.Counter)
    for r in observed(repo):
        key = (r["phase"], r["role"], r["resource"], r["operation"])
        layer = "-" if r["observed"] == "allow" else deny_layer(r["detail"])
        obs[key][(r["observed"], layer)] += 1
    eff_rows = []
    layer_counts = {ph: collections.Counter() for ph in PHASES}
    for ph in PHASES:
        for role, res_map in mx[ph]["expectations"].items():
            for res, ops in res_map.items():
                for op, expected in ops.items():
                    seen = obs.get((ph, role, res, op), collections.Counter())
                    text = "; ".join(f"{dec} ({lay}) x{n}" if lay != "-" else f"{dec} x{n}"
                                     for (dec, lay), n in sorted(seen.items()))
                    majority = seen.most_common(1)[0][0] if seen else ("", "")
                    if expected == "deny" and majority[0] == "deny":
                        layer_counts[ph][majority[1]] += 1
                    layers = sorted({lay for (dec, lay) in seen if dec == "deny"})
                    eff_rows.append([ph, role, res, op, expected, text or "not run",
                                     "+".join(layers) or "-"])

    # consistency checks
    live = live_ruleset(repo)
    declared = []
    for r in p1["rules"]:
        to = str(r["to"]) if r["to"].prefixlen < 32 else str(r["to"].network_address)
        declared.append((to, str(r["port"]) if r["port"] else None,
                         r["proto"] if r["port"] else None, str(p1["ranges"][r["group"]]), r["comment"]))
    live_t = [(x["to"], x["port"], x["proto"], x["src"], x["comment"]) for x in live]
    check("Phase 1: declared ruleset = live ruleset (journal)", sorted(declared) == sorted(live_t),
          f"{len(declared)} declared, {len(live_t)} live")
    z_table = {s["name"]: (s["host"], int(s["port"]), sorted(s["dial_roles"])) for s in z["services"]}
    nb_table = {s["name"]: (s["host"], int(s["port"]), sorted(s["dial_roles"])) for s in nb["services"]}
    check("OpenZiti dial table = NetBird service table", z_table == nb_table,
          f"{len(z_table)} services")
    nb_dep = {v[0]: (k[0], k[1], v[1]) for k, v in nb_idx.items()}
    check("NetBird service table = deployed policies (export)",
          nb_dep == {n: t for n, t in nb_table.items()}, f"{len(nb_dep)} policies deployed")
    for ph in PRODUCTS:
        bad = []
        for role, res_map in mx[ph]["expectations"].items():
            for res, ops in res_map.items():
                d = next((x for x in dests if x["name"] == res), None)
                if d is None:
                    continue                     # S3: IAM only, outside the overlay
                net = next(dec for dd, dec in grants[ph][role] if dd is d)
                exp_any_allow = any(v == "allow" for v in ops.values())
                if exp_any_allow and net != "allow":
                    bad.append(f"{role}/{res}")
                if net == "allow" and not exp_any_allow:
                    bad.append(f"{role}/{res} (network allows, matrix expects deny)")
        check(f"{ph}: network entitlements agree with matrix expectations", not bad, ", ".join(bad))
    ziti_expected = set()
    ziti_expected |= {("edge-router", n) for n in ("aws-edge", "lab-router")}
    ziti_expected |= {("ext-jwt-signer", "keycloak"), ("auth-policy", "keycloak-only"),
                      ("edge-router-policy", "clients-public-router"),
                      ("service-edge-router-policy", "all-services-all-routers")}
    ziti_expected |= {("identity", r) for r in roles}
    for s in z["services"]:
        ziti_expected |= {("config", f"{s['name']}-intercept"), ("config", f"{s['name']}-host"),
                          ("service", s["name"]), ("service-policy", f"{s['name']}-bind"),
                          ("service-policy", f"{s['name']}-dial")}
    ziti_journal = journal_created(repo)
    check("OpenZiti: objects from the service table = objects the bootstrap created (journal)",
          ziti_expected == ziti_journal, f"{len(ziti_expected)} expected, {len(ziti_journal)} journaled")

    nb_expected = {("identity-provider", "keycloak")}
    for n in nb["networks"]:
        nb_expected |= {("network", n["name"]), ("group", n["router_group"]),
                        ("resource", n["resource"]), ("router", n["name"])}
    nb_expected |= {("policy", s["name"]) for s in nb["services"]}
    nb_journal = journal_created_netbird(repo)
    check("NetBird: objects from the service table = objects the bootstrap and access model created (journal)",
          nb_expected == nb_journal, f"{len(nb_expected)} expected, {len(nb_journal)} journaled")

    # sizes
    zc = collections.Counter(k for k, _ in ziti_expected)
    n_rules = sum(len(p["rules"]) for p in nb["export"])
    nb_groups = {s["name"] for p in nb["export"] for r in p["rules"] for s in r["sources"]}
    size_rows = [
        ["phase-1", "routed allow rules (ufw)", len(p1["rules"])],
        ["phase-1", "group address ranges", len(p1["ranges"])],
        ["phase-1", "fixed client addresses (group membership)", len(p1["role_group"])],
        ["phase-2-openziti", "dial policies (access decisions)", sum(1 for _, n in ziti_expected if n.endswith("-dial"))],
        ["phase-2-openziti", "bind policies", sum(1 for _, n in ziti_expected if n.endswith("-bind"))],
        ["phase-2-openziti", "services", zc["service"]],
        ["phase-2-openziti", "configs (intercept + host)", zc["config"]],
        ["phase-2-openziti", "identities (one per role)", zc["identity"]],
        ["phase-2-openziti", "routers, signer, auth policy, router policies",
         zc["edge-router"] + zc["ext-jwt-signer"] + zc["auth-policy"] + zc["edge-router-policy"]
         + zc["service-edge-router-policy"]],
        ["phase-2-openziti", "total objects created", len(ziti_expected)],
        ["phase-2-netbird", "policies (access decisions)", len(nb["export"])],
        ["phase-2-netbird", "policy rules", n_rules],
        ["phase-2-netbird", "role groups (created by JWT group sync at login)", len(nb_groups)],
        ["phase-2-netbird", "networks / resources / routers", f"{len(nb['networks'])} / {len(nb['networks'])} / {len(nb['networks'])}"],
        ["phase-2-netbird", "routing-peer groups", len(nb["networks"])],
        ["phase-2-netbird", "IdP connector (Keycloak)", 1],
        ["phase-2-netbird", "total objects (bootstrap, access model, login-created groups)",
         len(nb_expected) + len(nb_groups)],
    ]
    breadth_rows = []
    for role in roles:
        a1, p1p = breadth_p1(p1, role)
        row = [role, p1["role_group"][role], a1, p1p]
        for ph in PRODUCTS:
            row += list(breadth_granted(grants[ph][role]))
        breadth_rows.append(row)

    # write
    def write_csv(name, header, rows):
        with open(os.path.join(args.out, name), "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(header)
            w.writerows(rows)

    write_csv("entitlements.csv", ["phase", "role", "destination", "address", "decision", "granted_by"], ent_rows)
    write_csv("changes.csv", ["product", "role", "destination", "phase_1", "product_decision", "change", "note"], change_rows)
    write_csv("effective.csv", ["phase", "role", "resource", "operation", "expected", "observed", "deny_layers"], eff_rows)

    ent = {(r[0], r[1], r[2]): r for r in ent_rows}
    grid = [[role, d["name"]] + [f"{ent[(ph, role, d['name'])][4]} ({ent[(ph, role, d['name'])][5]})"
                                 for ph in PHASES]
            for role in roles for d in dests]
    change_summary = collections.Counter((r[0], r[5]) for r in change_rows)
    changed = [r for r in change_rows if not r[5].startswith("kept")]
    layer_rows = [[ph] + [layer_counts[ph][l] for l in ("network", "database", "iam", "other")] for ph in PHASES]

    lines = [
        "# Phase 3 translation summary",
        "",
        "Generated by `analysis/translation.py` from committed artifacts; do not edit by hand.",
        "Method and terms: `docs/phase-3-translation.md`.",
        "",
        "## Consistency checks",
        "",
        md_table(["check", "result", "detail"],
                 [[n, "pass" if ok else "FAIL", d] for n, ok, d in checks]),
        "",
        "## Network entitlements (decision and granting rule or policy)",
        "",
        "Phase 1 rules: " + "; ".join(f"{r['id']} {r['comment']}" for r in p1["rules"]) + ".",
        "",
        md_table(["role", "destination", "phase-1", "phase-2-openziti", "phase-2-netbird"], grid),
        "",
        "## Changes from Phase 1",
        "",
        md_table(["product", "change", "count"],
                 [[p, c, n] for (p, c), n in sorted(change_summary.items())]),
        "",
        md_table(["product", "role", "destination", "phase-1", "product", "change", "note"], changed),
        "",
        "## Breadth at the network layer",
        "",
        "Addresses reachable, and address:port pairs (\"all\" when a rule has no port).",
        "",
        md_table(["role", "phase-1 group", "phase-1 addresses", "phase-1 ports",
                  "openziti addresses", "openziti address:ports", "netbird addresses", "netbird address:ports"],
                 breadth_rows),
        "",
        "## Size of the access-control artifacts",
        "",
        md_table(["phase", "object", "count"], size_rows),
        "",
        "## Expected denies by enforcement layer (matrix, majority observation)",
        "",
        md_table(["phase", "network", "database", "iam", "other"], layer_rows),
        "",
        "## Effective access (matrix)",
        "",
        md_table(["phase", "role", "resource", "operation", "expected", "observed", "deny layers observed"], eff_rows),
        "",
    ]
    with open(os.path.join(args.out, "translation-summary.md"), "w") as fh:
        fh.write("\n".join(lines))

    for n, ok, d in checks:
        print(f"{'pass' if ok else 'FAIL'}  {n}" + (f"  [{d}]" if d else ""))
    print(f"wrote {os.path.relpath(args.out)}/: entitlements.csv, changes.csv, effective.csv, translation-summary.md")
    sys.exit(0 if all(ok for _, ok, _ in checks) else 1)


if __name__ == "__main__":
    main()
