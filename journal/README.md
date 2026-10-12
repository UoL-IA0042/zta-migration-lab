# Work Journal

Primary data for the time-allocation and defect analyses; there is no
separate issue tracker. One file per
phase (`phase-0.md`, `phase-1.md`, ...). Entries are contemporaneous and
committed with the work they describe; commit timestamps cross-validate
entry timestamps.

## Entry format (machine-parseable)

```markdown
## 2026-09-12 09:40–11:05 | phase-2 | openziti | debugging
Controller failed to start after re-flash.
Defect: controller container exits at start after re-flash. Cause: cgroup v2 flag missing from the vendor kernel. Fix: kernel parameter added to the node image (a1b2c3d).
```

Header fields: `date start–end | phase | component | category`.

Categories (fixed taxonomy — do not invent new ones mid-study):
`planning`, `coding`, `deployment`, `debugging`, `testing`,
`documentation`.

## Rules

- Write the entry when the work happens, not at day's end.
- One entry per contiguous work session per category; switch categories,
  start a new entry.
- Record every defect, failure and item of unplanned work as one line
  starting `Defect:` (a list item `- Defect:` also counts), in the entry
  where it was found: what failed, its cause, and the fix or workaround
  with the commit when there is one —
  `Defect: <what failed>. Cause: <cause>. Fix: <fix or workaround>.`
  Lines inside fenced code blocks are not counted, so pasted output
  cannot add defects by accident.
- No secrets, no real credentials, no non-lab IPs: this ships with the
  public archive.
- Pasted output is redacted with fixed labels: `<account-id>`,
  `<hub-eip>` (`<hub-eip-dashed>` in EC2 hostnames), `<lab-egress-ip>`,
  `<edge-ip>`, and `<user>` for the local username (shell prompts,
  home-directory paths). For `terraform apply`, record the command (public values as
  variables), the `Plan:` summary line and anything unexpected, not the
  full output.
