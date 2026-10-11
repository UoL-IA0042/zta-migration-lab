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
