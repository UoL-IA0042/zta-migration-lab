#!/usr/bin/env python3
"""NetBird management-API bootstrap for the lab (docs/phase-2-netbird.md).

Runs on the edge host against the combined server on loopback. Two
subcommands, both convergent (create when missing, update when present,
print "created ..." / "updated ..." / "deleted ..." for each change):

  bootstrap     first admin + API token (POST /api/setup, once), Keycloak
                as the embedded IdP's OIDC connector, account settings
                (JWT group sync), Default policy removed, routing-peer
                groups, networks with their resource and router, one-off
                setup keys for routing peers not yet enrolled
  access-model  one policy per service: TCP port, source = the role
                groups created by JWT group sync, destination = the
                network resource. Role groups appear only after a role's
                first login, so this is re-run after logins; missing
                groups are reported, not created.

Input: a JSON file rendered by Ansible (no secrets). Secrets from the
environment: NB_OWNER_PASSWORD, NB_KEYCLOAK_SECRET. The API token is kept
in the token file named in the input (root-only).
Standard library only.
"""
import json
import os
import sys
import urllib.error
import urllib.request


class Api:
    def __init__(self, base, token=None):
        self.base = base.rstrip("/")
        self.token = token

    def call(self, method, path, body=None, ok=(200,)):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        if self.token:
            req.add_header("Authorization", "Token " + self.token)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                status = resp.status
        except urllib.error.HTTPError as err:
            raw, status = err.read(), err.code
        if status not in ok:
            sys.exit(f"{method} {path}: HTTP {status}: {raw[:300].decode(errors='replace')}")
        return json.loads(raw) if raw.strip() else None

    def get(self, path):
        return self.call("GET", path)


def say(*parts):
    print(*parts, flush=True)


def by_name(items, name):
    return next((i for i in items if i.get("name") == name), None)


# --- bootstrap ----------------------------------------------------------------

def ensure_token(cfg):
    api = Api(cfg["api"])
    path = cfg["token_file"]
    if api.get("/api/instance").get("setup_required"):
        resp = api.call("POST", "/api/setup", {
            "email": cfg["owner_email"],
            "password": os.environ["NB_OWNER_PASSWORD"],
            "name": cfg["owner_name"],
            "create_pat": True,
            "pat_expire_in": cfg["token_days"],
        })
        token = resp.get("personal_access_token")
        if not token:
            sys.exit("setup did not return a token: is NB_SETUP_PAT_ENABLED=true set on the server?")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            fh.write(token)
        say("created owner", cfg["owner_email"], "and API token")
    elif not os.path.exists(path):
        sys.exit(f"instance is set up but {path} is missing; the token cannot be recovered")
    with open(path) as fh:
        return Api(cfg["api"], fh.read().strip())


def ensure_idp(api, cfg):
    want = {"type": "oidc", "name": cfg["idp"]["name"], "issuer": cfg["idp"]["issuer"],
            "client_id": cfg["idp"]["client_id"], "client_secret": os.environ["NB_KEYCLOAK_SECRET"]}
    cur = by_name(api.get("/api/identity-providers") or [], want["name"])
    if cur is None:
        api.call("POST", "/api/identity-providers", want)
        say("created identity-provider", want["name"])
    elif (cur.get("issuer"), cur.get("client_id")) != (want["issuer"], want["client_id"]):
        api.call("PUT", f"/api/identity-providers/{cur['id']}", want)
        say("updated identity-provider", want["name"])


def ensure_settings(api, cfg):
    account = api.get("/api/accounts")[0]
    settings = dict(account["settings"])
    extra = dict(settings.get("extra") or {})
    changed = False
    for key, val in cfg["settings"].items():
        if settings.get(key) != val:
            settings[key] = val
            changed = True
    for key, val in cfg["settings_extra"].items():
        if extra.get(key) != val:
            extra[key] = val
            changed = True
    if changed:
        settings["extra"] = extra
        api.call("PUT", f"/api/accounts/{account['id']}", {"settings": settings})
        say("updated account settings")


def remove_default_policy(api):
    # The new account's "Default" policy lets every peer reach every other peer.
    for pol in api.get("/api/policies") or []:
        if pol.get("name") == "Default":
            api.call("DELETE", f"/api/policies/{pol['id']}")
            say("deleted policy Default (all peers to all peers)")


def ensure_group(api, name):
    grp = by_name(api.get("/api/groups") or [], name)
    if grp is None:
        grp = api.call("POST", "/api/groups", {"name": name})
        say("created group", name)
    return grp["id"]


