# Lab Addressing Plan (single source of truth)

Facts that multiple components must agree on. Components duplicate these
values deliberately in their own vars files (self-containment); when a
value changes here, update every location listed and note it in the
journal.

## On-premises (Turing Pi 2, lab LAN 10.0.0.0/24)

| Node | Address | Role |
|---|---|---|
| tpi2-1 | 10.0.0.71 | management, observability, DNS |
| tpi2-2 | 10.0.0.72 | identity (Keycloak :8080), ZT control planes |
| tpi2-3 | 10.0.0.73 | protected workloads |
| tpi2-4 | 10.0.0.74 | access gateways (OpenVPN :1194/udp) |

- MetalLB pool: `192.168.1.200–192.168.1.220` (outside DHCP scope)
- OpenVPN client subnet: `10.9.0.0/24`

## AWS

- VPC CIDR: `10.100.0.0/16`
- Workload app (aws-app): `10.100.10.10:8080`
- S3 data bucket: `lab-data-bucket`

## Identities

Roles (identical across OpenVPN clients, Keycloak realm roles, and
test-matrix expectations): `remote-admin`, `remote-developer`,
`remote-analyst`, `remote-contractor`.

## Consumers of these values

- `ansible-openvpn/openvpn.yaml` (lab/AWS subnets, DNS)
- `ansible-k3s/inventory.yaml`, `group_vars/all.yaml` (node IPs, MetalLB pool)
- `ansible-keycloak/group_vars/all.yaml` (tpi2-2, roles, OIDC clients)
- `ansible-observability/group_vars/all.yaml` (all node IPs)
- `ansible-workloads/group_vars/all.yaml` (tpi2-3, role DB users)
- `ansible-openziti/group_vars/all.yaml` (tpi2-2/tpi2-4, issuer, services)
- `ansible-netbird/group_vars/all.yaml` (tpi2-2, issuer)
- `terraform-aws/variables.tf` (VPC CIDR, app IP, bucket, roles)
- `test-matrix/matrix.yaml` (resource endpoints, roles)
- `perf-battery/` (target addresses, via CLI args)
