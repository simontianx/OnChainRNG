[DATE]

To the Editors
Blockchain: Research and Applications

Dear Editors,

I am submitting the manuscript "A Lightweight Gaussian Sampler for Smart
Contract Virtual Machines" for consideration as a full-length research paper in
Blockchain: Research and Applications.

Smart-contract virtual machines expose hash primitives and, increasingly,
uniform randomness services, but none of the major ones exposes a Gaussian
sampling primitive. The standard ways to obtain a Gaussian draw all sit badly
in deterministic VM execution: Box-Muller needs transcendental functions,
Ziggurat and other rejection methods need tables and a variable iteration
count, and the constant-time discrete Gaussian samplers developed for
lattice-based cryptography need multi-word arithmetic and many uniform bits per
output. The paper studies the most austere alternative that could work: take
the population count of one VM-native n-bit output, standardize it, and scale
it to an integer.

The contribution is a distribution-shaping layer rather than an entropy source,
and the paper is explicit that the seed must come from a VRF, beacon, or native
randomness service. Within that scope it offers three things. First, a
probabilistic justification via the Poisson-binomial law and Lyapunov's central
limit theorem, together with a corollary that isolates the one genuinely
empirical condition, a bound on the sum of the bit biases, under which the
fixed on-chain normalization inherits the Gaussian limit. Second, an empirical
study in which Keccak-256 and SHA-256 are compared against an iid fair-bit
control run through the identical pipeline, so that every extreme-value
statistic is calibrated rather than merely reported; the hash primitives are
indistinguishable from the control on every diagnostic, and a separate 10^6-draw
study matches the exact binomial law through z = 4. Third, measured EVM gas,
showing that the whole transform costs about 530 gas per draw provided the
population count is implemented with a constant instruction count.

The work fits the journal's scope in smart contracts, blockchain-based
algorithms, and performance optimization, and it is aimed at practitioners as
much as at theorists: the paper includes an algorithm box, an exact integer
formula for each width studied, and a note that the textbook population-count
loop leaks the output value through gas consumption.

All code, data, figures, and tables are reproducible from a fixed seed at
https://github.com/simontianx/OnChainRNG, including the Solidity reference
implementation and the gas benchmark.

The manuscript is original, is not under consideration elsewhere, and has not
been published previously. I am the sole author. I have no competing interests
to declare, and the work received no external funding.

Thank you for considering the manuscript.

Sincerely,

Simon Tian
Ninth Feature Capital
simon@9f.capital
