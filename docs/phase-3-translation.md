# Phase 3: rule-to-policy translation (desk analysis)

Status: method for Phase 3, decided 2026-10-11 under time constraints.
Phase 3 is an analysis of committed artifacts only; it needs no lab.
The two migrations it analyses were executed in Phase 2
(`phase-2-openziti`, `phase-2-netbird`), each from the Phase 1 baseline.

## Terms

| Term | Meaning here |
|---|---|
| Perimeter ruleset | Phase 1's access control: ufw routed-traffic rules on the VPN concentrator (tpi2-4), matching a VPN group's tunnel address range to a destination network, host or port (`ansible-openvpn/openvpn.yaml`, `perimeter_ruleset`) |
| Access model | A ZTNA product's equivalent: OpenZiti services with bind/dial policies; NetBird policies from role groups to network resources |
| Translation artifact | The code that produces an access model from the intended access (`ansible-openziti/templates/bootstrap-ziti.sh.j2` with its service table; `ansible-netbird/files/netbird-admin.py` with its service table and the deployed `policies-export.json`) |
| Destination | A host and port a remote worker may need: the six Phase 2 services, plus the lab DNS server that only Phase 1 grants |
| Entitlement | A role's network-layer permission for one destination (allow or deny), with the rule or policy that grants it |
| Effective access | What a role can actually do: the network entitlement combined with the workload's own controls (database grants, S3 IAM). The access test matrix measures it |
| Enforcement layer | Which control produced a deny: network (connection dropped), database (Postgres refused) or IAM (AWS refused), inferred from the probe detail |
| Breadth | How much a role can reach at the network layer: addresses and ports |

## Scope change

The methodology planned Phase 3 as migration planning (translation plus
a wave plan) and Phase 4 as its execution, twice, in waves with the VPN
running in parallel. In the lab each Phase 2 experiment already carried
out the migration, as a single cut-over per product: the access model
was translated, remote access moved to the overlay, and the
remote-access VPN retired. Phase 3 therefore analyses that translation
from the artifacts and the measurements already committed, and there is
no Phase 4. Not done, to be stated as limitations: wave-by-wave
migration, a period of parallel running, resilience tests of the IdP and
the control plane, and the external port scan. The K3s/Calico
east-west experiment was also not run.

## Question

What did translating the perimeter ruleset into each ZTNA access model
involve (RQ2): which entitlements were kept, narrowed, moved to another
enforcement layer or dropped, how many policy objects it took, and how
the reachable breadth changed. Effort and size come from the existing
instruments: journal hours (`parse_journal.py`) and code metrics per
phase tag (`code_metrics.sh`).

## Inputs (all committed)

| Input | Source |
|---|---|
| Perimeter ruleset, declared | `ansible-openvpn/openvpn.yaml`: `perimeter_ruleset`, `vpn_group_ranges`, client addresses (`openvpn_client_configs`) |
| Perimeter ruleset, live | `ufw status verbose` recorded in `journal/phase-1.md` |
| OpenZiti access model | `ansible-openziti/group_vars/all/vars.yaml` (`ziti_services`, `lab_roles`) and the bootstrap template; created objects recorded in `journal/phase-2.md` |
| NetBird access model | `ansible-netbird/policies-export.json` (deployed state), `group_vars/all/vars.yaml` (`netbird_services`, `netbird_networks`) |
| Workload controls | `ansible-workloads/templates/init.sql.j2` (database grants), `terraform-aws` per-role IAM |
| Intended and measured access | `test-matrix/matrix*.yaml` (expectations), `test-matrix/results/*.csv` (observed; `results/excluded/` and `results/phase-1-rebuild/` not used) |

## Method

1. Catalogue the destinations: the six Phase 2 services (same addresses
   and ports in all three phases) and the lab DNS server (53, udp and
   tcp). `perf-iperf3` is the perf battery's target, not a workload; it
   is kept in the catalogue because both access models grant it, and
   marked in the outputs.
2. Normalise each artifact into entitlements per role and destination.
   Phase 1: a role's tunnel address gives its group; a rule matches when
   the destination is inside its address range and the port and protocol
   match (a rule without a port matches every port). OpenZiti: a dial
   policy on the service lists the role. NetBird: a policy whose rule
   targets the destination's resource and port lists the role's group.
3. Classify each change from Phase 1 to each product: kept (allow to
   allow, deny to deny), narrowed (allow to deny at the network),
   enforcement moved (a deny that a workload control made in Phase 1 and
   the network makes now), dropped (a Phase 1 entitlement to a
   destination the access model does not publish at all; here the lab
   DNS server, since the overlay addresses resources by IP).
4. Effective access per phase from the matrix: expected and observed
   decision, and the enforcement layer of each deny.
5. Size: rules or objects in each artifact, objects per access intent,
   and breadth per role (addresses and ports reachable at the network
   layer).
6. Consistency checks: the declared Phase 1 ruleset matches the live
   one; the OpenZiti dial table, the NetBird service table and the
   deployed NetBird policies agree; each product's network entitlements
   agree with its matrix expectations.

## Outputs

`analysis/translation.py` (reproduce: `./translation.py` from
`analysis/`) writes to `analysis/results/`:

- `entitlements.csv`: role x destination x phase, decision and the
  granting rule or policy
- `changes.csv`: the classification per role and destination, per product
- `effective.csv`: matrix expectation, observed results and enforcement
  layer per phase, role, resource and operation
- `translation-summary.md`: the tables above in reading form, the size
  and breadth figures, and the consistency checks

The script exits nonzero if a consistency check fails.
