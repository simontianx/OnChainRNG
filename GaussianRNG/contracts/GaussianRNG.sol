// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface IGaussianRNG {
    function getGaussianRandomNumbers(uint256 salt, uint256 n) external view returns (uint256, int256[] memory);
    function reproduceGaussianRandomNumbers(uint256 seed, uint256 n) external view returns (int256[] memory);
    function countOnes(uint256 n) external pure returns (uint256);
}

///@author Simon Tian
///@title A novel on-chain Gaussian random number generator.
contract GaussianRNG is IGaussianRNG {

    /// @param salt A user provided number to create a seed, this can be
    /// an off-chain number or an on-chain source of randomness, to avoid miner
    /// manipulation.
    /// @param n The number of random numbers to be generated, ideally < 1000.
    /// @return seed The seed for this sequence of numbers, which can be used
    /// in another function for reproducing the same sequence of numbers.
    /// @return nums Desired sequence of Gaussian random numbers
    function getGaussianRandomNumbers(uint256 salt, uint256 n)
        external
        view
        override
        returns(uint256, int256[] memory)
    {
        uint256 seed = uint256(keccak256(abi.encodePacked(salt + block.timestamp)));
        return (seed, _GaussianRNG(seed, n));
    }

    /// To reproduce Gaussian random numbers with a given seed
    /// @param seed Seed value for a sequence of random numbers
    /// @param n The number of random numbers to be generated
    /// @return sequence of random numbers
    /// @notice This function is used for recreating a sequence of numbers given
    /// seed generated in the previous function.
    function reproduceGaussianRandomNumbers(uint256 seed, uint256 n)
        external
        pure
        override
        returns(int256[] memory)
    {
        return _GaussianRNG(seed, n);
    }

    /// The private function generating Gaussian random numbers
    /// @param seed Seed value for a sequence of random numbers
    /// @param n The number of random numbers to be generated
    /// @return sequence of random numbers
    function _GaussianRNG(uint256 seed, uint256 n)
        private
        pure
        returns (int256[] memory)
    {
        uint256 _num = uint256(keccak256(abi.encodePacked(seed)));
        int256[] memory results = new int256[](n);

        for (uint256 i = 0; i < n; i++) {
            uint256 result = _countOnes(_num);
            results[i] = int256(result * 125) - 16000;
            _num = uint256(keccak256(abi.encodePacked(_num)));
        }

        return results;
    }

    /// An external function for counting number of 1's in the binary representation
    /// of a hashed value produced by the keccak256 hashing algorithm.
    /// @param n The number to be checked.
    /// @return count The number of 1's.
    function countOnes(uint256 n) external pure override returns (uint256) {
        return _countOnes(n);
    }

    /// A private function to count the number of 1's using a SWAR
    /// (SIMD-within-a-register) reduction. The instruction count is fixed and
    /// does not depend on the input value, unlike the Kernighan loop
    /// (`n &= n - 1`), which costs one iteration per set bit and thereby
    /// leaks the Hamming weight through gas consumption. See
    /// benchmarks/README.md for measured gas.
    /// @param n The number to be checked.
    /// @return count The number of 1s.
    function _countOnes(uint256 n) private pure returns (uint256 count) {
        uint256 m1 = 0x5555555555555555555555555555555555555555555555555555555555555555;
        uint256 m2 = 0x3333333333333333333333333333333333333333333333333333333333333333;
        uint256 m4 = 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f;
        uint256 h01 = 0x0101010101010101010101010101010101010101010101010101010101010101;
        unchecked {
            n = n - ((n >> 1) & m1);
            n = (n & m2) + ((n >> 2) & m2);
            n = (n + (n >> 4)) & m4;
            // Each byte holds a count in [0, 8]; the byte-sum can reach 256,
            // so read the top 16 bits rather than the top byte.
            count = (n * h01) >> 248;
            // The only overflow case is n == type(uint256).max (count 256 wraps to 0).
            if (count == 0 && n != 0) count = 256;
        }
    }
}
