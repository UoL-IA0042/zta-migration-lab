# Analysis Tooling

Turns the raw data (journal, test-matrix CSVs, perf CSVs, git history)
into the Results chapter's numbers. All scripts operate on committed
data only, so the analysis is reproducible from the archived repo.

| Script | Input | Output | Research question |
|---|---|---|---|
| `parse_journal.py` | `journal/*.md` | `journal.csv` + category summary; `defects.csv` (`--defects`) | RQ3, RQ4 (time allocation, time sinks); RQ1 (pitfalls, from defects) |
| `code_metrics.sh` | phase tags | `code_metrics.csv` | RQ4, RQ5 (complexity proxy) |
| `test-matrix/aggregate.py` | matrix results | pass/fail summary | policy correctness per phase |
| `translation.py` | Phase 1 ruleset, both access models, matrices and results | `results/` (entitlements, changes, effective access, summary) | RQ2 (rule-to-policy translation, Phase 3) |

```bash
./parse_journal.py ../journal/ -o journal.csv --defects defects.csv
./code_metrics.sh                 # from repo root, after tagging phases
./translation.py                  # Phase 3; exits nonzero if a consistency check fails
python3 -m unittest discover -s tests
```

`translation.py` method and terms: `docs/phase-3-translation.md`. Its
outputs in `results/` are committed so the Results chapter's tables can
be traced to a commit; re-running it must leave them unchanged.

`parse_journal.py` exits nonzero on malformed headers or unknown
categories — run it before committing journal changes (or from a
pre-commit hook) so journal-format drift is caught the day it happens,
not at analysis time.

Defect data comes from the journal: every defect, failure and item of
unplanned work is a `Defect:` line in the entry where it was found
(`journal/README.md`). `journal.csv` counts them per entry, so defect
counts join to time and category; `defects.csv` lists each one with its
entry's date, phase, component and category. There is no issue tracker.
