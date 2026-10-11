# OpenZiti (Phase 2: application-embedded ZTNA)

Controller and public router on the AWS edge host, a private router on
tpi2-4, and a declarative bootstrap of the entire access model: Keycloak
as an external JWT signer, one Ziti identity per experimental role, one
service per protected resource, and bind/dial policies expressing least
privilege. The bootstrap script (`templates/bootstrap-ziti.sh.j2`) is the
rule-to-policy translation artifact for this implementation; its diff
against the Phase 1 firewall ruleset feeds RQ2 directly.

## Phase 2 layout (docs/phase-2-openziti.md)

Public components run on the AWS edge host (`terraform-aws`,
`enable_openziti=true`); the lab only dials out. Inventory groups:
`edge_host` (address from `LAB_EDGE_IP`), `lab_gateway` (tpi2-4, lab end
of the site-to-site tunnel) and `lab_router` (tpi2-4, private router).

| Name | Where | Role |
|---|---|---|
| `ctrl.<edge-ip-dashed>.sslip.io:1280` | edge host | controller: client API, management API, router control |
| `router.<edge-ip-dashed>.sslip.io:3022` | edge host | public router `aws-edge`: client connections and router links; hosts aws-app |
| `idp.<edge-ip-dashed>.sslip.io:443` | edge host | Caddy reverse proxy to Keycloak (step 3) |
| `lab-router` | tpi2-4 | private router (`--private`, no link listener): dials out, hosts the 10.0.0.73 services |

### Step 3: public IdP path (`idp-path.yaml`)

Publishes Keycloak at `https://idp.<edge-ip-dashed>.sslip.io` before any
Ziti component exists: Caddy on the edge host (automatic Let's Encrypt,
no ACME e-mail) proxies through the hub and tunnel to tpi2-4, which
allows the edge subnet to `10.0.0.72:8080` and NATs it onto the LAN so
tpi2-2's replies return the same way.

```bash
export LAB_EDGE_IP=$(terraform -chdir=../terraform-aws output -raw edge_host_public_ip)
ansible-playbook -i inventory.yaml idp-path.yaml
```

The last play fetches the discovery document from the control machine
through the edge host and asserts the issuer equals `keycloak_issuer`.
Prerequisite: Keycloak redeployed with the public issuer
(ansible-keycloak README, "Phase 2: public issuer").

### Step 4: overlay and access model (`site.yaml`)

Prerequisites: step 3 verified (the issuer check passed), and the vault
file with the controller admin password, created once:

```bash
openssl rand -base64 24    # paste as the value below
ansible-vault create --vault-password-file ../.vault-pass group_vars/all/vault.yaml
#   vault_ziti_admin_password: "<the generated value>"
```

Run:

```bash
export LAB_EDGE_IP=$(terraform -chdir=../terraform-aws output -raw edge_host_public_ip)
ansible-playbook -i inventory.yaml --vault-password-file ../.vault-pass site.yaml
```

1. Edge host: controller (first run bootstraps PKI, config and the admin
   user), then the bootstrap script, then the public router enrolled
   with the token the script issued.
2. tpi2-4: Docker with iptables management off (ufw owns the gateway's
   firewall; host networking needs no Docker rules), then the private
   router, enrolled with its token.
3. Check: both routers online, a connected link between them, and a
   terminator for every service. The single-use enrollment tokens are
   then deleted.
4. From the control machine: the controller's client API answers on its
   public name.

The playbook prints the image digests and the access-model changes;
journal both. The bootstrap creates what is missing and updates what
exists to the values in `group_vars`, so re-runs converge. Entities
removed from `group_vars` are not deleted; remove them by hand.

After a tpi2-4 reset the router identity is gone: add
`-e ziti_lab_router_reenroll=true`, which issues a new token and discards
the old router state on tpi2-4 before enrolling.

Ziti admin CLI, on the edge host:

```bash
cd /opt/openziti && sudo docker compose exec ziti-controller bash
ziti edge login https://localhost:1280 -u admin -y   # prompts for the password
```

## Access model (mirrors the phase-2 test matrix)

Services intercept the Phase 1 addresses, so the matrix keeps its
resources.

| Service | Intercept | admin | developer | analyst | contractor | Hosted by |
|---|---|---|---|---|---|---|
| intranet-web | 10.0.0.73:8080 | dial | dial | dial | dial | lab-router |
| file-service | 10.0.0.73:445 | dial | dial | dial | - | lab-router |
| postgres | 10.0.0.73:5432 | dial | dial | dial | - | lab-router |
| legacy-service | 10.0.0.73:8023 | dial | - | - | - | lab-router |
| aws-app | 10.100.10.10:8080 | dial | dial | dial | - | aws-edge |
| perf-iperf3 | 10.0.0.73:5201 | dial | - | - | - | lab-router (perf only, not in the matrix) |

Contrast with Phase 1: contractor loses all network reachability except
the intranet; legacy-service collapses to admin-only via the overlay
(segment-and-proxy realized). Clients may connect only to `aws-edge`
(edge-router policy `clients-public-router`).

Login: primary external JWT only (auth policy `keycloak-only`). The
Keycloak access token carries `aud: openziti` and `preferred_username`,
which matches the identity's external id (= role name).

## VERIFY at deployment time (journal these)

- Image digests printed by the playbook (controller, both routers)
- Overlay state printed by the final check (routers, link, terminators)
- ext-jwt-signer issuer equals the token `iss` exactly (no trailing slash
  drift): `ziti edge list ext-jwt-signers` against the discovery document
