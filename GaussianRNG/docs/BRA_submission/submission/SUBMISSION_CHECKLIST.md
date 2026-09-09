# BRA submission checklist

Target: *Blockchain: Research and Applications* (KeAi / Zhejiang University
Press / Elsevier). ISSN 2096-7209 (print), 2666-9536 (online).
Article type: **full-length research paper**.

## Before you start

- [ ] Confirm the current submission portal from the journal's own "Submit your
      article" button. Search results disagree on whether it is Elsevier
      Editorial Manager or the Academax system that Zhejiang University Press
      now uses. Do not guess a URL.
- [ ] Confirm the APC. The listed charge is USD 1,600, but the journal states
      it is sponsored by Zhejiang University Press for accepted papers.
      Verify on the journal's open-access page before submitting.
- [ ] Confirm the two declarations in the manuscript back matter are accurate:
      no competing interests, no external funding.

## Files to upload

| File | Source | Status |
|---|---|---|
| Manuscript PDF | `BRA_submission.pdf` | ready, 27 pp |
| Highlights | `submission/highlights.txt` | ready, 5 items, all <= 85 chars |
| Cover letter | `submission/cover_letter.md` | ready, fill in `[DATE]` |
| Declaration of interest | in manuscript back matter | ready |

BRA accepts a **single PDF for the refereeing stage**. Source files in
`elsarticle` format are only required at revision, so no template conversion is
needed now.

## Manuscript conformance (already done)

- [x] Numbered sections, abstract unnumbered
- [x] Abstract 248 words
- [x] Keywords (9)
- [x] Highlights, 5 items, each <= 85 characters
- [x] Data and code availability statement
- [x] Declaration of competing interest
- [x] Funding statement
- [x] CRediT authorship statement
- [x] Corresponding author with email on the title page
- [x] All figures cited in text; all tables generated from committed data
- [x] References via BibTeX, 22 entries, no undefined citations

## Suggested reviewers

BRA may ask for 3-5 names. Candidates whose work the paper engages with
directly (verify current affiliations and emails yourself, and avoid anyone
with a conflict):

- An author of the NativeVRF paper (Werapun et al., *Systems* 2023) for
  EVM-side randomness.
- A. K. Goharshady (probabilistic smart contracts, ICBC 2019).
- Someone from the discrete-Gaussian-sampling side, e.g. an author on
  Micciancio-Walter (CRYPTO 2017), for the sampler-design comparison.

## At revision stage only

- [ ] Convert to `elsarticle` (installed locally at
      `/usr/local/texlive/2025/texmf-dist/tex/latex/elsarticle/`)
- [ ] Split figures into separate files at required resolution
- [ ] Supply source `.tex`, `.bib`, and figure files

## Known open items

- BLAKE3 is named in Table 1 as a Solana primitive but is not evaluated. The
  text flags this. A reviewer may ask; adding it is about an hour.
- Tail evidence stops at z = 4 (76 expected draws at 10^6). Stated in the
  limitations.
