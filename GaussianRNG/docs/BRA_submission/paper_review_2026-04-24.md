# Paper Review: Publishability and Storytelling

Reviewed on 2026-04-24.

Manuscript: `BRA_submission.tex`

PDF status: `latexmk -g -pdf -interaction=nonstopmode -halt-on-error BRA_submission.tex` succeeds and produces a 21-page PDF.

## Bottom Line

The paper is close to a submit-ready technical draft, but it is not yet in publishable prose condition. The main technical story is coherent: define a popcount/Hamming-weight Gaussianization layer, justify it with a Poisson-binomial/Lyapunov-CLT model, and support the fixed-width implementation with empirical diagnostics.

The biggest blockers are editorial rather than computational:
- Section 5 still reads like a proposed future study even though the paper later reports cross-VM results.
- Several enumerated lists are still acting as draft scaffolding.
- The paper promises execution-cost measurements but does not report them.
- The contribution paragraph and numerical-study design need more narrative glue so the paper reads like a complete journal article rather than an expanded technical note.

## Must Fix Before Submission

### 1. Section 5 mixes future-tense planning with completed results

Location: `BRA_submission.tex`, lines 405-446.

The section begins:

`The current numerical results in this paper are specific to \texttt{keccak256}. For a cross-VM version of the paper, the study should be expanded...`

But immediately afterward, the manuscript reports cross-VM figures and tables. This makes the paper look unfinished.

Recommended fix:
- Rewrite Section 5 as a completed empirical expansion.
- Replace `should be expanded`, `cleanest study matrix`, and `should rerun` language with past/present-tense prose.
- State clearly that the expanded study evaluates Keccak-256, SHA-256, and Sui-reference outputs.

Suggested direction:

```tex
The expanded study evaluates the construction at the level of VM-exposed
primitives rather than chain labels alone. This choice separates the statistical
behavior of the digest or randomness interface from ecosystem-specific naming.
The study covers Keccak-256 and SHA-256 as hash primitives shared across EVM
and Solana environments, and it includes 256-bit and 512-bit Sui-reference
uniform outputs as direct Gaussianization targets for \texttt{RandomGenerator}.
```

### 2. Execution-cost measurements are promised but not delivered

Location: `BRA_submission.tex`, line 438.

The checklist includes:

`execution-cost measurements in the native VM.`

But the paper does not report gas, compute-unit, runtime, or implementation-cost results. This is risky because reviewers will treat the method's low-cost claim as central to the paper.

Recommended fix:
- Either remove this bullet entirely from the diagnostic list, or add a concrete implementation-cost subsection.
- If no gas/compute benchmark is available yet, remove the promise and keep the claim qualitative.
- If cost results are available, add a small table comparing the popcount transform against Box-Muller/rejection-style alternatives or at least report hash plus bit-count operation counts.

### 3. The contribution list is too compressed for journal storytelling

Location: `BRA_submission.tex`, lines 87-98.

The contribution list is technically accurate but still reads like outline notes. It also has a punctuation inconsistency: item 3 ends with a period before item 4.

Recommended fix:
- Convert the contribution list into a short paragraph followed by a tighter list, or keep the list but expand each item into a full sentence with explicit significance.
- Make contribution 4 less wordy and more concrete.

Suggested direction:

```tex
The paper makes four contributions. First, it formalizes a VM-native
Gaussianization transform that requires only an $n$-bit output, a population
count, and integer scaling. Second, it gives a probabilistic justification under
a heterogeneous Bernoulli model, where the Hamming weight follows a
Poisson-binomial law and Lyapunov's theorem supplies the asymptotic normal
limit. Third, it evaluates the finite-width behavior of the transform through
bit-bias, dependence, normality, tail, and repeated-output diagnostics. Fourth,
it shows how the same construction transfers across EVM, Solana, and Sui-style
randomness interfaces.
```

### 4. The numerical-study design lists need narrative expansion

Location: `BRA_submission.tex`, lines 378-403.

The current text is mostly two enumerated lists. The content is useful, but the section does not yet tell the reader why these families were chosen or how each diagnostic supports the central claim.

Recommended fix:
- Add one paragraph before the input-family list explaining the design logic.
- Convert the diagnostics list into prose that ties each diagnostic to a failure mode.
- Keep the input family list only if compactness is needed.

Suggested direction:

```tex
The one-shot experiments are designed to stress different ways in which
structure might survive the VM primitive. Sequential integers test ordered
numeric inputs, shifted integers test high-bit changes, transaction-style
strings test realistic formatted messages, and random ASCII strings test
unstructured variable-length inputs. Together these families probe whether the
popcount transform is sensitive to simple input regularities rather than only
to idealized random seeds.
```

### 5. The paper should name Hamming weight explicitly

Location: introduction and generator construction.

