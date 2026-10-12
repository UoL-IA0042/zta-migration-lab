# Commit map

The repository history was rewritten on 2026-10-12 to remove personal identifiers (`docs/anonymization.md`); every commit was then re-signed. The rewrite changed every commit hash, so hashes cited before it no longer exist in this repository. This file maps the hashes cited in the journal to the current commits. File contents are unchanged apart from the redactions.

## Terms

| Term | Meaning here |
|---|---|
| Cited hash | A short commit hash written in the journal or docs before the rewrite |
| Unsigned working commit | A commit as first made, before the author re-signed the branch with `git rebase --gpg-sign`; the journal cites these |
| Current commit | The same change in this repository's history |

## Hashes cited in the journal

These hashes are unsigned working commits, cited when the work was journaled; the same change was later re-signed and then rewritten. Matched on the commit subject, which is unique in the history.

| Cited | Where | Current | Subject |
|---|---|---|---|
| `910363b` | `journal/phase-2.md` | `3af5fa7` | Move the Phase 2 Terraform inputs into variables.tf |
| `4a14645` | `journal/phase-2.md` | `0bd510e` | NetBird step 4: match peers on name, not the OS hostname |
| `8b6c990` | `journal/phase-2.md` | `1d546f3` | Step 6 runbook (NetBird): first login with --no-browser in a private window |
| `47c70e9` | `journal/phase-2.md` | `cfda237` | NetBird step 4: give the owner's account the single-account domain |
| `48f34ad` | `journal/phase-2.md` | `6fd8c2e` | Step 6 runbook (NetBird): all four first logins, then the access model once |
| `27950de` | `journal/phase-3.md` | `8826de3` | Phase 3: rule-to-policy translation analysis |
| `6942035` | `journal/phase-3.md` | `e318717` | Record defects in the journal with Defect: lines, not an issue tracker |
| `68b7229` | `journal/phase-3.md` | `843eaf6` | Phase 2 journal: Defect: lines for the defects found during both experiments |
| `9749a34` | `journal/phase-3.md` | `c26809d` | Review export from committed files only; redact account IDs and username |
| `892d3c0` | `journal/phase-3.md` | `041c196` | README: Phase 3 analysis, phase tags, K3s and Calico marked not deployed |
