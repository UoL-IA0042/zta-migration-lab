## 2026-10-11 08:45-09:15 | phase-2 | openziti | planning
Designed the migration from the OpenVPN remote-access VPN to OpenZiti
(`docs/phase-2-openziti.md`, on branch `phase-2-openziti`). Decisions:
1. Public OpenZiti components (controller, public edge router, IdP
   reverse proxy) run on a new AWS edge host. The lab only dials out, so
   after the migration there is no inbound port at home and the Xfinity
   1194/udp forward is removed.
2. Public names are sslip.io names on the edge host's Elastic IP
   (`idp|ctrl|router.<edge-ip-dashed>.sslip.io`) with a Let's Encrypt
   certificate for the IdP. The names embed the public IP, so they are
   derived from `LAB_EDGE_IP` at run time and never committed.
3. OpenZiti is migrated first, NetBird second.
4. Only the remote-access VPN is replaced. The Phase 1 site-to-site
   tunnel (tpi2-4 to the AWS hub) stays as infrastructure, so the path
   to AWS is the same in both phases.
5. Login is Keycloak OIDC as the primary authenticator (`keycloak-only`
   auth policy). Certificate plus OIDC (secondary) is not used because it
   is broken on the macOS tunneler; primary external auth works on Ziti
   Desktop Edge for macOS 2.51 and later.

Services intercept the same addresses and ports as Phase 1, so the test
matrix keeps its resources and only the expectations change. Expected
differences: contractor loses the network path to postgres (deny by
network instead of by DB grant); developer and analyst lose
legacy-service. S3 is unchanged (IAM, outside the overlay).

## 2026-10-11 09:27-09:49 | phase-2 | openziti | coding
Implemented design steps 1-3 on branch `phase-2-openziti`. Nothing is
applied or deployed yet. The checks so far were offline only: syntax
checks, rendering the templates with and without `LAB_EDGE_IP`, and
`iptables-restore --test` on a copy of tpi2-4's ufw rules.