The paper uses `popcount`, which is practical and developer-friendly, but the formal information-theory and coding-theory name is `Hamming weight`. Adding this phrase helps reviewers connect the method to known mathematical language.

Recommended fix:
- Define `popcount`, or `Hamming weight`, once near the beginning.
- Use both terms strategically: `population count, or Hamming weight`.

Suggested direction:

```tex
The statistic used by the transform is the population count, equivalently the
Hamming weight, of the VM-native bit string.
```

## Should Fix Before Submission

### 6. Related work is short for a journal submission

Location: `BRA_submission.tex`, lines 100-134.

The section is serviceable, but it covers only three clusters: blockchain randomness, Poisson-binomial theory, and statistical testing. For DLT, Ledger, or IEEE venues, reviewers may expect clearer positioning against:
- Gaussian or non-uniform sampling methods.
- Deterministic smart-contract implementation constraints.
- Lightweight randomness transforms or distribution shaping.
- Standard RNG testing batteries and why this paper uses targeted diagnostics instead.

Recommended fix:
- Add one paragraph on why standard Gaussian samplers are awkward on-chain.
- Add one paragraph explaining why this paper is not another entropy-source paper.
- Add one paragraph explaining why targeted diagnostics are enough for the paper's limited claim but not a cryptographic certification.

### 7. The Sui-reference framing needs extra caution

Location: `BRA_submission.tex`, lines 164-170 and 414-418.

The paper describes Sui native-randomness reference models. If these outputs are idealized rather than actually generated through Sui's production `RandomGenerator`, the text must say so very plainly.

Recommended fix:
- Use `Sui-style reference` or `Sui native-randomness reference model` consistently.
- Avoid implying a direct empirical test of production Sui randomness unless that was actually done.

### 8. The limitations are accurate but visually over-fragmented

Location: `BRA_submission.tex`, lines 720-750.

Five separate `remark` blocks are mathematically clean but read choppy at the end of a journal article.

Recommended fix:
- Convert this section into two or three paragraphs.
- Keep the same content, but make the narrative smoother: model limitation, finite-width limitation, and cryptographic/security limitation.

### 9. The conclusion should echo the cross-VM result earlier and more concretely

Location: `BRA_submission.tex`, lines 752-777.

The conclusion is solid, but the strongest applied result is buried at the end. It should explicitly restate that the method is a distribution-shaping layer and that the cross-VM study supports portability across the tested primitives.

Recommended fix:
- Add one sentence before the final paragraph summarizing the cross-VM evidence.
- Avoid phrasing that sounds too defensive; keep the limitations, but end with the actual contribution.

## Optional Improvements

### 10. Add a compact algorithm box

The paper would benefit from a short algorithm environment or displayed pseudocode:
- Input: seed or VM-native randomness value.
- Compute hash/randomness output.
- Compute Hamming weight.
- Standardize with fixed constants.
- Return integer-scaled output.

This would make the construction easier to cite and implement.

### 11. Add a one-sentence entropy interpretation

The paper could mention that Hamming-weight agreement is an entropy-related diagnostic of marginal bit balance, not a complete entropy or independence proof. This connects naturally to the limitation section without overselling the result.

Suggested direction:

```tex
Viewed through an information-theoretic lens, the Hamming-weight distribution
checks whether the output has the composition expected from fair bits; it does
not by itself certify the full entropy or independence structure of the bit
string.
```

### 12. Consider renaming Section 3

Current title: `Cross-VM Applicability`.

Possible stronger title:
- `Target VM Model`
- `VM Scope and Entropy Sources`
- `Applicability Across Smart-Contract VMs`

The current title is acceptable, but a revised title could make it clearer that this section defines scope rather than reports results.

## Bullet Lists To Expand Or Reduce

The following lists are the ones most likely to make the paper feel underdeveloped:

1. Contribution list: lines 87-98.
2. Concrete 256/512-bit examples: lines 213-231.
3. One-shot input families: lines 380-388.
4. Diagnostic checklist: lines 390-397.
5. Cross-VM study matrix: lines 412-419.
6. Cross-VM diagnostic checklist: lines 429-439.
7. Limitation remarks: lines 722-750.

Recommended treatment:
- Keep the 256/512-bit examples as an enumerated list because they are formula-heavy.
- Convert the contribution list to prose.
- Keep the input-family list but add a motivation paragraph.
- Convert both diagnostic checklists to prose.
- Convert the limitation remarks to paragraphs.

## Publishability Verdict

The manuscript is technically coherent and compiles cleanly. It is under publishable conditions in the sense that the core argument exists, the figures/tables are wired in, and the statistical story is defensible.

It is not yet submission-polished. The main work left is to remove draft-plan language, expand the scaffold bullets into narrative prose, and either substantiate or remove the execution-cost claim. After those edits, the paper should read much more like a complete journal submission.
