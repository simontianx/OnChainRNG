# EVM gas benchmark for the popcount Gaussian transform

Foundry project measuring the internal gas of each stage of the transform
`Z = 125 * popcount(keccak256(seed)) - 16000` on the EVM.

Run:

```bash
forge test -vvvv --match-test testGasProfile
```

`testPopcountAgreement` checks that the SWAR popcount agrees with the
Kernighan loop on 512 chained keccak digests and on the edge cases
`0`, `1`, `1 << 255`, and `2^256 - 1`.

## Results (2026-09-08)

forge 0.2.0 (0ad127a), solc 0.8.26, optimizer on (200 runs), EVM `cancun`,
2,000 chained keccak digests, gas measured with `gasleft()` deltas inside a
single call (so the numbers exclude the 21,000 base transaction cost and
calldata).

| Stage                             | Mean gas | Min   | Max   | Shape          |
|-----------------------------------|---------:|------:|------:|----------------|
| `keccak256` of one 32-byte word   |      268 |   221 |   316 | fixed (memory) |
| popcount, Kernighan loop          |    7,761 | 6,074 | 9,374 | data-dependent |
| popcount, SWAR                    |      233 |   233 |   233 | constant       |
| integer scaling `125 S - 16000`   |       29 |    29 |    29 | constant       |

Full transform per draw: about 530 gas with the SWAR popcount versus about
8,060 gas with the Kernighan loop. The Kernighan variant costs one loop
iteration per set bit, so its gas leaks the Hamming weight of the digest and
therefore the output value; the SWAR variant has a fixed instruction count.

The small spread in the `keccak256` row comes from memory-expansion cost in
`abi.encodePacked` and is not data-dependent in the digest value.
