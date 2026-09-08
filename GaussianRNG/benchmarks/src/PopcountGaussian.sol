// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Popcount-based Gaussian transform: reference implementations for gas measurement.
/// @notice Two population-count variants are provided so that the data-dependent
/// Kernighan loop can be compared against a constant-shape SWAR reduction.
library PopcountGaussian {
    /// @dev Kernighan loop: one iteration per set bit (~128 on average for a keccak digest).
    function popcountLoop(uint256 x) internal pure returns (uint256 count) {
        assembly {
            for {} gt(x, 0) {} {
                x := and(x, sub(x, 1))
                count := add(count, 1)
            }
        }
    }

    /// @dev SWAR (SIMD-within-a-register) popcount for a 256-bit word.
    /// Fixed instruction count, independent of the input value.
    function popcountSwar(uint256 x) internal pure returns (uint256 count) {
        uint256 m1 = 0x5555555555555555555555555555555555555555555555555555555555555555;
        uint256 m2 = 0x3333333333333333333333333333333333333333333333333333333333333333;
        uint256 m4 = 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f;
        uint256 h01 = 0x0101010101010101010101010101010101010101010101010101010101010101;
        unchecked {
            x = x - ((x >> 1) & m1);
            x = (x & m2) + ((x >> 2) & m2);
            x = (x + (x >> 4)) & m4;
            // Each byte now holds a count in [0, 8]; summing 32 bytes gives at most 256,
            // which does not fit in the top byte, so take the top 16 bits instead.
            count = (x * h01) >> 248;
            // Correct for the single overflow case (x == type(uint256).max).
            if (count == 0 && x != 0) count = 256;
        }
    }

    /// @dev Integer-scaled Gaussian output at n = 256, c = 1000: Z = 125 S - 16000.
    function gaussianFromCount(uint256 s) internal pure returns (int256) {
        unchecked {
            return int256(s) * 125 - 16000;
        }
    }
}

/// @notice Thin wrapper contract so that each step can be measured with an external call.
contract PopcountGaussianHarness {
    function hashOnly(uint256 seed) external pure returns (uint256) {
        return uint256(keccak256(abi.encodePacked(seed)));
    }

    function loopOnly(uint256 x) external pure returns (uint256) {
        return PopcountGaussian.popcountLoop(x);
    }

    function swarOnly(uint256 x) external pure returns (uint256) {
        return PopcountGaussian.popcountSwar(x);
    }

    function fullLoop(uint256 seed) external pure returns (int256) {
        uint256 h = uint256(keccak256(abi.encodePacked(seed)));
        return PopcountGaussian.gaussianFromCount(PopcountGaussian.popcountLoop(h));
    }

    function fullSwar(uint256 seed) external pure returns (int256) {
        uint256 h = uint256(keccak256(abi.encodePacked(seed)));
        return PopcountGaussian.gaussianFromCount(PopcountGaussian.popcountSwar(h));
    }
}
