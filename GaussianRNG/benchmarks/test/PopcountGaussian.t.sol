// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../src/PopcountGaussian.sol";

/// @notice Minimal test harness (no forge-std dependency) that reports internal gas
/// for each step of the popcount Gaussian transform via `gasleft()` deltas.
contract PopcountGaussianTest {
    uint256 internal constant N = 2000;

    function _check(bool ok, string memory what) internal pure {
        require(ok, what);
    }

    /// Correctness: SWAR and loop agree on keccak outputs and on edge cases.
    function testPopcountAgreement() public pure {
        uint256 h = 0;
        for (uint256 i = 0; i < 512; i++) {
            h = uint256(keccak256(abi.encodePacked(h, i)));
            _check(PopcountGaussian.popcountLoop(h) == PopcountGaussian.popcountSwar(h), "mismatch");
        }
        _check(PopcountGaussian.popcountSwar(0) == 0, "zero");
        _check(PopcountGaussian.popcountSwar(type(uint256).max) == 256, "max");
        _check(PopcountGaussian.popcountSwar(1) == 1, "one");
        _check(PopcountGaussian.popcountSwar(1 << 255) == 1, "top bit");
    }

    /// Emits mean/min/max internal gas for each stage; read from `forge test -vv`.
    event Gas(string stage, uint256 meanGas, uint256 minGas, uint256 maxGas);

    function _stats(uint256[] memory xs) internal pure returns (uint256 mean, uint256 lo, uint256 hi) {
        lo = type(uint256).max;
        uint256 total;
        for (uint256 i = 0; i < xs.length; i++) {
            total += xs[i];
            if (xs[i] < lo) lo = xs[i];
            if (xs[i] > hi) hi = xs[i];
        }
        mean = total / xs.length;
    }

    function testGasProfile() public {
        uint256[] memory gHash = new uint256[](N);
        uint256[] memory gLoop = new uint256[](N);
        uint256[] memory gSwar = new uint256[](N);
        uint256[] memory gScale = new uint256[](N);

        uint256 h = 0;
        for (uint256 i = 0; i < N; i++) {
            uint256 g0 = gasleft();
            uint256 next = uint256(keccak256(abi.encodePacked(h)));
            uint256 g1 = gasleft();
            uint256 c1 = PopcountGaussian.popcountLoop(next);
            uint256 g2 = gasleft();
            uint256 c2 = PopcountGaussian.popcountSwar(next);
            uint256 g3 = gasleft();
            int256 z = PopcountGaussian.gaussianFromCount(c2);
            uint256 g4 = gasleft();

            _check(c1 == c2, "count mismatch");
            _check(z == int256(c2) * 125 - 16000, "scale");

            gHash[i] = g0 - g1;
            gLoop[i] = g1 - g2;
            gSwar[i] = g2 - g3;
            gScale[i] = g3 - g4;
            h = next;
        }

        (uint256 m, uint256 lo, uint256 hi) = _stats(gHash);
        emit Gas("keccak256(32 bytes)", m, lo, hi);
        (m, lo, hi) = _stats(gLoop);
        emit Gas("popcount Kernighan loop", m, lo, hi);
        (m, lo, hi) = _stats(gSwar);
        emit Gas("popcount SWAR", m, lo, hi);
        (m, lo, hi) = _stats(gScale);
        emit Gas("integer scaling 125S-16000", m, lo, hi);
    }
}
