# ZTA Migration Lab

Experimental infrastructure for dissertation research on migrating from
perimeter-based VPN remote access to zero-trust architecture in a hybrid
(on-premises + AWS) environment. The on-premises platform is a Turing
Pi 2 cluster (4x RK1: 8-core RK3588, 32 GB RAM, 4 TB NVMe per node)
running bare-metal Ubuntu ARM64; the cloud platform is AWS.

This repository is both the deployment tooling and part of the research
data: work journals, test results, and the git history itself feed the
dissertation's analysis of migration effort, defects, and complexity.

## Structure

Each component is self-contained and independently deployable (own
inventory, dependencies, README, and run instructions). Reuse happens
through pinned external roles and collections, never through
cross-directory references; facts that must agree across components are
documented in `docs/addressing.md`.

| Directory | Purpose | Phase |
|---|---|---|
| `ansible-observability/` | Prometheus/Grafana/Loki (tpi2-1) + node_exporter, Alloy (all) | 0 |
| `ansible-keycloak/` | Identity provider, realm-as-code (tpi2-2) | 0 |
| `ansible-workloads/` | Protected resources: postgres, web, SMB, legacy (tpi2-3) | 0 |
| `terraform-aws/` | VPC, Graviton workloads, S3, per-role IAM | 0 |
| `ansible-openvpn/` | Perimeter VPN baseline (kyl191.openvpn, pinned) | 1 |
| `ansible-openziti/` | App-embedded ZTNA: controller, router, access model | 2 |
| `ansible-netbird/` | WireGuard-mesh ZTNA: management stack + policies | 2 |
| `ansible-k3s/` | K3s + MetalLB + Longhorn substrate | 2 (not run) |
| `calico-policies/` | East-west zero trust: install + NetworkPolicies | 2 (not run) |
| `test-matrix/` | Access-control test harness + per-phase matrices | all |
| `perf-battery/` | Throughput/latency measurements per access path | all |
| `analysis/` | Journal parser, code metrics, Phase 3 translation analysis | all, 3 |
| `journal/` | Structured work journal (primary time/defect data) | all |
| `docs/` | Conventions, addressing plan, phase designs, anonymization | — |

Deployment order: observability -> keycloak -> workloads -> terraform-aws
-> openvpn (phase 1) -> ZTNA components per phase 2 experiment
(`ansible-openziti`, then `ansible-netbird`, each from the Phase 1
baseline). Phase 3 is an analysis of committed data only
(`docs/phase-3-translation.md`, `analysis/translation.py`); there is no
Phase 4. The K3s/Calico east-west experiment was dropped for time and
its directories were never deployed.
Components marked VERIFY in their READMEs pin fast-moving upstream
details that must be confirmed against current releases at deploy time
and recorded in the journal.

## Conventions

- **Phase tags.** Each experimental phase is a signed tag
  (`phase-0-infrastructure`, `phase-1-baseline`, `phase-2-openziti`,
  `phase-2-netbird`). Every result in the
  dissertation traces to the tag that produced it. Tags are deposited to
  Zenodo via the GitHub integration; cite the version DOI.
- **Reproducibility.** Every experiment starts from a clean state: nodes
  re-flashed via the Turing Pi BMC, environments rebuilt from this repo
  at the relevant tag. No configuration exists outside version control.
- **Secrets.** Vaulted with ansible-vault or supplied via environment;
  never committed in plaintext. `CHANGE-ME-USE-VAULT` marks every value
  requiring replacement.
- **Journal.** Contemporaneous entries in `journal/`, committed with the
  work they describe; format and parsing documented there.
- **Results are data.** Test-matrix CSVs and measurement output are
  committed, keyed by run ID to the producing tag.

## Quick start (per component)

```bash
cd <component>
ansible-galaxy install -r requirements.yaml   # where present
ansible-playbook -i inventory.yaml <playbook>.yaml
```

See each component's README for specifics and pre-run checks.

## Anonymized review

The accompanying dissertation is anonymized during submission. Reviewer
-facing copies of this repository are produced with
`scripts/anonymize_export.sh` (no git history, no CITATION.cff, scanned
against an identifier blocklist); the LICENSE names "The Author(s)"
accordingly. Full attribution and the Zenodo DOI are restored in the
post-review archived release. See `docs/anonymization.md`.

## Citation

See `CITATION.cff` (attributed release only). Archived releases:
Zenodo DOI (added after first deposit).

## License

MIT — see `LICENSE`.
