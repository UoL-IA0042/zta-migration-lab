# Phase 1 Baseline: OpenVPN via Ansible

Deploys the perimeter-based remote-access baseline on `tpi2-4` of the
Turing Pi 2 cluster using the community role
[`kyl191.openvpn`](https://galaxy.ansible.com/kyl191/openvpn) (MIT,
CI-tested on Ubuntu 22.04/24.04/26.04; architecture-agnostic, works on
ARM64 since it installs the distro `openvpn` package).

## Files

- `requirements.yaml` — pinned role + collections
- `inventory.yaml` — Turing Pi 2 node inventory (`vpn` group = tpi2-4)
  plus the AWS VPN gateway (`aws_vpn_gateway`, address from
  `AWS_VPN_GATEWAY_IP`)
- `openvpn.yaml` — three plays: site-to-site hub on AWS, remote-access
  server on tpi2-4, site-to-site client on tpi2-4

## Usage

```bash
ansible-galaxy install -r requirements.yaml
export AWS_VPN_GATEWAY_IP=$(terraform -chdir=../terraform-aws output -raw vpn_gateway_public_ip)
LAB_VPN_ENDPOINT=<lab public IP or DDNS name> \
  ansible-playbook -i inventory.yaml openvpn.yaml
```

Apply `terraform-aws` first (with `lab_egress_cidr` set): the hub
instance, its Elastic IP, security group and the VPC routes come from
there.

The public endpoint comes from the environment so no public address is
committed (journal rule: no non-lab IPs).

Generated client profiles land in `~/ovpn-client-configs/<client>/`.
Distribute them to the emulated remote-worker machines.

## Before first run

1. tpi2-4 must hold its ISP-gateway lease (10.0.0.251, pinned MAC) and
   the gateway must forward 1194/udp to it. See `docs/addressing.md`
   ("Edge node") and the post-reset checks in `node-reset/README.md`.
2. Adjust `lab_onprem_network` and `aws_vpc_network` to your addressing plan.
3. UFW is the firewall on tpi2-4 (`openvpn_firewall: ufw`); it does not
   need to be enabled beforehand, the role enables it.
4. Test from a remote worker **off** the lab LAN (e.g. a phone hotspot).
   A machine on the LAN reaches 10.0.0.73 directly, bypassing the VPN,
   so its deny results are meaningless; hairpin NAT through the ISP
   gateway is also unreliable.

## Site-to-site to AWS

```
remote worker --1194/udp--> [ISP gw fwd] --> tpi2-4 tun0 (remote access)
                                              |  perimeter ruleset, SNAT to 10.0.0.251
                                              +--> 10.0.0.0/24 (on-prem)
                                              +--> s2s0 --1194/udp out--> AWS hub --> 10.100.0.0/16
```

The hub on the AWS VPN gateway is an OpenVPN server whose only client
is tpi2-4. tpi2-4 dials out to the hub's Elastic IP, so this leg needs
no inbound port on the ISP gateway. The hub owns the LAN route
(`route` + ccd `iroute 10.0.0.0/24`) and pushes `10.100.0.0/16` to
tpi2-4; the tunnel is `openvpn-client@aws-s2s` on interface `s2s0`
(fixed name, so the remote-access server keeps `tun0`). Remote-worker
traffic reaches AWS SNATed to 10.0.0.251, which the VPC routes back
through the hub. The final play waits for the route and checks that
`aws-app` answers through the tunnel.

Transit subnet: `10.9.1.0/24`. Hub ingress (1194/udp, 22/tcp) is
limited to `lab_egress_cidr` in terraform-aws.

## Perimeter ruleset (Phase 1 access control)

Each client gets a fixed tunnel address inside its group's range
(`openvpn_client_configs`, enforced by `ccd-exclusive`), and
`perimeter_ruleset` in `openvpn.yaml` allows routed traffic per group;
everything else from the tunnel is dropped.

| Group | Range | Allowed |
|---|---|---|
| staff (admin, developer, analyst) | `10.9.0.16/28` | all of `10.0.0.0/24` and `10.100.0.0/16` |
| contractor | `10.9.0.32/28` | intranet-web, postgres (database refuses the login), lab DNS |

This is the legacy ruleset the Phase 3 rule-to-policy translation takes
as input; the play prints the live `ufw status verbose` for the
journal. The role resets ufw to incoming ALLOW / forward ACCEPT on every
run, so the play's post_tasks re-apply default-deny for both (SSH and
monitoring are allowed from the lab LAN only).

## Notes for the dissertation

- Client identities (`remote-admin`, `remote-developer`, `remote-analyst`,
  `remote-contractor`) mirror the roles used in the ZTNA phases so that
  access-matrix results are comparable across architectures.
- `openvpn_sync_certs: true` + `openvpn_use_crl: true` make the client list
  declarative: removing a name from `openvpn_clients` revokes its cert on
  the next run. This is the perimeter-era analogue of policy-as-code and
  worth noting in the rule-to-policy translation analysis.
- Pin any role upgrade in `requirements.yaml` and re-tag the repo so each
  experimental phase remains reproducible from its git tag.
