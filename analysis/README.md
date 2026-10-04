# Analysis Tooling

Turns the raw data (journal, test-matrix CSVs, perf CSVs, git history)
into the Results chapter's numbers. All scripts operate on committed
data only, so the analysis is reproducible from the archived repo.

| Script | Input | Output | Research question |
|---|---|---|---|
| `parse_journal.py` | `journal/*.md` | `journal.csv` + category summary | RQ3, RQ4 (time allocation, time sinks) |
| `code_metrics.sh` | phase tags | `code_metrics.csv` | RQ4, RQ5 (complexity proxy) |
| `test-matrix/aggregate.py` | matrix results | pass/fail summary | policy correctness per phase |

```bash
./parse_journal.py ../journal/ -o journal.csv
./code_metrics.sh                 # from repo root, after tagging phases
```

`parse_journal.py` exits nonzero on malformed headers or unknown
categories — run it in CI (or a pre-commit hook) so journal-format
drift is caught the day it happens, not at analysis time.

Defect data comes from the issue tracker export (GitHub Issues API);
join to journal entries on the `#NN` references in `issue_refs`.
