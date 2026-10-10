# Lab Addressing Plan (single source of truth)

Facts that multiple components must agree on. Components duplicate these
values deliberately in their own vars files (self-containment); when a
value changes here, update every location listed and note it in the
journal.

## On-premises (Turing Pi 2, lab LAN 10.0.0.0/24)

| Node | Address | Role |
|---|---|---|
| tpi2-1 | 10.0.0.71 | management, observability (Loki :3100), DNS |
| tpi2-2 | 10.0.0.72 | identity (Keycloak :8080), ZT control planes |
| tpi2-3 | 10.0.0.73 | protected workloads |
| tpi2-4 | 10.0.0.251 | access gateways (OpenVPN :1194/udp); edge node, see below |

- MetalLB pool: `192.168.1.200–192.168.1.220` (outside DHCP scope)
- OpenVPN remote-access client subnet: `10.9.0.0/24`, fixed per-client
  addresses (ccd `ifconfig-push`, `ccd-exclusive`):

  | Client | Address | Group range (perimeter ruleset) |
  |---|---|---|
  | remote-admin | 10.9.0.17 | staff `10.9.0.16/28` |
  | remote-developer | 10.9.0.18 | staff `10.9.0.16/28` |
  | remote-analyst | 10.9.0.19 | staff `10.9.0.16/28` |
  | remote-contractor | 10.9.0.33 | contractor `10.9.0.32/28` |

- OpenVPN site-to-site transit (tpi2-4 <-> AWS hub): `10.9.1.0/24`

### Edge node (ISP gateway constraints)

The LAN is one subnet with two DHCP servers: the ISP gateway
(10.0.0.1) leases a narrow range, dnsmasq leases the rest. The ISP
gateway only port-forwards to devices it has leased an address to and
lists in its device app, so any node that must accept inbound traffic
from the internet is an *edge node*:

- Takes its lease from the ISP gateway, reserved in the gateway app.
- dnsmasq ignores it (`dhcp-host=<mac>,ignore`) so only the ISP
  gateway answers its DHCP requests.
- Uses `dhcp-identifier: mac` and a pinned, globally administered MAC
  (`macaddress:` in netplan); the gateway app did not list the node
  under its generated (locally administered) MAC.
- Golden image seeded with `MACADDRESS=<mac> prepare-golden-image.sh
  <img> <host> dhcp` (node-reset).

| Node | Pinned MAC | Reserved address | Forwarded ports |
|---|---|---|---|
| tpi2-4 | `00:52:83:67:c2:f5` | 10.0.0.251 | 1194/udp (OpenVPN remote access) |

Phase 2 edge nodes (OpenZiti controller/router, NetBird management,
Keycloak for remote SSO) need the same treatment and their own
forwards; add them here when moved.

## AWS

- VPC CIDR: `10.100.0.0/16`
- VPN gateway (site-to-site hub): Elastic IP, not committed —
  `terraform output -raw vpn_gateway_public_ip`, exported as
  `AWS_VPN_GATEWAY_IP` for ansible-openvpn. Ingress (1194/udp, 22/tcp)
  limited to `lab_egress_cidr`.
- Workload app (aws-app): `10.100.10.10:8080`
- S3 data bucket: `lab-data-bucket-<suffix>` (random suffix per environment;
  `terraform output -raw data_bucket`, exported as `LAB_DATA_BUCKET` for the matrix)

## Identities

Roles (identical across OpenVPN clients, Keycloak realm roles, and
test-matrix expectations): `remote-admin`, `remote-developer`,
`remote-analyst`, `remote-contractor`.

## Consumers of these values

- `ansible-openvpn/openvpn.yaml`, `inventory.yaml` (lab/AWS subnets, DNS, client
  addresses, transit subnet, tpi2-4)
- `ansible-k3s/inventory.yaml`, `group_vars/all.yaml` (node IPs, MetalLB pool)
- `ansible-keycloak/group_vars/all.yaml` (tpi2-2, roles, OIDC clients)
- `ansible-observability/group_vars/all.yaml` (all node IPs, Loki push URL)
- `ansible-workloads/group_vars/all.yaml` (tpi2-3, role DB users)
- `ansible-openziti/group_vars/all.yaml` (tpi2-2/tpi2-4, issuer, services)
- `ansible-netbird/group_vars/all.yaml` (tpi2-2, issuer)
- `terraform-aws/variables.tf` (VPC CIDR, app IP, bucket, roles, lab egress)
- `node-reset/inventory.yaml`, `prepare-golden-image.sh` args (node IPs, edge MAC)
- `test-matrix/matrix.yaml` (resource endpoints, roles)
- `perf-battery/` (target addresses, via CLI args)
