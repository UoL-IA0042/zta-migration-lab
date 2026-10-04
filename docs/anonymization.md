# Anonymization Procedure

The dissertation is anonymized during submission to minimize grading
bias. Because this repository is cited by and accompanies the
dissertation, review-facing copies of it must be anonymous too. The
repository therefore lives in two forms:

1. **Review export** (anonymous): a snapshot produced by
   `scripts/anonymize_export.sh`, shared with reviewers via an
   anonymizing host (e.g. anonymous.4open.science) or as an archive
   through the submission system. No git history, no CITATION.cff, no
   personal identifiers.
2. **Archived release** (attributed): after review concludes, the named
   repository is published on GitHub and deposited to Zenodo with full
   CITATION.cff attribution and the DOI cited in the final dissertation.

## Deanonymization vectors this repo carries

- **Git history**: every commit embeds `user.name` and `user.email`.
  The export script strips `.git` entirely; never share a clone with
  reviewers. (History is preserved in the attributed release, where it
  serves the methodology's timestamp cross-validation.)
- **CITATION.cff**: names, email, ORCID. Excluded from the export.
- **LICENSE**: copyright holder reads "The Author(s)" with an
  explanatory note; restored to full attribution post-review only if
  your institution requires it (many leave "The Author(s)" permanently).
- **Journal entries**: write them as if a reviewer will read them — no
  names, employers, or personal locations. They are data and DO ship in
  the review export.
- **Incidental identifiers**: hostnames, home-network details, cloud
  account IDs, bucket names containing usernames. The export script
  greps for a configurable blocklist and refuses to export on a match.

## In-text citation during review

Cite the artifact anonymously in the submitted dissertation, e.g.
"(Anonymous, 2026; repository provided as supplementary material)" or
the anonymized hosting URL, and replace with the Zenodo DOI citation in
the final version. Keep a `sed`-able placeholder (ANON-CITATION) in the
manuscript source so the swap is mechanical.

## Checklist before producing the review export

1. Run `scripts/anonymize_export.sh` and fix anything it flags.
2. Search the dissertation PDF for name, email, ORCID, and repo URL.
3. Verify AWS outputs/screenshots in the dissertation don't show the
   account ID or IAM user ARNs (they contain the account number).
4. Confirm journal entries pass the identifier rules above.
