# OpenZiti (Phase 2: application-embedded ZTNA)

Controller (quickstart mode) on tpi2-2, dedicated edge router on tpi2-4,
and a declarative bootstrap of the entire access model: Keycloak as an
external JWT signer, one Ziti identity per experimental role, one
service per protected resource, and bind/dial policies expressing least
privilege. The bootstrap script is the rule-to-policy translation
artifact for this implementation — its diff against the Phase 1
firewall ruleset feeds RQ2 directly.

## Phase 2 layout (docs/phase-2-openziti.md)

Public components run on the AWS edge host (`terraform-aws`,
`enable_openziti=true`); the lab only dials out. Inventory groups:
`edge_host` (address from `LAB_EDGE_IP`), `lab_gateway` (tpi2-4, lab end
of the site-to-site tunnel). The controller/router plays below are being
reworked onto the edge host (implementation step 4).

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

## Deploy

```bash
# vault ziti_admin_password first
ansible-playbook -i inventory.yaml site.yaml
```

Router enrollment runbook (after the controller play, before the router
play completes):

```bash
# on tpi2-2, inside the controller container:
ziti edge create edge-router tpi2-4-router --role-attributes router \
  --tunneler-enabled -o /ziti-home/tpi2-4-router.jwt
# copy tpi2-4-router.jwt to tpi2-4:/opt/openziti/enrollment.jwt, then re-run
# the router play (or docker compose restart on tpi2-4)
```

Client side: emulated remote workers run `ziti-edge-tunnel` (ARM64 and
x86 builds available), authenticating via the Keycloak PKCE flow.
Verify the IdP integration end-to-end with:

```bash
ziti ops verify ext-jwt-signer oidc
```

## Access model (mirrors phase-2 test matrix)

| Service | admin | developer | analyst | contractor |
|---|---|---|---|---|
| intranet-web | dial | dial | dial | dial |
| file-service | dial | dial | dial | — |
| postgres | dial | dial | dial | — |
| legacy-service | dial | — | — | — |
| aws-app | dial | dial | dial | — |

Note the contrast with Phase 1: contractor loses all network
reachability except the intranet; legacy-service collapses to
admin-only via the overlay (segment-and-proxy realized).

## VERIFY at deployment time (journal these)

- Image tag against https://github.com/openziti/ziti/releases
- `ziti edge quickstart` flag names for the pinned version
- ext-jwt-signer flags (`--claims-property`, audience) against
  https://openziti.io/docs/guides/external-auth/ — issuer must match
  Keycloak's discovery document exactly, trailing slash included
- AWS router: add an EC2 instance to `ziti_routers` for cloud-side
  hosting of aws-app rather than hairpinning through tpi2-4
