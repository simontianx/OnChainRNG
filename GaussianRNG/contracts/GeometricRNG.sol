// SPDX-License-Identifier: MIT

pragma solidity 0.8.4;

contract GeometricRNG {

    uint256 val;

    function getVal2() public pure returns (uint256) {
        return ~uint256(0);
    }

    function setVal(uint256 val) public {
        val = uint256(keccak256(abi.encodePacked(val)));
    }

    function getVal() public view returns (uint256) {
        return val;
    }

    function getN11s() public view returns (uint256) {
        return 256 - _mostSignificantBit(val & (val >> 1));
    }

    function getN111s() public view returns (uint256) {
        return 256 - _mostSignificantBit(val & (val >> 1) & (val >> 2));
    }

    function getN1111s() public view returns (uint256) {
        return 256 - _mostSignificantBit(val & (val >> 1) & (val >> 2) & (val >> 3));
    }

    function input(uint256 n) public pure returns (uint256) {
        uint256 temp = uint256(keccak256(abi.encodePacked(n)));
        return 256 - _mostSignificantBit(temp & (temp >> 1));
    }

    // returns the 0 indexed position of the most significant bit of the input x
    // s.t. x >= 2**msb and x < 2**(msb+1)
    function _mostSignificantBit(uint256 x) private pure returns (uint8 r) {
        require(x > 0, 'BitMath::mostSignificantBit: zero');

        if (x >= 0x100000000000000000000000000000000) {
            x >>= 128;
            r += 128;
        }

        if (x >= 0x10000000000000000) {
            x >>= 64;
            r += 64;
        }

        if (x >= 0x100000000) {
            x >>= 32;
            r += 32;
        }

        if (x >= 0x10000) {
            x >>= 16;
            r += 16;
        }

        if (x >= 0x100) {
            x >>= 8;
            r += 8;
        }

        if (x >= 0x10) {
            x >>= 4;
            r += 4;
        }

        if (x >= 0x4) {
            x >>= 2;
            r += 2;
        }

        if (x >= 0x2) r += 1;
    }
}
