# Phase 2 design: OpenVPN remote access -> NetBird

Status: design, for review before implementation. Second Phase 2
experiment, after `phase-2-openziti`; decisions recorded in
journal/phase-2.md (planning, 2026-10-11).

## Terms

| Term | Meaning here |
|---|---|
| Management server | NetBird control plane (`netbird-server`): peers, groups, policies, networks; also runs signal, relay and STUN in the combined image (v0.65+) |
| Embedded IdP | NetBird's built-in login service (Dex), always on. Users log in to it; it delegates to Keycloak through an external OIDC connector |
| Peer | A machine running the NetBird client (WireGuard). The Mac per role, tpi2-4, the edge host |
| Routing peer | A peer that forwards traffic from other peers to addresses outside the mesh (here: tpi2-4 for 10.0.0.73, the edge host for 10.100.10.10) |
| Network / resource | NetBird's model for non-peer destinations: a network holds resources (an address) and the routing peers that reach them |
| Policy | Allow rule: source group -> destination (group or resource), protocol and ports. Default deny otherwise |
| JWT group sync | NetBird assigns users to groups from a claim in the login token (`groups`, mapped from Keycloak realm roles) |
| Setup key | One-time key that enrolls a server peer (tpi2-4, edge host) without an interactive login |
| P2P / relayed | A WireGuard connection is direct after NAT traversal (STUN), or carried by the relay over 443 when traversal fails |
| Edge host | The AWS EC2 instance for public components (as in phase-2-openziti), recreated for this experiment |
| sslip.io name | DNS name that resolves to the IP embedded in it, e.g. `netbird.203-0-113-7.sslip.io` |

## Decisions

1. Start from the Phase 1 baseline (step 0), so NetBird's migration
   effort is measured from the same state as OpenZiti's: OpenZiti torn
   down, nodes restored from golden images, OpenVPN redeployed.
