# Phase 1 Baseline: OpenVPN via Ansible

Deploys the perimeter-based remote-access baseline on `tpi2-4` of the
Turing Pi 2 cluster using the community role
[`kyl191.openvpn`](https://galaxy.ansible.com/kyl191/openvpn) (MIT,
CI-tested on Ubuntu 22.04/24.04/26.04; architecture-agnostic, works on
ARM64 since it installs the distro `openvpn` package).

## Files

- `requirements.yaml` — pinned role + collections
- `inventory.yaml` — Turing Pi 2 node inventory (`vpn` group = tpi2-4)
- `openvpn.yaml` — playbook with lab-specific configuration

## Usage

```bash
ansible-galaxy install -r requirements.yaml
ansible-playbook -i inventory.yaml openvpn.yaml
```

Generated client profiles land in `~/ovpn-client-configs/<client>/`.
Distribute them to the emulated remote-worker machines.

## Before first run

1. Set `openvpn_server_hostname` to the address remote clients will dial
   (your router's public IP or DDNS name) and port-forward UDP 1194 to tpi2-4.
2. Adjust `lab_onprem_network` and `aws_vpc_network` to your addressing plan.
3. Confirm UFW is the active firewall on tpi2-4 (`sudo ufw status`);
   otherwise set `openvpn_firewall` accordingly.

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
