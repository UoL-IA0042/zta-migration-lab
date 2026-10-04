# Work Journal

Primary data for the time-allocation and defect analyses. One file per
phase (`phase-0.md`, `phase-1.md`, ...). Entries are contemporaneous and
committed with the work they describe; commit timestamps cross-validate
entry timestamps.

## Entry format (machine-parseable)

```markdown
## 2026-09-12 09:40–11:05 | phase-2 | openziti | debugging
Controller failed to start after re-flash; cgroup v2 flag missing from
vendor kernel. Logged as issue #23.
```

Header fields: `date start–end | phase | component | category`.

Categories (fixed taxonomy — do not invent new ones mid-study):
`planning`, `coding`, `deployment`, `debugging`, `testing`,
`documentation`.

## Rules

- Write the entry when the work happens, not at day's end.
- One entry per contiguous work session per category; switch categories,
  start a new entry.
- Reference issue numbers for any defect or unplanned work.
- No secrets, no real credentials, no non-lab IPs: this ships with the
  public archive.