def ensure_network(api, net):
    cur = by_name(api.get("/api/networks") or [], net["name"])
    if cur is None:
        cur = api.call("POST", "/api/networks", {"name": net["name"], "description": net["description"]})
        say("created network", net["name"])
    nid = cur["id"]
    router_group = ensure_group(api, net["router_group"])
    res_req = {"name": net["resource"], "description": net["description"],
               "address": net["address"], "enabled": True, "groups": []}
    res = by_name(api.get(f"/api/networks/{nid}/resources") or [], net["resource"])
    if res is None:
        api.call("POST", f"/api/networks/{nid}/resources", res_req)
        say("created resource", net["resource"], net["address"])
    elif res.get("address") != net["address"] or not res.get("enabled"):
        api.call("PUT", f"/api/networks/{nid}/resources/{res['id']}", res_req)
        say("updated resource", net["resource"])
    rt_req = {"peer_groups": [router_group], "metric": 9999, "masquerade": True, "enabled": True}
    routers = api.get(f"/api/networks/{nid}/routers") or []
    if not routers:
        api.call("POST", f"/api/networks/{nid}/routers", rt_req)
        say("created router for", net["name"], "via group", net["router_group"])
    else:
        rt = routers[0]
        if rt.get("peer_groups") != [router_group] or not rt.get("masquerade") or not rt.get("enabled"):
            api.call("PUT", f"/api/networks/{nid}/routers/{rt['id']}", rt_req)
            say("updated router for", net["name"])
    return router_group


def setup_keys_for_missing_peers(api, cfg, router_groups):
    # After a node reset its local identity is gone: delete the stale peer so
    # a new key is issued (cfg "reenroll", from -e netbird_reenroll=...).
    # Peers are matched on "name", which `netbird up --hostname` sets; the
    # API's "hostname" is the OS hostname (ip-10-100-1-x on EC2).
    for peer in api.get("/api/peers") or []:
        if peer.get("name") in cfg.get("reenroll", []):
            api.call("DELETE", f"/api/peers/{peer['id']}")
            say("deleted peer", peer["name"], "(re-enroll)")
    peers = {p.get("name") for p in api.get("/api/peers") or []}
    os.makedirs(cfg["key_dir"], mode=0o700, exist_ok=True)
    for net in cfg["networks"]:
        host = net["peer_hostname"]
        path = os.path.join(cfg["key_dir"], host + ".key")
        if host in peers:
            if os.path.exists(path):
                os.remove(path)
            continue
        key = api.call("POST", "/api/setup-keys", {
            "name": f"enroll-{host}", "type": "one-off", "expires_in": 3600,
            "auto_groups": [router_groups[net["name"]]], "usage_limit": 1, "ephemeral": False,
        })
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            fh.write(key["key"])
        say("created setup-key for", host)


def bootstrap(cfg):
    api = ensure_token(cfg)
    ensure_idp(api, cfg)
    ensure_settings(api, cfg)
    remove_default_policy(api)
    router_groups = {net["name"]: ensure_network(api, net) for net in cfg["networks"]}
    setup_keys_for_missing_peers(api, cfg, router_groups)
    say("bootstrap complete")


# --- access model ---------------------------------------------------------------

def access_model(cfg):
    with open(cfg["token_file"]) as fh:
        api = Api(cfg["api"], fh.read().strip())
    groups = api.get("/api/groups") or []
    jwt_groups = {g["name"]: g["id"] for g in groups if g.get("issued") == "jwt"}
    missing = [r for r in cfg["roles"] if r not in jwt_groups]
    resources = {}
    for net in api.get("/api/networks") or []:
        for res in api.get(f"/api/networks/{net['id']}/resources") or []:
            resources[res["name"]] = res
    policies = api.get("/api/policies") or []
    for svc in cfg["services"]:
        res = resources.get(svc["resource"])
        if res is None:
            sys.exit(f"resource {svc['resource']} missing: run site.yaml first")
        sources = [jwt_groups[r] for r in svc["dial_roles"] if r in jwt_groups]
        name = svc["name"]
        cur = by_name(policies, name)
        if not sources:
            say("pending", name, "(no role group has logged in yet)")
            continue
        rule = {"name": name, "description": f"{svc['host']}:{svc['port']}", "enabled": True,
                "action": "accept", "bidirectional": False, "protocol": "tcp",
                "ports": [str(svc["port"])], "sources": sources,
                "destinationResource": {"id": res["id"], "type": res["type"]}}
        body = {"name": name, "description": f"{name} for {', '.join(svc['dial_roles'])}",
                "enabled": True, "rules": [rule]}
        if cur is None:
            api.call("POST", "/api/policies", body)
            say("created policy", name, "sources", ",".join(r for r in svc["dial_roles"] if r in jwt_groups))
            continue
        old = (cur.get("rules") or [{}])[0]
        old_sources = sorted(s["id"] if isinstance(s, dict) else s for s in old.get("sources") or [])
        old_dest = (old.get("destinationResource") or {}).get("id")
        if (old_sources != sorted(sources) or old.get("ports") != rule["ports"]
                or old_dest != res["id"] or old.get("protocol") != "tcp" or not cur.get("enabled")):
            if old.get("id"):
                rule["id"] = old["id"]
            api.call("PUT", f"/api/policies/{cur['id']}", body)
            say("updated policy", name, "sources", ",".join(r for r in svc["dial_roles"] if r in jwt_groups))
    if missing:
        say("missing role groups (log in once as each, then re-run):", ",".join(missing))
    with open(cfg["export_file"], "w") as fh:
        json.dump(api.get("/api/policies") or [], fh, indent=2, sort_keys=True)
        fh.write("\n")
    say("access model complete")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("bootstrap", "access-model"):
        sys.exit("usage: netbird-admin.py bootstrap|access-model <config.json>")
    with open(sys.argv[2]) as fh:
        config = json.load(fh)
    (bootstrap if sys.argv[1] == "bootstrap" else access_model)(config)
