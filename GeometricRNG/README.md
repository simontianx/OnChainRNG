# Geometric Random Number Generator
## Abstract
A novel on-chain Geometric random number generator is created. For the binary
representation of a hashed value by the `keccak256` hashing algorithm, the
number of `0`s proceeding the first `1` has a Geometric distribution.

## Methodology
A Geometric distribution is often used to describe the probability of a certain
number of failures before seeing a success. For a PoW consensus mechanism,
generating hashed values with a certain number of leading zeros can be seen as
sampling from a Geometric distribution.

## `keccak256` Algorithm
The `keccak256` hashing algorithm can generate pseudo randomness that is roughly
fair across all 256 digits, i.e., every digit has roughly equal probability of
being `0` or `1`. This property is the prerequisite for this RNG.

## Finding the Most Significant Digit
To find the most significant bit in Solidity, the algorithm can be found [here](https://github.com/Uniswap/uniswap-v3-core/blob/main/contracts/libraries/BitMath.sol).
