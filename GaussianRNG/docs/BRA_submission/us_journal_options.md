# US Journal Options Beyond BRA

Checked on 2026-04-15.

Paper in scope: `A Lightweight Gaussian Sampler for Smart-Contract Virtual Machines`.

Short read:
- Best topical fit: `ACM Distributed Ledger Technologies: Research and Practice (DLT)`.
- Best blockchain-native backup: `Ledger`.
- Fastest likely decision: `IEEE Open Journal of the Computer Society` or `IEEE Access`.
- Hard no: do not submit to two journals at the same time.

## Recommendation

### Fit-first submission order
1. `ACM Distributed Ledger Technologies: Research and Practice (DLT)`
2. `Ledger`
3. `IEEE Open Journal of the Computer Society`
4. `IEEE Access`
5. `IEEE Transactions on Emerging Topics in Computing` only if the paper is reframed more strongly as an emerging-computing systems paper

### Speed-first submission order
1. `IEEE Open Journal of the Computer Society`
2. `IEEE Access`
3. `ACM Distributed Ledger Technologies: Research and Practice (DLT)`
4. `Ledger`
5. `IEEE Transactions on Emerging Topics in Computing`

## Ranked Notes

### 1. ACM Distributed Ledger Technologies: Research and Practice (DLT)
- Publisher: ACM
- Why it fits: DLT explicitly covers blockchain, cryptocurrency, smart contracts, cryptographic primitives, blockchain engineering, and empirical evaluation. That is the cleanest match to this paper's current framing.
- Fit: `Very high`
- Difficulty: `Medium`
- Likely review speed: `Medium / unknown`
- Notes: This is the best venue if you want the paper judged as a blockchain/smart-contract methods paper rather than forced into a broader computing frame.
- Practical downside: I did not find an official current review-time claim, so speed is harder to predict.
- Official sources:
  - https://www.acm.org/media-center/2021/september/dlt-cfp
  - https://www.acm.org/media-center/2022/october/dlt-inaugural-issue
  - https://dl.acm.org/journal/dlt

### 2. Ledger
- Publisher: University of Pittsburgh
- Why it fits: Ledger is a blockchain- and cryptocurrency-dedicated journal and accepts original research spanning computer science, engineering, and cryptographic methods.
- Fit: `High`
- Difficulty: `Medium`
- Likely review speed: `Medium`
- Notes: Good niche fallback if DLT rejects. It is more specialized and more comfortable with blockchain-specific engineering papers than a general CS journal.
- Practical downside: The review model is unusually transparent, and the journal states that peer-review transcripts for accepted papers are published. That is not bad, but you should want that.
- Official speed signal: Ledger says it targets a `twelve-week` turnaround for first-round reviews.
- Official sources:
  - https://ledgerjournal.org/ojs/ledger/about
  - https://ledgerjournal.org/ojs/index.php/ledger/about

### 3. IEEE Open Journal of the Computer Society
- Publisher: IEEE Computer Society
- Why it fits: Broad enough to take a smart-contract VM paper if it is presented as a computing-methods contribution with clear technical evaluation.
- Fit: `Medium`
- Difficulty: `Medium`
- Likely review speed: `Fast`
- Notes: This is the best fast-decision venue if you want a reputable US society journal and can pitch the work as a lightweight deterministic computing method for blockchain VMs.
- Practical downside: It is not blockchain-specific, so the introduction and contribution framing would need to lean harder on computing systems and deterministic implementation constraints.
- Official speed signal: IEEE says OJ-CS offers rapid publication with a `five-week` review cycle.
- Official sources:
  - https://www.computer.org/digital-library/journals/oj/cfp-open-journal

### 4. IEEE Access
- Publisher: IEEE
- Why it fits: Broad engineering scope, open to multidisciplinary and applications-oriented papers that do not fit neatly into narrower IEEE journals.
- Fit: `Medium`
- Difficulty: `Medium`
- Likely review speed: `Fast`
- Notes: This is the practical fallback if you want quick handling and broad visibility more than a blockchain-native audience.
- Practical downside: It is broad, so the paper can feel less targeted there than in DLT or Ledger.
- Official speed signal: IEEE Access advertises `4 to 6 weeks` from submission to publication and lists a `27%` average acceptance rate.
- Official sources:
  - https://ieeeaccess.ieee.org/about/

### 5. IEEE Transactions on Emerging Topics in Computing
- Publisher: IEEE Computer Society
- Why it fits: Only conditionally suitable. TETC wants emerging research with clear evaluation and state-of-the-art comparison, and it has run blockchain-focused special sections before.
- Fit: `Medium-low`
- Difficulty: `High`
- Likely review speed: `Slow to medium`
- Notes: I would not use this as the first backup in the paper's current form. It becomes more plausible if the paper is reframed toward emerging computing methodology, evaluation rigor, and broader systems relevance beyond blockchain.
- Practical downside: Higher risk of an administrative or editorial desk rejection if the manuscript still reads mainly as a blockchain application paper.
- Official sources:
  - https://www.computer.org/digital-library/journals/ec/technical-tracks
  - https://www.computer.org/digital-library/journals/ec/call-for-papers-ieee-transactions-on-emerging-topics-in-computing-special-section-on-scalable-computing-for-blockchain-systems

## How I would actually sequence submissions

If the goal is the strongest topical home:
1. Submit to `DLT`.
2. If rejected, revise lightly and submit to `Ledger`.
3. If rejected again, broaden the framing and submit to `OJ-CS`.
4. Use `IEEE Access` as the final fast, broad fallback.

If the goal is the fastest credible decision:
1. Submit to `OJ-CS`.
2. If rejected, go to `IEEE Access`.
3. Then try `DLT` only if you want the more domain-specific venue and are willing to wait longer.

I would personally choose the first path unless speed is the dominant concern.

## Submission constraints

- Sequential submission is fine.
- Simultaneous submission is not.
- If the paper is still under review at BRA, wait for rejection or formally withdraw before sending it elsewhere.

## Important inference note

The `fit` ratings are my judgment from the manuscript abstract and the journals' official scope pages.

The `difficulty` and some of the `likely review speed` labels are partly inferential because not every journal publishes a current official review-time statistic. Where an official speed claim exists, I used it directly. Where it does not, I marked the speed more cautiously.

## Source notes

- ACM Open / ACM journal publishing model as of 2026-01-01:
  - https://authors.acm.org/open-access
  - https://authors.acm.org/journals/submission-process
- ACM DLT scope:
  - https://www.acm.org/media-center/2021/september/dlt-cfp
  - https://www.acm.org/media-center/2022/october/dlt-inaugural-issue
- Ledger scope and turnaround:
  - https://ledgerjournal.org/ojs/ledger/about
- IEEE Open Journal of the Computer Society scope and speed:
  - https://www.computer.org/digital-library/journals/oj/cfp-open-journal
- IEEE Access scope and speed:
  - https://ieeeaccess.ieee.org/about/
- IEEE TETC technical-track expectations:
  - https://www.computer.org/digital-library/journals/ec/technical-tracks
