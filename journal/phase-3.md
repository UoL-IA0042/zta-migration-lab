## 2026-10-11 19:15-19:30 | phase-3 | analysis | planning
Decided the scope of Phase 3 after both Phase 2 experiments were tagged (`phase-2-openziti`, `phase-2-netbird`). The methodology planned Phase 3 as migration planning (translation plus a wave plan) and Phase 4 as its execution, twice, in waves with the VPN in parallel. Each Phase 2 experiment had already carried out the migration as a single cut-over, so three options were weighed: follow the design as written (another Phase 2's worth of lab time, twice), a lighter Phase 4 in waves, or reframe the chapters to what was done.

Decisions, under time constraints:
1. Phase 3 is a desk analysis of the rule-to-policy translation from committed artifacts only; no lab work, and no Phase 4.
2. The K3s/Calico east-west experiment is dropped; `ansible-k3s/` and `calico-policies/` stay in the repo, marked not deployed.
3. Not done, to be stated as limitations: wave-by-wave migration, parallel running of the VPN and the ZTNA implementation, resilience tests of the IdP and control plane, and the external port scan.
4. No CI pipelines and no issue tracker: the journal is the record of defects.

## 2026-10-11 19:30-19:50 | phase-3 | analysis | coding
Wrote the Phase 3 method (`docs/phase-3-translation.md`) and the analysis (`analysis/translation.py`, tests in `analysis/tests/`), committed in 27950de with its outputs in `analysis/results/`. The script normalises the Phase 1 perimeter ruleset, the OpenZiti dial table and the deployed NetBird policies (`policies-export.json`) into network entitlements per role and destination, classifies each change from Phase 1, and joins the test matrix for effective access and the enforcement layer of each deny.

All seven consistency checks pass, among them: declared Phase 1 ruleset = live ruleset recorded in the Phase 1 journal; OpenZiti dial table = NetBird service table = deployed NetBird policies; each product's objects = the objects its bootstrap created (journal). The failure-injection tests confirm each check can fail.

Summary of the results (`analysis/results/translation-summary.md`), identical for both products:
* Of 28 role x destination cells: 15 kept (allow), 4 kept (deny), 4 narrowed (developer and analyst lose `legacy-service` and the perf target `perf-iperf3`), 1 enforcement moved (contractor -> postgres: refused by the database in Phase 1, by the network now), 4 dropped (lab DNS, not published through the overlay).
* Breadth: staff from 65,792 addresses on any port to 2 addresses and 4-6 address:ports; contractor from 2 addresses and 3 address:ports to 1 and 1.
* Expected denies by layer (network / database / IAM): Phase 1 3 / 3 / 4; both products 7 / 1 / 4.
* Size: Phase 1 6 routed rules; OpenZiti 40 objects; NetBird 19 (4 of them groups created by JWT group sync at login).

## 2026-10-11 19:50-20:40 | phase-3 | dissertation | documentation
Revised the Methodology and Experimental Design chapters to the Phase 3 decision (v2 -> v3): three phases; Phase 2 renamed "Zero-trust deployments and migration" and described as executed; Phase 3 as the translation analysis; Phase 4 removed; Calico, CI pipelines and the issue tracker removed; the node roles, cloud component and remote-worker client corrected to what was deployed (control planes on the AWS edge host, IAM users per role, a single client on a mobile connection); new Limitations text for the narrowed scope. In Table 2 the Exposure and Resilience rows are kept and marked not performed; the Resilience Procedures section was removed.

Recording defects in the journal: added the `Defect:` line convention (`journal/README.md`), and `parse_journal.py` now counts them per entry and lists them with `--defects` (6942035). Added `Defect:` lines for the defects found in both Phase 2 experiments (68b7229): 13 in total.

- Defect: the Methodology's Phase 2 paragraph still contained a half-applied earlier edit (FerrumGate and Calico left in the sentence naming the implementations). Cause: an edit from the October chapter review applied only in part. Fix: paragraph replaced in v3.

## 2026-10-11 20:40-20:55 | phase-3 | scripts | debugging
Reviewed the repository before the Results chapter.

- Defect: `scripts/anonymize_export.sh` copied the working tree, so gitignored files (`.vault-pass`, `terraform.tfstate`, `.gitconfig`, `.venv`) would have shipped in the anonymous review export. Cause: rsync of the working tree instead of the committed files. Fix: the export is built from `git archive HEAD` and refuses to run with uncommitted changes (9749a34).
- Defect: the export blocklist matched the local username in pasted paths and prompts (Phase 0 and 1 journals). Cause: unredacted pasted output. Fix: replaced with a new `<user>` label (9749a34).
- Defect: AWS account IDs appear in IAM ARNs in the matrix CSVs (S3 AccessDenied messages). Cause: probe output recorded verbatim. Fix: redacted to `<account-id>` in the export copy only, with a check that none remain; the committed data keeps them (9749a34).
- Defect: the export script read its blocklist with `mapfile`, which macOS bash 3.2 lacks. Cause: bash 4 builtin. Fix: `while read` loop (9749a34).
- Defect: `code_metrics.sh` could not be run in the review environment. Cause: `cloc` not installable there (no access to GitHub or the package registries). Fix: workaround, run on the Mac.

Updated `README.md` (Phase 3, phase tags, K3s and Calico marked not deployed) and the K3s and Calico READMEs (892d3c0).
