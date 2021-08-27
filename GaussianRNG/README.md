# An On-Chain Gaussian Random Number Generator
A novel on-chain Gaussian random number generator is proposed and presented in this project. It relies on the count of 1's in the hashed value produced by the `keccak256` hashing algorithm. By Lyapunov Central Limit Theorem, this count after proper transformations, has a Gaussian distribution. It is lightning fast and costs little gas, and has a great potential in gaining a broad applicability.

## `keccak256` algorithm
`keccak256` algorithm is the default hashing algorithm to many blockchains. It is known to be generating pseudo randomness that is roughly fair across all `256` digits, i.e., every digit has roughly equal probability of being `0` or `1`. The independence of outcomes among all digits is also an important property.

## Algorithm for counting 1's
This is a well-known problem and a list of algorithms can be found [here](https://www.geeksforgeeks.org/count-set-bits-in-an-integer/).

## Lyapunov Central Limit Theorem
For a sequence of random numbers, this theorem states even if they are not necessarily identically 
distributed, although they have to be independent, the central limit theorem is still valid under [Lyapunov condition](https://en.wikipedia.org/wiki/Central_limit_theorem). Mathematical details of applying this theorem can be found in the [pdf](https://github.com/simontianx/OnChainRNG/blob/main/GaussianRNG/docs/GPRNG.pdf) in this repo.  

## Put it in Solidity and on blockchain
Since Solidity does not support floating numbers, and it is easy to realize that `(x-128)/8` can have at most 3 significant decimal numbers given `x` is an `uint256` integer and `1/8=0.125`. In practice, the number generated from this can be multiplied by `1000` and stored in an `int256` integer `x * 125 - 16000`. Users do not need to worry about fractions until later when the original scale has to be restored.

## Accuracy and higher accuracy
This algorithm does not produce continuous Gaussian random numbers. Note this is an approximation with precision up to three decimal points. It may not cover all scenarios but it is a step forward to consume Gaussian randomness on-chain.

If the precision of one more decimal point is desired, four arrays of `256` binary digits can be concatenated to create a 
`1024`-digit array. The formula in this case is `(x-512)/16 * 10000 = 625 * x - 320000`. Again, the final results should be divided by `10000` instead of `1000` to restore the original scale.

A general rule is if one more decimal point in precision is desired, `3` times more digits are then needed. On the other hand, if a lower accuracy is acceptable for faster computing speed and lower gas costs, only `1/4` of digits to the current level are sufficient.

## Source of randomness
The source of randomness is another topic and is not covered in the discussion of this algorithm, however, it is recommended to use a high-quality `salt` to initialize the sequence of Gaussian random numbers.
