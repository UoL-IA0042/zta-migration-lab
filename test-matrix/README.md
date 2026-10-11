# Access-Control Test Matrix Harness

The correctness instrument for every experimental phase: executes
positive and negative access probes per role and records results as CSV
for the analysis pipeline. Negative cases are the direct measure of
least privilege — every role must carry both `allow` and `deny` rows.

## Files

- `run_matrix.py` — probe runner (Python 3.10+, PyYAML only; `requirements.txt`)
- `matrix.yaml` — Phase 1 (perimeter baseline) access model
- `aggregate.py` — merges result CSVs, per-phase/role summary, nonzero
  exit on any FAIL/ERROR (usable as a migration-wave gate)
- `results/` — CSV output, one file per run (commit these; they are data)

## Execution model

Run once per role, from a machine holding that role's session (VPN
profile in Phase 1, ZTNA enrollment later). This is deliberate: it
exercises the real access path rather than simulating it.

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt   # once
./run_matrix.py --matrix matrix.yaml --role remote-developer            # execute
./run_matrix.py --matrix matrix.yaml --role remote-admin --dry-run      # validate
./aggregate.py results/ --fails                                        # summarize
```

Credentials are supplied ambiently on the probing machine (PGPASSWORD,
AWS profiles named after roles, bearer tokens via `auth_token_env`) —
never in the matrix file, which is committed.

Per-environment values are supplied the same way: `exec` commands may
reference `$VAR` / `${VAR}`, expanded from the environment, and an unset
variable yields ERROR rather than a silent deny. Currently required:
`LAB_DATA_BUCKET` (the S3 bucket name, from `terraform output -raw
data_bucket` in `terraform-aws/`).

## Probe semantics

| Type | allow | deny |
|---|---|---|
| tcp  | connect succeeds | timeout / refused / unreachable |
| http | 2xx/3xx | 401/403, or connection failure |
| exec | exit 0 | nonzero exit whose output matches `deny_pattern`; timeout only if `deny_on_timeout` |

Anything else is ERROR: the probe, not the policy, needs fixing, and the
row is excluded from pass/fail analysis. For `exec` probes this matters
most: a missing client, AWS profile or password also exits nonzero, so
without a deny signature a half-configured probing machine would score
every deny row as a pass. Every `exec` resource sets:

| Setting | Meaning |
|---|---|
| `deny_pattern` | regex a genuine deny's stdout/stderr must match (IAM `AccessDenied`; Postgres `permission denied for ...`) |
| `deny_on_timeout` | whether a timeout is a legitimate deny (true where the network itself may deny, false for S3, which is reached over the internet) |
| `timeout` | per-probe override of `defaults.timeout` (any probe type) |

Settings sit on the resource and can be overridden per operation.

Probing machine prerequisites (otherwise rows are ERROR, not deny):
`psql` on PATH (macOS: `export PATH="$(brew --prefix libpq)/bin:$PATH"`),
`PGPASSWORD` for the role, an AWS profile named after the role, and
`LAB_DATA_BUCKET`. Run `--dry-run` first; the planned deny signature is
printed for each exec probe.

## Per-phase matrices

One matrix file per phase (`matrix.yaml`, `matrix-phase2-openziti.yaml`, ...).
The Phase 1 matrix deliberately encodes the coarse perimeter model,
including over-broad allows; later matrices tighten to least privilege.
The git diff between phase matrices is itself an analysis artifact: it
quantifies the access-model change the migration delivers.

## Result schema

`run_id, timestamp_utc, phase, role, resource, operation, probe_type,
expected, observed, result, latency_ms, detail`

`latency_ms` doubles as a coarse per-operation latency sample across
architectures; the dedicated performance battery provides the precise
measurements.

## Verified

Smoke-tested: all five probe outcome paths (http/tcp/exec × allow/deny),
planted-failure detection, and aggregator gating confirmed working.