2. Public NetBird components run on the AWS edge host, as OpenZiti's
   did; the lab only dials out. Same names scheme (sslip.io on the
   Elastic IP), Caddy terminates TLS (Let's Encrypt).
3. Keycloak stays the only source of identities: NetBird's embedded IdP
   uses it as an external OIDC provider; local NetBird logins are used
   only for the bootstrap admin.
4. Only the remote-access VPN is replaced; the site-to-site tunnel stays.
5. Each experiment's directory is self-contained: `ansible-netbird`
   carries its own IdP-path play (adapted from ansible-openziti), so
   code metrics per product count the full migration.

## Architecture

```
Mac (hotspot)                AWS public subnet                    Lab LAN
NetBird client  --443-->  edge host: Caddy
  SSO (browser)              idp.<eip>.sslip.io  --> hub --s2s0--> tpi2-4 --> Keycloak 10.0.0.72:8080
                             netbird.<eip>.sslip.io --> netbird-server (mgmt, signal, relay)
                                                    \-> dashboard
                --3478/udp-> STUN (netbird-server)
  WireGuard  <== P2P or relayed ==>  routing peer: edge host -> aws-app 10.100.10.10:8080
  WireGuard  <== P2P or relayed ==>  routing peer: tpi2-4     -> 10.0.0.73 services
```

- Data path differs from OpenZiti: WireGuard between the Mac and the
  routing peer, direct if NAT traversal succeeds (hotspot CGNAT and the
  Xfinity NAT make relaying likely), otherwise through the relay on the
  edge host. The connection type is recorded per run (`netbird status -d`).
- Security group (edge host): 80/443 TCP and 3478 UDP from anywhere;
  22 from `lab_egress_cidr`.

## Access model (same as phase-2-openziti)

| Resource | Address | admin | developer | analyst | contractor | Routing peer |
|---|---|---|---|---|---|---|
| intranet-web | 10.0.0.73 tcp/8080 | allow | allow | allow | allow | tpi2-4 |
| file-service | 10.0.0.73 tcp/445 | allow | allow | allow | - | tpi2-4 |
| postgres | 10.0.0.73 tcp/5432 | allow | allow | allow | - | tpi2-4 |
| legacy-service | 10.0.0.73 tcp/8023 | allow | - | - | - | tpi2-4 |
| aws-app | 10.100.10.10 tcp/8080 | allow | allow | allow | - | edge host |
| perf-iperf3 | 10.0.0.73 tcp/5201 | allow | - | - | - | tpi2-4 (perf only) |

One policy per row (source: role groups, destination: resource, TCP
port). The matrix expectations equal `matrix-phase2-openziti.yaml`;
deny mechanisms may differ (WireGuard firewall drops, so expect
timeouts where OpenZiti refused), which is itself a finding. The
exported policy set (`policies-export.json`) is this product's
rule-to-policy artifact (RQ2).

## Keycloak changes (part of the migration effort)

- Public issuer through the edge host, as in phase-2-openziti step 2.
- `netbird` client: confidential, redirect
  `https://netbird.<eip>.sslip.io/oauth2/callback` (embedded IdP
  connector callback), secret from the vault.
- Mapper: realm roles also emitted as `groups` in the ID token (NetBird's
  connector reads `groups`; the existing `roles` claim stays).
- Fix in the realm template for all clients: default scopes include
  `basic` (Keycloak 25+ carries `sub` there) and drop `openid`, which is
  not a client scope. The embedded IdP needs `sub`; this likely also
  explains the account console's "unexpected error".
- Applied by a clean Keycloak redeploy (`keycloak_reset=yes`).

## Implementation order

0. Rebuild the Phase 1 baseline (below). The NetBird migration clock
   starts after step 0.
1. Terraform: `enable_netbird` creates the edge host with the NetBird
   security group (the edge-host resources serve either experiment).
2. ansible-keycloak: public issuer, netbird client, groups mapper, scope
   fix; redeploy.
3. ansible-netbird `idp-path.yaml`: tpi2-4 relay rule and NAT, Caddy
   with the `idp` and `netbird` sites; verify the issuer from the Mac.
4. ansible-netbird `site.yaml`: netbird-server and dashboard on the edge
   host (pinned versions); bootstrap through the management API:
   Keycloak connector, JWT group sync (`groups`), groups, networks,
   resources, routing peers (setup keys), policies; export the policy
   set; enroll tpi2-4 and the edge host as routing peers; check both
   online and the routes present.
5. Decommission remote-access OpenVPN
   (`ansible-openvpn/decommission-remote-access.yaml`, unchanged) and the
   ISP 1194/udp forward.
6. Client: NetBird for macOS, management URL
   `https://netbird.<eip>.sslip.io`, SSO login per role; runbook with
   role switching and pre-run checks.
7. `matrix-phase2-netbird.yaml`, matrix runs, perf (`--phase
   phase-2-netbird --path netbird`, `netbird-aws`), connection type per
   run, tag `phase-2-netbird`.

## Step 0: rebuild the Phase 1 baseline

| Step | Where | Command / action |
|---|---|---|
| 1 | terraform-aws | `terraform apply -var enable_openziti=false` (plus the usual vars): destroys the edge host, EIP, subnet, route table, SG and the hub SG rule |
| 2 | node-reset | `reset.yaml -l tpi2-4`, then `-l tpi2-2`, then `-l tpi2-3` (golden images: phase 0; clears the router, Docker on tpi2-4, the public issuer, and Phase 2 probe writes) |
| 3 | Mac (home) | `curl -s http://10.0.0.72:8080/realms/lab/.well-known/openid-configuration \| jq -r .issuer` prints `http://10.0.0.72:8080/realms/lab` |
| 4 | ansible-openvpn | `openvpn.yaml` as in Phase 1 (hub, remote-access server, site-to-site client); new client profiles land in `~/ovpn-client-configs/` |
| 5 | ISP gateway | re-add the 1194/udp forward to tpi2-4 (manual, journaled) |
| 6 | Mac | Ziti Desktop Edge off (identity removed); import the new OpenVPN profiles |
| 7 | test-matrix | Phase 1 matrix, all four roles, hotspot: `--matrix matrix.yaml --out-dir results/phase-1-rebuild`; expect the Phase 1 results |

Results of step 7 are kept apart from the Phase 1 data: they show the
rebuilt baseline matches, they are not new Phase 1 measurements. Perf is
not repeated; Phase 1's perf runs stay the reference.

## VERIFY at deployment (journal results)

- Image versions: `netbirdio/netbird-server` 0.80.0 and
  `netbirdio/dashboard` v2.94.0 at the time of writing; journal digests.
- Bootstrap admin access to the management API (owner login and a
  personal access token for a service user) without manual dashboard
  steps.
- NetBird client on tpi2-4 alongside ufw (default deny routed): its
  forwarding and masquerade rules must take effect without opening
  other routed traffic.
- Connection type per run (P2P or relayed) for the Mac and each routing
  peer.
- macOS client: SSO with a custom management URL and switching users
  between roles.
