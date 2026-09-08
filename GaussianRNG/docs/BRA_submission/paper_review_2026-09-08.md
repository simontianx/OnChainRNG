# Paper Review: Technical and Statistical Pass

Reviewed on 2026-09-08. Manuscript: `BRA_submission.tex`.

Starting point: the 2026-04-24 editorial review had been applied (items 1–9, 11).
This pass went one layer down: every in-text number was checked against the
generated tables and CSVs (all were accurate), and the statistical argument,
the theorem, the implementation, and venue readiness were examined.

All items below were applied in the same session; the "Applied" notes say how.

## Blockers

### 1. The theorem did not justify the normalization actually used
The theorem proves `(S_n − μ_n)/σ_n → N(0,1)` under `ε ≤ p_i ≤ 1−ε`, but the
sampler uses `(S_n − n/2)/(√n/2)`. The hypothesis is compatible with the
practical estimator diverging: `p_i ≡ 0.51` satisfies it, yet the practical
normalization has mean `0.02√n → ∞`. The binding condition is on the *sum*
of biases, `B_n = Σe_i = o(√n)`; the scale condition `Q_n/n → 0` is second
order and effectively automatic.

Applied: Corollary 1 with proof (Slutsky), plus a paragraph showing that at
n=256 the scale factor is ≥ 0.9992 by algebra alone while the centering shift
could be up to 0.64σ, so the empirical question is entirely about `B_n`.
Tables now report `(μ̂−128)/8` directly (worst 0.021σ).

### 2. The σ̂ evidence was algebraically forced
`σ̂ = √Σp̂(1−p̂)` was 7.9996 in all six families to four decimals. Given
`max|e_i| ≈ 0.019`, the deviation is bounded by ~0.006 for any dataset, and
σ̂ assumes the independence it might be hoped to test.

Applied: replaced with the variance ratio `s_S²/σ̂²` (observed 0.988–1.017,
SE ≈ 0.014, all within 1.2 SE of 1). This is a dependence test at the level of
the statistic the sampler consumes. `generate_study_artifacts.py` now emits
`sd_popcount`, `variance_ratio`, `centering_shift_z`.

### 3. KS numbers understated the result ~5×
KS between the exact Binomial(256, ½) and N(128, 8²), same two-sided
convention, is 0.0249. Observed 0.028–0.036 was almost entirely lattice
effect. Same for W1 (≈0.25 from unit rounding).

Applied: script now computes KS and W1 against the exact binomial
(0.004–0.012 and 0.05–0.19). Distribution table has both references; text
states the 0.0249 floor and notes no family rejects the exact binomial at 5%.

### 4. No cost measurement; reference implementation contradicted the claim
Paper claimed "fixed execution shape"; `contracts/GaussianRNG.sol` used the
Kernighan loop (one iteration per set bit, data-dependent, leaks output via
gas).

Applied: Foundry benchmark in `GaussianRNG/benchmarks` (2,000 chained
digests, gasleft deltas): keccak 268, Kernighan 7,761 (6,074–9,374), SWAR 233
constant, scaling 29. ~530 gas per draw with SWAR. Gas table added to the
paper; `_countOnes` in the contract replaced with the SWAR reduction
(verified against the loop on 300 chained digests plus edge cases).

## Significant

### 5. Sui rows mislabeled in abstract, and wasted
They are MT19937 uniform bytes. The body disclosed this; the abstract did not.
Reframed as the iid fair-bit null control run through the identical pipeline,
which calibrates every "max" statistic. Keccak/SHA fall inside the control's
range on every axis. Labels changed in `generate_cross_vm_artifacts.py` and
the R figure script; figures regenerated.

### 6. One bit crossed the Bonferroni band; text was silent
Experiment 1.1, z = 3.84 vs threshold 3.73. One exceedance in 1,536 tests is
what chance predicts. Sentence added.

### 7. Missing related work
Added: Box–Muller 1958, Marsaglia–Tsang 2000, Devroye 1986, Knuth–Yao 1976,
Dwarakanath–Galbraith 2014, Karney 2016, Micciancio–Walter 2017 (discrete
Gaussian sampling for lattice crypto — the directly adjacent literature),
L'Ecuyer–Simard 2007 (TestU01). New paragraph positions the method against
constant-time discrete Gaussian samplers.

### 8. n = 512 formula not implementable on-chain
`1000/(8√2)` is irrational. Added `Z_{512,10^6} = 88388(S−256)` (relative
error 4e−6, no division) and the 10³-scale variant with its error bound.

### 9. "Three decimal digits of precision" was misleading
Integer scale 1000 ≠ resolution; resolution is 0.125σ, support ±16σ,
resolution scales as `2/√n`. Fixed in the paper and in `GaussianRNG/README.md`.

### 10. Promised-but-unreported diagnostics
Runs-test z and tail error at z=2 were computed but absent from the sequence
table. Columns added. SHA-256 bit ACF (0.052, the largest dependence statistic
in the study) is now discussed explicitly. BLAKE3 flagged as listed but not
evaluated.

### 11. Rogers–Tanimoto and Sokal–Michener are the same statistic
Both are monotone in the match count; text now says so and points to φ as the
informative one.

## Venue readiness
Added keywords, highlights (≤85 chars), data/code availability, declaration of
competing interest, funding, CRediT. Date updated. Kept `article` class since
the target venue is not final (see `us_journal_options.md`); `elsarticle` is
installed locally if BRA is chosen.

Items the author must confirm personally: the competing-interest and funding
statements use standard wording and were not verified.

## Not done / follow-ups
- Tail estimates beyond z=2 remain noisy at n=10,000; the paper now says so.
  Rerunning with 10^6 draws for the tail panels would remove the caveat.
- BLAKE3 is still untested.
- `hardhat` test in `GaussianRNG/test/test.js` was not rerun (no node_modules);
  the contract was verified with Foundry instead.
