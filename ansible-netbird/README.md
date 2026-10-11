# NetBird (Phase 2: WireGuard-mesh ZTNA)

Second Phase 2 experiment (docs/phase-2-netbird.md): NetBird's combined
management server and dashboard on the AWS edge host behind Caddy,
Keycloak as the upstream OIDC provider of NetBird's embedded IdP, and
routing peers on tpi2-4 and the edge host. This directory holds the
whole NetBird migration, so per-product code metrics count all of it.

| Term | Meaning here |
|---|---|
| Combined server | `netbird-server`: management, signal, relay, STUN and the embedded IdP (Dex) in one container |
| Embedded IdP | NetBird's login service; Keycloak is configured as its external OIDC connector |
| Routing peer | NetBird peer that forwards to non-mesh addresses (tpi2-4: 10.0.0.73, edge host: 10.100.10.10) |
| JWT group sync | Users join NetBird groups from the `groups` claim (Keycloak realm roles) |

Inventory groups: `edge_host` (address from `LAB_EDGE_IP`), `lab_gateway`
(tpi2-4, lab end of the site-to-site tunnel).

| Name | Where | Serves |
|---|---|---|
| `idp.<edge-ip-dashed>.sslip.io:443` | edge host, Caddy | Keycloak through the tunnel |
| `netbird.<edge-ip-dashed>.sslip.io:443` | edge host, Caddy | NetBird gRPC (h2c), relay, signal and management websockets, API, embedded IdP (`127.0.0.1:8081`); dashboard (`127.0.0.1:8080`) |
| `<edge ip>:3478/udp` | edge host | STUN (combined server) |

## Step 3: public IdP path (`idp-path.yaml`)

Prerequisites: `terraform-aws` with `enable_netbird=true`, and Keycloak
redeployed with the public issuer (ansible-keycloak README, Phase 2).

```bash
export LAB_EDGE_IP=$(terraform -chdir=../terraform-aws output -raw edge_host_public_ip)
ansible-playbook -i inventory.yaml idp-path.yaml
```

- tpi2-4: routed rule `s2s0` edge subnet -> `10.0.0.72:8080` and a
  MASQUERADE block, so tpi2-2's replies return through tpi2-4.
- Edge host: Caddy with both sites and automatic Let's Encrypt
  certificates (no ACME e-mail). The NetBird site answers 502 until the
  server starts in step 4.
- Control machine: the discovery document's issuer equals
  `keycloak_issuer`, and the NetBird name has a valid certificate.

Adapted from `ansible-openziti/idp-path.yaml`; the Caddy routes follow
NetBird's external-Caddy layout (`getting-started.sh`, v0.80.0).

## Step 4: server, bootstrap, routing peers (`site.yaml`)

Prerequisites: step 3 verified, the OpenVPN site-to-site tunnel up, and
this role's vault (once). The Keycloak client secret is not repeated
here: the plays load `ansible-keycloak/group_vars/all/vault.yaml`
(`vault_netbird_secret`).

```bash
openssl rand -base64 24    # paste as the value below
ansible-vault create --vault-password-file ../.vault-pass group_vars/all/vault.yaml
#   vault_netbird_owner_password: "<the generated value>"
```

Run:

```bash
export LAB_EDGE_IP=$(terraform -chdir=../terraform-aws output -raw edge_host_public_ip)
ansible-playbook -i inventory.yaml --vault-password-file ../.vault-pass site.yaml
```

1. Edge host: `netbird-server` 0.80.0 (host networking, loopback
   `127.0.0.1:8081`, STUN 3478/udp) and `dashboard` v2.94.0
   (`127.0.0.1:8080`) behind Caddy. Server-local secrets (relay secret,
   datastore and cookie keys) are generated on first run in
   `/opt/netbird/secrets.json` and never leave the host.
2. Bootstrap (`files/netbird-admin.py bootstrap`, management API on
   loopback):
   - first admin `nb-admin@lab.example.com` through `POST /api/setup`;
     the returned API token (365 days) is kept root-only in
     `/opt/netbird/admin.token`
   - Keycloak as the embedded IdP's OIDC connector (`keycloak`)
   - account settings: JWT group sync from the `groups` claim, group
     propagation to peers, no manual user approval
   - the account's `Default` policy (every peer to every peer) is deleted
   - networks `lab` (resource 10.0.0.73/32, routing peer group
     `routers-lab`) and `aws` (10.100.10.10/32, `routers-aws`), masquerade
   - one-off setup keys (1 hour) for routing peers not yet enrolled
3. Routing peers (tpi2-4, edge host): NetBird client from
   pkgs.netbird.io pinned to the server version, enrolled with its setup
   key, `--disable-dns --disable-client-routes` so the gateways keep their
   own resolver and routes. On tpi2-4 the client inserts its own accept
   rules for `wt0` at the top of the kernel FORWARD chain, ahead of ufw's
   default-deny routed policy; NetBird's policies, not ufw, decide what
   mesh traffic reaches the LAN.
4. Check: both routing peers connected in the management API; setup
   keys deleted. Then the access model (below) runs once.

The playbook prints the bootstrap changes, image digests and client
version; journal them. Re-runs converge. After a routing peer's node was
reset its identity is gone: `-e netbird_reenroll=tpi2-4` (comma-separated,
no spaces) deletes the stale peer and enrolls it again.

## Access model (`access-model.yaml`)

One policy per service: TCP port, source the role groups, destination the
network resource (`netbird_services`, same table as phase-2-openziti).
The role groups are created by NetBird's JWT group sync at each role's
first login, and the sync only uses groups it created, so the bootstrap
cannot create them in advance (and no group named after a role may be
created by hand). Run after each role's first login, before that role's
matrix run:

```bash
ansible-playbook -i inventory.yaml access-model.yaml
```

It reports roles still missing, and exports the policy set to
`policies-export.json`: commit it, it is this product's rule-to-policy
artifact (RQ2). That the access model needs a login first is itself a
migration finding.

Dashboard: `https://netbird.<edge-ip-dashed>.sslip.io`, admin login
`nb-admin@lab.example.com` with the vaulted password.

## VERIFY at deployment time (journal these)

- Image digests and the client package version (`netbird=0.80.0` must
  exist in pkgs.netbird.io; adjust `netbird_version` if the package uses
  another version string)
- Routing peers connected; connection type per peer (`netbird status -d`)
- tpi2-4: ufw rules unchanged, `wt0` accept rules present
  (`sudo iptables -S FORWARD | head`)
