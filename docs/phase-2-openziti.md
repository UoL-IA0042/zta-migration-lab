# Phase 2 design: OpenVPN remote access -> OpenZiti

Status: design, for review before implementation. Decisions recorded in
journal/phase-2.md (planning, 2026-10-11).

## Terms

| Term | Meaning here |
|---|---|
| Controller | OpenZiti control plane: identities, services, policies, enrollment (client API :1280) |
| Edge router | OpenZiti data-plane node. *Public* router accepts client connections (:3022); *private* router only dials out |
| Tunneler | Client that intercepts traffic for authorized services (Ziti Desktop Edge on the Mac; a router in tunneler mode on the hosting side) |
| Intercept / host config | Per service: the address the client intercepts, and the address the hosting router forwards to |
| Bind / Dial policy | Which identities may host (bind) and which may reach (dial) a service: the access model |
| ext-jwt-signer | Controller trust in an external IdP's tokens (Keycloak here); identities log in with OIDC instead of certificates |
| Hub | Phase 1's AWS OpenVPN site-to-site hub (kept) |
| Edge host | New EC2 instance carrying the public Ziti components and the IdP proxy |
| sslip.io name | DNS name that resolves to the IP embedded in it, e.g. `ctrl.203-0-113-7.sslip.io` -> 203.0.113.7; no domain to register, no personal identifier |

## Decisions

1. Public Ziti components run in AWS; the lab only dials out. No inbound
   port at home after the migration (the 1194/udp forward is removed).
2. Public names are sslip.io names on the edge host's Elastic IP; the IdP
   gets a Let's Encrypt certificate.
3. OpenZiti is migrated first (phase-2-openziti), NetBird second.
4. Only the remote-access VPN is replaced. The AWS<->lab site-to-site
   tunnel stays as infrastructure.
5. Login is Keycloak OIDC as the **primary** authenticator
   (`keycloak-only` auth policy). Certificate+OIDC (secondary) is not
   used: it is broken on the macOS tunneler (ziti-sdk-c #919, June 2026);
   primary external auth works on Ziti Desktop Edge for macOS >= 2.51.

## Architecture

```
Mac (hotspot)                AWS public subnet                  Lab LAN
Ziti Desktop Edge  --443-->  edge host: Caddy (idp.<eip>.sslip.io)
  OIDC login (browser)          | reverse proxy over site-to-site
                                +--> hub --s2s0--> tpi2-4 --> Keycloak 10.0.0.72:8080
                   --1280--> controller (ctrl.<eip>.sslip.io)
                   --3022--> public edge router (router.<eip>.sslip.io)
                                |  hosts aws-app (10.100.10.10:8080)
                                +<--link (dialed from lab)-- private router tpi2-4
                                                               hosts 10.0.0.73 services
```

- **Edge host** (`terraform-aws/phase2-openziti.tf`, toggled by
  `enable_openziti` so the phase-1 tag stays reproducible): Graviton
  instance (t4g.small: controller + router + proxy), Elastic IP, public
  subnet. Security group: 80/443, 1280, 3022 from anywhere (remote
  workers have no fixed address: the exposure moves from home to cloud
  and is authenticated-only, which is a migration finding); 22 from
  `lab_egress_cidr`. Route `10.0.0.0/24` via the hub; the hub's security
  group must admit the edge host (forwarded traffic is filtered on the
  hub ENI).
- **Controller** and **public router**: official `openziti/ziti-controller`
  and `openziti/ziti-router` images (pin current 2.x at deploy; journal
  versions). Controller keeps its own PKI; clients trust it through the
  network JWT. Public router runs in host mode and hosts `aws-app`.
- **IdP path**: Caddy terminates TLS for `idp.<eip>.sslip.io` and proxies
  to Keycloak through the site-to-site tunnel. Keycloak is reconfigured
  with `KC_HOSTNAME=https://idp.<eip>.sslip.io` and proxy headers, so the
  issuer is `https://idp.<eip>.sslip.io/realms/lab` everywhere (Mac,
  controller). tpi2-4 gains one routed rule (s2s0 -> 10.0.0.72:8080) and
  SNAT for 10.100.0.0/16 -> LAN, so tpi2-2's replies return via tpi2-4.
- **Private router** on tpi2-4 (host mode, no inbound listener reachable
  from outside): dials the controller and links to the public router;
  hosts the on-prem services.
- **Decommission**: tpi2-4's remote-access OpenVPN server is stopped and
  disabled, and the Xfinity 1194/udp forward deleted (manual step,
  journaled). The site-to-site client stays.

## Access model (identical addresses, least privilege)

Services intercept the **same addresses and ports** as Phase 1, so the
test matrix keeps its resources and only the expectations change; the
diff between `matrix.yaml` and `matrix-phase2-openziti.yaml` is the
access-model change.

| Service | Intercept / host | admin | developer | analyst | contractor | Hosted by |
|---|---|---|---|---|---|---|
| intranet-web | 10.0.0.73:8080 | dial | dial | dial | dial | tpi2-4 router |
| file-service | 10.0.0.73:445 | dial | dial | dial | - | tpi2-4 router |
| postgres | 10.0.0.73:5432 | dial | dial | dial | - | tpi2-4 router |
| legacy-service | 10.0.0.73:8023 | dial | - | - | - | tpi2-4 router |
| aws-app | 10.100.10.10:8080 | dial | dial | dial | - | AWS router |
| perf-iperf3 | 10.0.0.73:5201 | dial | - | - | - | tpi2-4 router (perf only, not in matrix) |

Changes from Phase 1 to expect in the matrix: contractor loses the
network path to postgres (deny by network, previously by DB); developer
and analyst lose legacy-service. DB grants still decide analyst writes.
S3 is unchanged (IAM, outside the overlay).

Identity mapping: one Ziti identity per role, `externalId` = Keycloak
`preferred_username` (= role name), auth policy `keycloak-only`.

## Keycloak changes (part of the migration effort, not phase 0)

- `KC_HOSTNAME` -> public https URL; `KC_PROXY_HEADERS=xforwarded`.
- `openziti` client: public client with PKCE (S256), redirect
  `http://localhost:20314/auth/callback`, audience mapper so access
  tokens carry `aud: openziti`.
- `--import-realm` skips existing realms, so the change is applied by a
  clean Keycloak redeploy on tpi2-2 (golden images stay phase 0).

## Implementation order

1. Terraform: edge host, EIP, SGs, route; hub SG rule.
2. ansible-keycloak: public hostname, openziti client changes; redeploy.
3. tpi2-4: s2s0 -> Keycloak rule + SNAT; verify
   `https://idp.<eip>.sslip.io/realms/lab/.well-known/openid-configuration`
   from the Mac.
4. ansible-openziti (rework): edge-host play (controller, public router,
   Caddy), bootstrap (ext-jwt-signer, auth policy, identities, services,
   policies, router enrollment), tpi2-4 private-router play.
5. Decommission remote-access OpenVPN.
6. Client: Ziti Desktop Edge >= 2.51, add network, log in per role.
7. `matrix-phase2-openziti.yaml`, matrix runs, perf (`--path openziti`,
   `openziti-aws`), tag `phase-2-openziti`.

## VERIFY at deployment (journal results)

- Image tags for controller/router (2.x) and Ziti Desktop Edge version.
- ext-jwt-signer fields: issuer exactly equals token `iss` (no trailing
  slash drift); `external-auth-url` = issuer; audience present in token.
- Router link: private router dials, public router listens (no inbound
  needed on tpi2-4).
- Known client issue: if JWT enrollment fails on macOS 2.51, add the
  network by controller URL instead (OpenZiti forum, Oct 2025).
