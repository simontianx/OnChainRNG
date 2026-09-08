# An On-Chain Gaussian Random Number Generator
A novel on-chain Gaussian random number generator is proposed and presented in this project. It is taking the count of 1's in the binary representation of a hashed value calculated by the `keccak256` hashing algorithm, through proper transformations, according to Lyapunov Central Limit Theorem, to obtain a Gaussian distribution. It is lightning fast and costs little gas, and has a great potential in gaining broad applicability.

## `keccak256` Algorithm
`keccak256` algorithm is the default hashing algorithm to many blockchains. It is known to be generating pseudo randomness that is roughly fair across all `256` digits, i.e., every digit has roughly equal probability of being `0` or `1`. The independence of outcomes among all digits is assumed and being studied in a numerical study [here](https://github.com/simontianx/OnChainRNG/tree/main/GaussianRNG/docs/NumericalStudy).

## Algorithm for counting 1's
This is a well-known problem and a list of algorithms can be found [here](https://www.geeksforgeeks.org/count-set-bits-in-an-integer/).

## Lyapunov Central Limit Theorem
For a sequence of random numbers, the theorem states that even if they are not necessarily identically
distributed, although they have to be independent, the central limit theorem is still valid under [Lyapunov condition](https://en.wikipedia.org/wiki/Central_limit_theorem). Mathematical details of applying this theorem can be found in the [pdf](https://github.com/simontianx/OnChainRNG/blob/main/GaussianRNG/docs/GPRNG.pdf) in this repo.  

## Put it in Solidity and on blockchain
Suppose the desired count of `1`'s is denoted by `x`, and based on _Lyapunov Central Limit Theorem_, we can have `(x-128)/8` converges in distribution to a standard Gaussian distribution.

Since Solidity does not support floating numbers, and it is easy to realize that `(x-128)/8` can have at most 3 significant decimal numbers given `x` is an `uint256` integer and `1/8=0.125`. In practice, the number generated from this can be multiplied by `1000` and stored in an `int256` integer `x * 125 - 16000`. Users do not need to worry about fractions until later when the original scale has to be restored.

## Accuracy
This algorithm does not produce continuous Gaussian random numbers. The output is lattice-valued: with `256` bits the integer scale is `1000`, but adjacent outputs differ by `125`, so the effective resolution is `0.125` standard deviations (and the support is bounded at `±16` standard deviations). It may not cover all scenarios but it is a step forward to consume Gaussian randomness on-chain.

Resolution improves as `2/sqrt(n)`. Concatenating four `256`-bit digests into a `1024`-bit array gives `(x-512)/16 * 10000 = 625 * x - 320000` at scale `10000`, with resolution `0.0625` standard deviations. Each additional decimal digit of resolution costs a hundredfold increase in width, so widening is a coarse lever; if lower resolution is acceptable for lower gas cost, `1/4` of the current width is sufficient for half the resolution.

## Gas cost
Measured with Foundry (see `benchmarks/README.md`): one `keccak256` of a 32-byte word is about `270` gas, the SWAR population count used in `contracts/GaussianRNG.sol` is a constant `233` gas, and the integer scaling is `29` gas, so one Gaussian draw costs about `530` gas in total. The textbook Kernighan loop (`n &= n - 1`) averages about `7,800` gas and is data-dependent, which also leaks the output through gas consumption, so it should not be used.

## Source of randomness
The source of randomness is another topic and is not covered in the discussion of this algorithm, however, it is recommended to use a high-quality `salt` to initialize the sequence of Gaussian random numbers.
