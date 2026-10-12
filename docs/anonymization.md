# Anonymization Procedure

The author is never identified, in this repository or anywhere it is
published. The repository is permanently pseudonymous: the author,
committer and copyright holder is **UoL IA0042** (GitHub organization
`UoL-IA0042`, a dedicated email address and a signing key used only for
this project). There is no attributed release.

The repository is published in two forms, both pseudonymous:

1. **Archived release**: the public GitHub repository, deposited to
   Zenodo through the GitHub integration with "UoL IA0042" as creator
   (`CITATION.cff`). The version DOI is the citation used in the
   dissertation.
2. **Review export**: a snapshot produced by
   `scripts/anonymize_export.sh`, for reviewers who need an archive
   rather than a link. No git history, no `CITATION.cff`, scanned
   against a local identifier blocklist.

## Deanonymization vectors this repo carries

- **Git history**: every commit embeds `user.name` and `user.email`;
  all are the pseudonym. History is published (it serves the
  methodology's timestamp cross-validation), so it must stay free of
  identifiers too: an identifier found in history is removed with
  `git filter-repo`, not just in the latest commit.
- **Signatures**: commits and tags are signed with an SSH key used only
  for this project; a signature embeds the public key, so the key must
  never be registered on any other account.
- **CITATION.cff**: the pseudonym only; no name, email or ORCID.
- **LICENSE**: the copyright holder is "The Author(s)", permanently.
- **Journal entries**: write them as if a reviewer will read them — no
  names, employers, or personal locations. They are data and DO ship in
  the review export.
- **Incidental identifiers**: hostnames, home-network details, cloud
  account IDs, bucket names containing usernames. The export script
  greps for a blocklist of personal identifiers and refuses to export on
  a match. The blocklist (`scripts/anonymize_blocklist.txt`) is
  gitignored and kept only on the author's machine, since it is itself a
  list of identifiers.
  AWS account IDs inside ARNs (the S3 AccessDenied messages in the
  matrix CSVs) are redacted to `<account-id>` in the committed data and
  in the export.
- **Untracked secrets**: `.vault-pass`, `terraform.tfstate`, `.gitconfig`
  and virtualenvs live in the working tree but are gitignored. The export
  is built from the committed tree at HEAD (`git archive`), so they never
  reach it; the script refuses to run with uncommitted changes.

## Citation in the dissertation

Cite the Zenodo version DOI under the pseudonym, e.g. *UoL IA0042 (2026)
ZTA Migration Lab: experimental infrastructure for VPN to zero-trust
architecture migration research (Version 1.0.0) [Software]. Zenodo.
https://doi.org/10.5281/zenodo.<id>*. The Zenodo profile, like the
GitHub account, carries only the pseudonym.

## Checklist before producing the review export

1. Run `scripts/anonymize_export.sh` and fix anything it flags.
2. Search the dissertation PDF for name, email and ORCID.
3. Verify AWS outputs/screenshots in the dissertation don't show the
   account ID or IAM user ARNs (they contain the account number).
4. Confirm journal entries pass the identifier rules above.