Step 1, terraform-aws: new `phase2-openziti.tf`, all behind
`enable_openziti` (default false), so with the flag unset the AWS side
is unchanged from Phase 1 (to confirm with `terraform plan`). Adds the
edge host (t4g.small) in its own subnet 10.100.1.0/24 with its own route
table (internet via the IGW, on-prem via the hub's network interface), a
security group open to the internet on 80, 443, 1280 and 3022 and SSH
from the lab egress address only, and an Elastic IP. The hub security
group in `main.tf` gains one ingress rule, edge subnet to the Keycloak
port, also only when the flag is set.
The three new inputs were first declared in `phase2-openziti.tf` and
were moved to `variables.tf`, where the other inputs are (commit
910363b).

Step 2, ansible-keycloak: the issuer becomes
`https://idp.<edge-ip-dashed>.sslip.io/realms/lab` when `LAB_EDGE_IP` is
set and stays `http://10.0.0.72:8080/realms/lab` otherwise.
`KC_PROXY_HEADERS=xforwarded` is set only in public mode. The `openziti`
client becomes a public client with PKCE (S256), redirect
`http://localhost:20314/auth/callback` and an audience mapper, so
access tokens carry `aud: openziti`. Keycloak's realm import skips
existing realms, so the change needs a clean redeploy:
`-e keycloak_reset=yes` deletes `pgdata` and re-imports the realm from
the template. This is part of the migration effort, not a phase 0
change; the tpi2-2 golden image stays as it is. The playbook now checks
that the served issuer equals the configured one.

Step 3, ansible-openziti: new `idp-path.yaml` publishes Keycloak through
the edge host before any OpenZiti component exists. On tpi2-4: a ufw
route rule allowing the edge subnet in on `s2s0` to 10.0.0.72:8080
(routed traffic is otherwise denied by the Phase 1 perimeter ruleset),
and a MASQUERADE block in `before.rules` with its own marker, so
tpi2-2's replies return through tpi2-4. On the edge host: Caddy 2.11
with automatic Let's Encrypt (no ACME e-mail), proxying to Keycloak
through the hub and the tunnel. The last play fetches the discovery
document from the Mac and checks the issuer. The inventory gains the
groups `edge_host` (address from `LAB_EDGE_IP`) and `lab_gateway`
(tpi2-4).

## 2026-10-11 09:55-11:00 | phase-2 | openziti | deployment
Step 4, openziti deployment

Caddy image digest: `sha256:f2a1290d0463aad60660d4ec134943f183ee2a5f6c3eb7bf32dd984f2f020772`

```
TASK [Show image digests] **************************************************************************************************************************************************
ok: [ziti-edge] => {
    "digests.stdout_lines": [
        "openziti/ziti-controller@sha256:834cb8a784b55716a56c0aab15d8809bc553834a534dbb8986d0711cb5c34dfc",
        "openziti/ziti-router@sha256:540e5450f2ecd72cdc0db94bb7d969814f826e19d3bd4bbde192483c38bb5423"
    ]
}

TASK [Show image digest] ***************************************************************************************************************************************************
ok: [tpi2-4] => {
    "lab_digest.stdout": "openziti/ziti-router@sha256:540e5450f2ecd72cdc0db94bb7d969814f826e19d3bd4bbde192483c38bb5423"
}

TASK [Show access-model changes] *******************************************************************************************************************************************
ok: [ziti-edge] => {
    "model.stdout_lines": [
        "created edge-router aws-edge",
        "created edge-router lab-router",
        "created ext-jwt-signer keycloak",
        "created auth-policy keycloak-only",
        "created identity remote-admin",
        "created identity remote-developer",
        "created identity remote-analyst",
        "created identity remote-contractor",
        "created config intranet-web-intercept",
        "created config intranet-web-host",
        "created service intranet-web",
        "created service-policy intranet-web-bind",
        "created service-policy intranet-web-dial",
        "created config file-service-intercept",
        "created config file-service-host",
        "created service file-service",
        "created service-policy file-service-bind",
        "created service-policy file-service-dial",
        "created config postgres-intercept",
        "created config postgres-host",
        "created service postgres",
        "created service-policy postgres-bind",
        "created service-policy postgres-dial",
        "created config legacy-service-intercept",
        "created config legacy-service-host",
        "created service legacy-service",
        "created service-policy legacy-service-bind",
        "created service-policy legacy-service-dial",
        "created config aws-app-intercept",
        "created config aws-app-host",
        "created service aws-app",
        "created service-policy aws-app-bind",
        "created service-policy aws-app-dial",
        "created config perf-iperf3-intercept",
        "created config perf-iperf3-host",
        "created service perf-iperf3",
        "created service-policy perf-iperf3-bind",
        "created service-policy perf-iperf3-dial",
        "created edge-router-policy clients-public-router",
        "created service-edge-router-policy all-services-all-routers",
        "bootstrap complete"
    ]
}

TASK [Overlay state] *******************************************************************************************************************************************************
ok: [ziti-edge] => {
    "msg": {
        "links": [
            {
                "dst": "aws-edge",
                "src": "lab-router",
                "state": "Connected"
            }
        ],
        "routers": [
            {
                "isOnline": true,
                "name": "lab-router"
            },
            {
                "isOnline": true,
                "name": "aws-edge"
            }
        ],
        "terminators": [
            {
                "router": "lab-router",
                "service": "intranet-web"
            },
            {
                "router": "lab-router",
                "service": "postgres"
            },
            {
                "router": "lab-router",
                "service": "file-service"
            },
            {
                "router": "lab-router",
                "service": "perf-iperf3"
            },
            {
                "router": "aws-edge",
                "service": "aws-app"
            },
            {
                "router": "lab-router",
                "service": "legacy-service"
            }
        ]
    }
}
```

## 2026-10-11 11:00-11:15 | phase-2 | openvpn | deployment
Step 5, decomissioning openvpn clients.

```
TASK [Show ufw rules before] ***********************************************************************************************************************************************
ok: [tpi2-4] => {
    "ufw_before.stdout_lines": [
        "Status: active",
        "",
        "     To                         Action      From",
        "     --                         ------      ----",
        "[ 1] 1194/udp                   ALLOW IN    Anywhere                  ",
        "[ 2] Anywhere on tun0           ALLOW IN    Anywhere                  ",
        "[ 3] 10.0.0.0/24                ALLOW FWD   10.9.0.16/28 on tun0       # staff -> on-prem LAN",
        "[ 4] 10.100.0.0/16              ALLOW FWD   10.9.0.16/28 on tun0       # staff -> AWS VPC",
        "[ 5] 10.0.0.73 8080/tcp         ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> intranet-web",
        "[ 6] 10.0.0.73 5432/tcp         ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> postgres (db denies)",
        "[ 7] 10.0.0.153 53/udp          ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> lab DNS",
        "[ 8] 10.0.0.153 53/tcp          ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> lab DNS (tcp)",
        "[ 9] Anywhere                   ALLOW IN    10.0.0.0/24                # lab LAN -> tpi2-4 (ssh, node_exporter)",
        "[10] 10.0.0.72 8080/tcp         ALLOW FWD   10.100.1.0/24 on s2s0      # phase 2: edge host IdP proxy -> Keycloak",
        "[11] 1194/udp (v6)              ALLOW IN    Anywhere (v6)             ",
        "[12] Anywhere (v6) on tun0      ALLOW IN    Anywhere (v6)             "
    ]
}

TASK [Show removed rules (journal; the perimeter ruleset as deployed)] *****************************************************************************************************
ok: [tpi2-4] => {
    "removed.stdout_lines": [
        "removed: 1194/udp                   ALLOW IN    Anywhere                  ",
        "removed: Anywhere on tun0           ALLOW IN    Anywhere                  ",
        "removed: 10.0.0.0/24                ALLOW FWD   10.9.0.16/28 on tun0       # staff -> on-prem LAN",
        "removed: 10.100.0.0/16              ALLOW FWD   10.9.0.16/28 on tun0       # staff -> AWS VPC",
        "removed: 10.0.0.73 8080/tcp         ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> intranet-web",
        "removed: 10.0.0.73 5432/tcp         ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> postgres (db denies)",
        "removed: 10.0.0.153 53/udp          ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> lab DNS",
        "removed: 10.0.0.153 53/tcp          ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> lab DNS (tcp)",
        "removed: 1194/udp (v6)              ALLOW IN    Anywhere (v6)             ",
        "removed: Anywhere (v6) on tun0      ALLOW IN    Anywhere (v6)             "
    ]
}

TASK [Remote access gone; site-to-site and forwarding intact] **************************************************************************************************************
ok: [tpi2-4] => {
    "changed": false,
    "msg": "state: {\"server_active\": \"inactive\", \"udp1194_listeners\": \"0\", \"tun0_present\": \"no\", \"vpn_rules_left\": \"0\", \"vpn_nat_left\": \"0\", \"routed_default\": \"deny (routed)\", \"s2s_active\": \"active\", \"s2s_route\": \"1\", \"ip_forward\": \"1\"}"
}

TASK [Show ufw state after] ************************************************************************************************************************************************
ok: [tpi2-4] => {
    "ufw_after.stdout_lines": [
        "Status: active",
        "Logging: on (low)",
        "Default: deny (incoming), allow (outgoing), deny (routed)",
        "New profiles: skip",
        "",
        "To                         Action      From",
        "--                         ------      ----",
        "Anywhere                   ALLOW IN    10.0.0.0/24                # lab LAN -> tpi2-4 (ssh, node_exporter)",
        "",
        "10.0.0.72 8080/tcp         ALLOW FWD   10.100.1.0/24 on s2s0      # phase 2: edge host IdP proxy -> Keycloak"
    ]
}
```

Removing the port-forward for UDP/1194.
Removing the Phase 1 OpenVPN client profiles.
Re-ran the `ansible-openziti` playbook and confirmed there were no changes.

## 2026-10-11 13:45-14:45 | phase-2 | openziti | testing
Ziti Desktop Edge version = 2.59

- Defect: Ziti Desktop Edge's External Auth button stayed disabled after the identity was added, so the Keycloak login could not start. Cause: Ziti Desktop Edge 2.59 for macOS, not investigated further. Fix: workaround, quit and restart the app.
- Defect: re-adding the identity for the next role (`remote-developer`) by its URL failed with a TLS error. Cause: not determined. Fix: workaround, add each identity from its network JWT.

`remote-admin` run of `test-matrix` was successful.


`remote-admin` run of `perf-battery`
Pre-checks passed
Ping test and CSV file name for lab performance testing
```
$ ping -c 30 1.1.1.1 | tail -1
round-trip min/avg/max/stddev = 31.300/46.455/136.150/24.733 ms

phase-2-openziti_openziti_20261011T205853Z_4c481c1e0822.csv
```

Ping test and CSV file name for AWS performance testing
```
$ ping -c 30 1.1.1.1 | tail -1
round-trip min/avg/max/stddev = 31.554/59.466/108.630/23.473 ms

phase-2-openziti_openziti-aws_20261011T210641Z_667c2e3e2855.csv
```

`remote-developer` run of `test-matrix` was successful
CSV results file: phase-2-openziti_remote-developer_20261011T211654Z_e3fdca541888.csv


`remote-analyst` run of `test-matrix` was successful
CSV results file: phase-2-openziti_remote-analyst_20261011T212248Z_695f6f812590.csv

`remote-contractor` run of `test-matrix` was successful
CSV results file: phase-2-openziti_remote-contractor_20261011T212555Z_327a94be666e.csv

Some observations:
* On-prem latency is about 115 ms higher, but much steadier. The OpenZiti p50 was 258–262 ms across reps, against 129–1135 ms for the VPN, and the SYN-retransmit peaks are gone. Two likely contributors, consistent with the design but not yet tested: the route now goes through AWS, and curl opens a new connection per sample, so each sample includes setting up a new path through the overlay.
* The AWS path is about even (257 vs 265 ms). OpenZiti reaches aws-app directly from the public router, not through home and the site-to-site tunnel.
* Upload is capped at about 2.2 Mbps (2.16–2.26 in every rep), against about 7.6 on the VPN. A spread that tight looks like a fixed bottleneck, not hotspot noise. If you have ten minutes, iperf3 -c 10.0.0.73 -P 4 (4 streams) would show whether it’s a per-stream limit. Otherwise, list it as a limitation to investigate.

Aggregate results:
| phase | role | pass | fail | error | rate |
---|---|---|---|---|---|
| phase-1 | remote-admin | 8 | 0 | 0 | 100.0% |
| phase-1 | remote-analyst | 8 | 0 | 0 | 100.0% |
| phase-1 | remote-contractor | 8 | 0 | 0 | 100.0% |
| phase-1 | remote-developer | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-admin | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-analyst | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-contractor | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-developer | 8 | 0 | 0 | 100.0% |

## 2026-10-11 15:00-16:45 | phase-2 | netbird | deployment
As part of the next Phase 2 deployment of netbird, resources from the previous Phase 2 deployment of openziti need to be reset.

Steps to reset the deployment environment:
1. Destory the current resources managed by terraform
2. Reset the relevant nodes back to a known state from the `node-reset/` playbooks
3. Verify keycloak is back to its private issuer with the following command
```
   curl -s http://10.0.0.72:8080/realms/lab/.well-known/openid-configuration | jq -r .issuer
```
expecting the following response `http://10.0.0.72:8080/realms/lab`
4. Redeploy OpenVPN from `ansible-openvpn/`
5. Re-add the port-forward for OpenVPN
6. Turn Ziti Desktop Edge off and remove its identity, then import the new OpenVPN profiles from ~/ovpn-client-configs/
7. Re-check the Phase 1 matrix, on the hotspot, all four roles, from `test-matrix/`. Results go in a separate folder so they don’t mix with the Phase 1 data

Caddy image hash
`sha256:f2a1290d0463aad60660d4ec134943f183ee2a5f6c3eb7bf32dd984f2f020772`

Some results are being excluded because it is a result of restting the environment for the next experiments with netbird.

Resetting the environment took a little more work than expected, but it is now clean and the baseline `test-matrix` results are recorded.

- Defect: SSH and Ansible to tpi2-3 failed with `Connection refused` during the reset. Cause: Ziti Desktop Edge was still running, and its route (`utun4`) captured 10.0.0.73. Fix: quit Ziti Desktop Edge.
- Defect: the Phase 1 re-check failed for `remote-admin` (6 FAIL, timeouts; CSV excluded). Cause: a stale `sudo openvpn` client from an earlier session, holding the old PKI, kept retrying alongside the new one. Fix: killed the stale process; the new connection completed after a delay.
- Defect: `idp-path.yaml` got HTTP 502 for the issuer's discovery document. Cause: the site-to-site tunnel was down, because `openvpn.yaml` had not been re-run on the reset tpi2-4. Fix: re-ran `openvpn.yaml`.

Deploying Netbird from `ansible-netbird` playbook.

```
TASK [Show bootstrap changes] ******************************************************************************************************************************
ok: [nb-edge] => {
    "bootstrap.stdout_lines": [
        "created owner nb-admin@lab.example.com and API token",
        "created identity-provider keycloak",
        "updated account settings",
        "deleted policy Default (all peers to all peers)",
        "created network lab",
        "created group routers-lab",
        "created resource lab-workloads",
        "created router for lab via group routers-lab",
        "created network aws",
        "created group routers-aws",
        "created resource aws-app",
        "created router for aws via group routers-aws",
        "created setup-key for lab node",
        "created setup-key for AWS node",
        "bootstrap complete"
    ]
}

TASK [Show image digests] **************************************************************************************************************************************************
ok: [nb-edge] => {
    "digests.stdout_lines": [
        "netbirdio/netbird-server@sha256:05b3d8d6d056e5062a2965d4d6e5d6d83f09f2bf9133947a8e5972e0e0e7a261",
        "netbirdio/dashboard@sha256:70e0fc6dd3b7758148d182fb55ecd8d4f9ce01e9bba56c9389224e0b8354009d"
    ]
}

TASK [Show the client version] *********************************************************************************************************************************************
ok: [tpi2-4] => {
    "nb_version.stdout": "0.80.0"
}
ok: [nb-edge] => {
    "nb_version.stdout": "0.80.0"
}

TASK [Show access-model changes and pending roles] *********************************************************************************************************
ok: [nb-edge] => {
    "model.stdout_lines": [
        "pending intranet-web (no role group has logged in yet)",
        "pending file-service (no role group has logged in yet)",
        "pending postgres (no role group has logged in yet)",
        "pending legacy-service (no role group has logged in yet)",
        "pending aws-app (no role group has logged in yet)",
        "pending perf-iperf3 (no role group has logged in yet)",
        "missing role groups (log in once as each, then re-run): remote-admin,remote-developer,remote-analyst,remote-contractor",
        "access model complete"
    ]
}
```

The first run enrolled both routing peers (client 0.80.0, so the package version string was fine). Its final check then failed on the name mismatch, a defect fixed in 4a14645.

- Defect: the routing-peer check in `site.yaml` failed although both peers were connected. Cause: it matched the API's `hostname` (the OS hostname) instead of the peer `name` set by `--hostname`; the bootstrap had the same bug and would have enrolled `nb-edge` a second time on a re-run. Fix: match on `name` (4a14645).

Verified `ufw` and `iptables` look correct. Decommissioned the OpenVPN clients.

```
$ netbird version
0.80.0
$ netbird down
Disconnected
$ netbird profile add remote-admin && netbird profile select remote-admin
Profile added: 86da00cf  remote-admin
Profile switched to: 86da00cf
```

## 2026-10-11 16:45-18:30 | phase-2 | netbird | deployment
First login as `remote-admin`, from the profile created above.

- Defect: `netbird up` on the Mac failed with `DeadlineExceeded`. Cause: the edge IP was mistyped in the management URL. Fix: build the URL from `LAB_EDGE_IP` (`${LAB_EDGE_IP//./-}`).

The first attempt registered the Mac as `nb-admin`, not `remote-admin`: `netbird up` opened the default browser, which still had the dashboard admin's NetBird session, so the login never reached Keycloak and no JWT group was created. Deregistered the peer (`netbird deregister`) and changed the runbook (8b6c990): log in with `netbird up --no-browser`, open the printed URL in a private window, and choose Keycloak.

- Defect: the first `remote-admin` login registered the Mac as `nb-admin`. Cause: `netbird up` opened the default browser, which reused the dashboard admin's NetBird session, so the login never reached Keycloak. Fix: `netbird deregister`, then log in with `--no-browser` in a private window (8b6c990).

The second attempt went through Keycloak and the client reported `Login successful` and `Connected`, but `netbird status` showed `Networks: -`. The `remote-admin` matrix (hotspot) had 6 FAIL, all timeouts; the CSV is excluded (`results/excluded/`). Re-running `access-model.yaml` still listed every role as missing, and the admin API showed only `nb-admin` in `/api/users` and only `All`, `routers-lab` and `routers-aws` in `/api/groups`. The Keycloak connector itself was configured correctly (`/api/identity-providers`).

The server log gave the cause: gRPC streams for two account IDs, the bootstrap account (`db629vnnf72s73ektihg`, both routing peers) and a second one (`db62kdnnf72s73ektnbg`, the Mac). The Keycloak login had created a new, empty NetBird account for `remote-admin` instead of joining the admin's. The admin token only sees its own account, so the user, its group and the Mac's peer were invisible to it, and no network or policy applied to the Mac.

Deviation found in implementation (NetBird v0.80.0 source):
- Users join an existing account only through single account mode, which looks the account up by its domain (`netbird.selfhosted`, category private, primary for the domain).
- The headless bootstrap creates the owner through `POST /api/setup` with an API token. That path provisions the account without a domain; only an interactive owner login would set it. So the first Keycloak user found no account for the domain and got one of its own.
- Accounts cannot be merged, so the deployment had to be wiped.

Fix (47c70e9): after the bootstrap, `site.yaml` checks the store and, on a fresh install, stops the server, writes the single-account domain into the owner's account, and starts it again, before any user can log in. It stops with a pointer to the README if more than one account exists. The routing peers now run `netbird down` before enrolling, so they enroll again after a wipe. This is another case where the headless, configuration-as-code deployment needed a workaround that an interactive deployment would not.

- Defect: the `remote-admin` user and the Mac's peer landed in a second NetBird account, invisible to the admin token and outside every network and policy (matrix 6 FAIL, timeouts; CSV excluded). Cause: `POST /api/setup` creates the owner's account without the single-account domain, so single account mode found no account for the first Keycloak login. Fix: `site.yaml` writes the domain into the owner's account before any login (47c70e9); server state wiped and redeployed.

Wiped the server state (secrets and Keycloak kept) and redeployed:
```
# edge host
cd /opt/netbird && sudo docker compose down
sudo rm -rf data/* admin.token enroll/*
# Mac, ansible-netbird/
netbird down
ansible-playbook -i inventory.yaml --vault-password-file ../.vault-pass site.yaml
```

```
TASK [Show bootstrap changes (journal these)] ******************************************************************************************************************************
ok: [nb-edge] => {
    "bootstrap.stdout_lines": [
        "created owner nb-admin@lab.example.com and API token",
        "created identity-provider keycloak",
        "updated account settings",
        "deleted policy Default (all peers to all peers)",
        "created network lab",
        "created group routers-lab",
        "created resource lab-workloads 10.0.0.73/32",
        "created router for lab via group routers-lab",
        "created network aws",
        "created group routers-aws",
        "created resource aws-app 10.100.10.10/32",
        "created router for aws via group routers-aws",
        "created setup-key for tpi2-4",
        "created setup-key for nb-edge",
        "bootstrap complete"
    ]
}

TASK [Account domain (journal this)] ***************************************************************************************************************************************
ok: [nb-edge] => {
    "msg": {
        "accounts": 1,
        "domain": "netbird.selfhosted",
        "domain_category": "private",
        "ok": true,
        "primary": true
    }
}

TASK [Show image digests] **************************************************************************************************************************************************
ok: [nb-edge] => {
    "digests.stdout_lines": [
        "netbirdio/netbird-server@sha256:05b3d8d6d056e5062a2965d4d6e5d6d83f09f2bf9133947a8e5972e0e0e7a261",
        "netbirdio/dashboard@sha256:70e0fc6dd3b7758148d182fb55ecd8d4f9ce01e9bba56c9389224e0b8354009d"
    ]
}

TASK [Show the client version] *********************************************************************************************************************************************
ok: [tpi2-4] => {
    "nb_version.stdout": "0.80.0"
}
ok: [nb-edge] => {
    "nb_version.stdout": "0.80.0"
}

TASK [Peers (journal this)] ************************************************************************************************************************************************
ok: [nb-edge] => {
    "msg": [
        ["nb-edge", true, "100.100.210.43", "0.80.0"],
        ["tpi2-4", true, "100.100.51.207", "0.80.0"]
    ]
}

TASK [Show access-model changes and pending roles (journal these)] *********************************************************************************************************
ok: [nb-edge] => {
    "model.stdout_lines": [
        "pending intranet-web (no role group has logged in yet)",
        "pending file-service (no role group has logged in yet)",
        "pending postgres (no role group has logged in yet)",
        "pending legacy-service (no role group has logged in yet)",
        "pending aws-app (no role group has logged in yet)",
        "pending perf-iperf3 (no role group has logged in yet)",
        "missing role groups (log in once as each, then re-run): remote-admin,remote-developer,remote-analyst,remote-contractor",
        "access model complete"
    ]
}

PLAY RECAP *****************************************************************************************************************************************************************
nb-edge                    : ok=46   changed=11   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
tpi2-4                     : ok=13   changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

The image digests are the same as in the first deployment, so the redeploy ran the same server and dashboard. Both routing peers enrolled again and connected, and the owner's account now carries the single-account domain before any role has logged in. The access model is back to all roles pending, as expected after a wipe; the `remote-admin` login is repeated next.

## 2026-10-11 18:30-18:45 | phase-2 | netbird | deployment
First logins for all four roles on home Wi-Fi, then the access model once, so all six policies are written with their final sources in one run and one `policies-export.json`.

Adding the `remote-admin` profile again warned that the name already existed: the profile from before the wipe was still there. Selected the new profile by ID and removed the old one (`netbird profile list --show-id`, `select`, `remove`).

- Defect: `netbird profile add remote-admin` created a second profile with the same name, so `select` by name failed. Cause: the profile from before the wipe was still on the Mac. Fix: selected the new profile by ID and removed the old one.

`remote-admin` logged in through Keycloak and joined the owner's account this time:
```
$ sudo curl -s -H "Authorization: Token $T" $A/users | jq '.[] | {email, role}'
{ "email": "nb-admin@lab.example.com", "role": "owner" }
{ "email": "remote-admin@lab.example.com", "role": "user" }
$ sudo curl -s -H "Authorization: Token $T" $A/groups | jq '.[] | {name, issued}'
{ "name": "All", "issued": "api" }
{ "name": "routers-lab", "issued": "api" }
{ "name": "routers-aws", "issued": "api" }
{ "name": "remote-admin", "issued": "jwt" }
```

The `remote-developer` login registered as `remote-admin`: `mac-remote-developer` had the same `user_id` as `mac-remote-admin` in `/api/peers`, and no new user or group appeared. Keycloak had reused the `remote-admin` session even in a private window, because private windows share one session while any of them is open. Fix: `netbird deregister` in that profile, quit the browser (Cmd-Q), log in again in a new private window, and check that Keycloak asks for the password. Developer, analyst and contractor then each registered as their own user, with a peer `user_id` of their own and a `<role>` group with `issued: "jwt"`. Runbook updated (48f34ad): quit the browser between roles, and check the password prompt and each peer's `user_id`.

- Defect: the `remote-developer` login registered the Mac as `remote-admin`. Cause: private browser windows share one Keycloak session while any of them is open. Fix: `netbird deregister`, quit the browser, log in again; runbook updated (48f34ad).

```
TASK [Show access-model changes and pending roles (journal these)] *********************************************************************************************************
ok: [nb-edge] => {
    "model.stdout_lines": [
        "created policy intranet-web sources remote-admin,remote-developer,remote-analyst,remote-contractor",
        "created policy file-service sources remote-admin,remote-developer,remote-analyst",
        "created policy postgres sources remote-admin,remote-developer,remote-analyst",
        "created policy legacy-service sources remote-admin",
        "created policy aws-app sources remote-admin,remote-developer,remote-analyst",
        "created policy perf-iperf3 sources remote-admin",
        "access model complete"
    ]
}
```
The policy sources match the dial table, and no role is missing. Policy set exported to `ansible-netbird/policies-export.json`.

## 2026-10-11 18:45-19:00 | phase-2 | netbird | testing
`test-matrix` runs on the hotspot, one role at a time: `netbird profile select <role> && netbird up`, pre-checks, matrix, `netbird down`. Every profile routed 10.0.0.73 through `utun100`.

| role | result | CSV results file |
|---|---|---|
| remote-admin | 8/8 | phase-2-netbird_remote-admin_20261012T014834Z_cdb09e563521.csv |
| remote-developer | 8/8 | phase-2-netbird_remote-developer_20261012T014957Z_026eabe71dec.csv |
| remote-analyst | 7/8 | phase-2-netbird_remote-analyst_20261012T015111Z_8c98eef2fe6a.csv |
| remote-analyst (re-run) | 8/8 | phase-2-netbird_remote-analyst_20261012T015458Z_0e4310cd6803.csv |
| remote-contractor | 8/8 | phase-2-netbird_remote-contractor_20261012T015643Z_82671de0f93e.csv |

The analyst failure was `postgres read`, expected allow, observed deny (timeout). It does not look like a policy decision: `postgres write` in the same run, a second later, reached the database and was refused by its grants (`permission denied for table probe_writes`), and the probes to 8080 and 445 just before it connected quickly. Checked by hand straight after, same profile:
```
$ nc -vz -G 5 10.0.0.73 5432
Connection to 10.0.0.73 port 5432 [tcp/postgresql] succeeded!
$ time psql -w -h 10.0.0.73 -U remote-analyst -d labdb -tAc 'SELECT 1'
real	0m0.449s
$ time psql -w -h 10.0.0.73 -U remote-analyst -d labdb -tAc 'SELECT 1'
real	0m0.454s
$ time PGGSSENCMODE=disable psql -w -h 10.0.0.73 -U remote-analyst -d labdb -tAc 'SELECT 1'
real	0m0.428s
```
Connections were consistently fast, and disabling GSSAPI changed nothing, so it was not client-side Kerberos or DNS. The re-run passed 8/8. The first `psql` connection of a run was slow in two of the four first-pass runs:

- Defect: the analyst's `postgres read` timed out (matrix FAIL) although the network allowed it. Cause: not determined; the first `psql` connection of a run was intermittently slow (6.6 s, and over the 10 s limit), while manual checks were consistently fast. Fix: none; the re-run passed, and both CSVs are kept.

| run | postgres read | postgres write |
|---|---|---|
| remote-admin | 476 ms | 492 ms |
| remote-developer | 6,664 ms (pass) | 428 ms |
| remote-analyst | 10,014 ms (timeout) | 589 ms |
| remote-analyst re-run | 459 ms | 432 ms |

Phase 1 and OpenZiti `postgres read` were 449–1,080 ms for every role. Both analyst CSVs are kept in `results/`: the failure happened under the final configuration, so it is an observation, not a setup error.

Some observations:
* `netbird status -d` right after `netbird up` showed `Connection type: -` and no relay address for every peer, so the connection type (P2P or relayed) was not captured by the pre-checks. The status was read before any traffic; it has to be read after traffic (after the matrix or perf run).
* The contractor's status listed only `tpi2-4`, not `nb-edge`. No contractor policy targets `aws-app`, so the AWS routing peer is not in the contractor's network map at all, and `aws-app` is a timeout deny. The other three roles list both routing peers.
* NetBird adds `netbird.selfhosted` as a search domain to the Mac's resolver while up (routing peers run with `--disable-dns`; the Mac does not).
* The S3 denies come from IAM, as in the other phases; S3 is reached over the internet, not the mesh.

Aggregate results (excluding `results/excluded/`):
| phase | role | pass | fail | error | rate |
|---|---|---|---|---|---|
| phase-1 | remote-admin | 8 | 0 | 0 | 100.0% |
| phase-1 | remote-analyst | 8 | 0 | 0 | 100.0% |
| phase-1 | remote-contractor | 8 | 0 | 0 | 100.0% |
| phase-1 | remote-developer | 8 | 0 | 0 | 100.0% |
| phase-2-netbird | remote-admin | 8 | 0 | 0 | 100.0% |
| phase-2-netbird | remote-analyst | 15 | 1 | 0 | 93.8% |
| phase-2-netbird | remote-contractor | 8 | 0 | 0 | 100.0% |
| phase-2-netbird | remote-developer | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-admin | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-analyst | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-contractor | 8 | 0 | 0 | 100.0% |
| phase-2-openziti | remote-developer | 8 | 0 | 0 | 100.0% |

## 2026-10-11 19:00-19:15 | phase-2 | netbird | testing
`remote-admin` run of `perf-battery`, profile `remote-admin`, on the hotspot.

The first lab run left out `--iperf-server`, so it has HTTP latency only and no throughput rows; it is excluded (`perf-battery/results/excluded/phase-2-netbird_netbird_20261012T020151Z_9ee1d019e8ff.csv`) and the lab path was re-run with both tests.

- Defect: the first lab perf run had no throughput results. Cause: `run_perf.py` was run without `--iperf-server`. Fix: re-ran the lab path with both tests; the first CSV is excluded.

Ping test and CSV file name for lab performance testing
```
$ ping -c 30 1.1.1.1 | tail -1
round-trip min/avg/max/stddev = 30.111/45.109/91.343/19.436 ms

phase-2-netbird_netbird_20261012T020714Z_f541779e0281.csv
```

CSV file name for AWS performance testing
```
phase-2-netbird_netbird-aws_20261012T020241Z_0165085a3a62.csv
```

Mean (standard deviation) over 5 reps, against the earlier paths:

| path | throughput up (Mbps) | throughput down (Mbps) | HTTP p50 (ms) | HTTP max (ms) |
|---|---|---|---|---|
| vpn | 6.6 (3.7) | 26.0 (7.2) | 344.6 (442.3) | 1130.6 (1077.5) |
| openziti | 2.2 (0.0) | 27.3 (6.9) | 260.2 (1.3) | 678.4 (464.7) |
| netbird | 6.9 (2.9) | 30.5 (2.3) | 138.1 (6.1) | 203.4 (19.2) |
| vpn-aws | | | 255.5 (30.6) | 803.6 (381.9) |
| openziti-aws | | | 258.7 (3.7) | 347.6 (63.3) |
| netbird-aws | | | 125.5 (1.6) | 191.7 (29.7) |

Some observations:
* On-prem latency is about half of OpenZiti's (p50 133–145 ms against 258–262 ms) and close to the VPN's good reps (128–176 ms), without the VPN's 1.1 s outliers. The worst sample in any NetBird rep was 225 ms.
* The AWS path is about half of both the VPN and OpenZiti (p50 124–127 ms against 216–285 and 256–265 ms), and the steadiest of all paths.
* Upload is not capped as it was on OpenZiti (about 2.2 Mbps in every rep): NetBird's 3.0–10.4 Mbps is in the VPN's range, with the spread that suggests hotspot variation rather than a fixed bottleneck. Download is the highest and steadiest of the three.
* The connection type (P2P or relayed) was not recorded for these runs. The latencies are consistent with a direct WireGuard path from the Mac to each routing peer (to tpi2-4 at home and to the edge host in AWS), but that is not verified.

