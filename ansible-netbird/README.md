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

Next step; see the design's implementation order.
