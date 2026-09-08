#!/usr/bin/env python3
"""Large-sample tail study for the popcount transform.

Draws 10^6 keccak256 popcounts for each of the six one-shot input families and
for each of the four repeated-hash chains, and compares the two-sided tail
probabilities of the standardized count against the continuous Gaussian and
the exact Binomial(256, 1/2) references.  Kept separate from
generate_study_artifacts.py so the 10,000-sample results there are unchanged.
"""
from __future__ import annotations

import csv
import math
import multiprocessing as mp
import os
import random
from statistics import NormalDist

import generate_study_artifacts as base

N_TAIL = 1_000_000
CHUNK = 20_000
Z_LEVELS = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
NUM_BITS = base.NUM_BITS
GENERATED_DIR = base.GENERATED_DIR
RANDOM_SEED = base.RANDOM_SEED

FAMILIES = [
    ("exp1_seq_uint", "Experiment 1.1", "seq_uint"),
    ("exp1_shifted_uint", "Experiment 1.2", "shifted_uint"),
    ("exp2_prefixed_seq", "Experiment 2.1", "prefixed_seq"),
    ("exp2_prefixed_shifted", "Experiment 2.2", "prefixed_shifted"),
    ("exp3_random_ascii_7", "Experiment 3.1", "ascii7"),
    ("exp3_random_ascii_32", "Experiment 3.2", "ascii32"),
]
CHAINS = [
    ("seq_uint_seed_1", "Sequence 1", base.packed_uint256(1)),
    ("seq_uint_seed_shifted", "Sequence 2", base.packed_uint256((1 << 128) + 1)),
    ("seq_string_seed_tx", "Sequence 3", base.packed_string("Transaction Number: 1")),
    ("seq_string_seed_alpha", "Sequence 4", base.packed_string("Sequence Seed: alpha-2026")),
]


def _input_bytes(kind: str, index: int, rng: random.Random) -> bytes:
    if kind == "seq_uint":
        return base.packed_uint256(index)
    if kind == "shifted_uint":
        return base.packed_uint256((1 << 128) + index)
    if kind == "prefixed_seq":
        return base.packed_string(f"Transaction Number: {index}")
    if kind == "prefixed_shifted":
        return base.packed_string(f"Transaction Number: {(1 << 128) + index}")
    if kind == "ascii7":
        return base.packed_string(base.random_ascii_string(rng, 7))
    if kind == "ascii32":
        return base.packed_string(base.random_ascii_string(rng, 32))
    raise ValueError(kind)


def family_chunk(args: tuple[str, int]) -> list[int]:
    kind, chunk_index = args
    rng = random.Random(f"{RANDOM_SEED}:{kind}:{chunk_index}")
    hist = [0] * (NUM_BITS + 1)
    start = chunk_index * CHUNK
    for index in range(start, start + CHUNK):
        digest = base.keccak256(_input_bytes(kind, index, rng))
        hist[sum(byte.bit_count() for byte in digest)] += 1
    return hist


def chain_hist(seed_data: bytes) -> list[int]:
    hist = [0] * (NUM_BITS + 1)
    current = base.keccak256(seed_data)
    for _ in range(N_TAIL):
        hist[sum(byte.bit_count() for byte in current)] += 1
        current = base.keccak256(current)
    return hist


def merge(hists: list[list[int]]) -> list[int]:
    total = [0] * (NUM_BITS + 1)
    for hist in hists:
        for k, value in enumerate(hist):
            total[k] += value
    return total


def two_sided_tail(hist: list[int], z: float) -> float:
    threshold = z * 8.0
    n = sum(hist)
    return sum(count for k, count in enumerate(hist) if abs(k - 128.0) >= threshold) / n


def binomial_pmf() -> list[float]:
    total = 2 ** NUM_BITS
    return [math.comb(NUM_BITS, k) / total for k in range(NUM_BITS + 1)]


def ks_vs_binomial(hist: list[int], pmf: list[float]) -> float:
    n = sum(hist)
    emp = 0
    ref = 0.0
    distance = 0.0
    for k in range(NUM_BITS + 1):
        emp += hist[k]
        ref += pmf[k]
        distance = max(distance, abs(emp / n - ref))
    return distance


def main() -> None:
    base.validate_keccak()
    os.makedirs(GENERATED_DIR, exist_ok=True)
    pmf = binomial_pmf()
    gaussian = NormalDist()
    n_chunks = N_TAIL // CHUNK

    ctx = mp.get_context("fork")
    with ctx.Pool(processes=max(1, os.cpu_count() or 1)) as pool:
        chain_results = [pool.apply_async(chain_hist, (seed,)) for _, _, seed in CHAINS]
        family_hists: dict[str, list[int]] = {}
        for slug, _label, kind in FAMILIES:
            family_hists[slug] = merge(pool.map(family_chunk, [(kind, c) for c in range(n_chunks)]))
        chain_hists = {slug: result.get() for (slug, _label, _seed), result in zip(CHAINS, chain_results)}

    binomial_hist_like = pmf  # probabilities, used with same tail function via scaling
    binomial_tails = {
        z: sum(p for k, p in enumerate(pmf) if abs(k - 128.0) >= z * 8.0) for z in Z_LEVELS
    }
    gaussian_tails = {z: 2.0 * (1.0 - gaussian.cdf(z)) for z in Z_LEVELS}

    rows: list[list[object]] = []
    table_rows: list[tuple[str, list[float]]] = []
    ks_rows: list[tuple[str, float, float, float]] = []
    worst_abs_z = 0.0
    all_targets = [(slug, label, family_hists[slug]) for slug, label, _ in FAMILIES] + [
        (slug, label, chain_hists[slug]) for slug, label, _ in CHAINS
    ]
    for slug, label, hist in all_targets:
        n = sum(hist)
        mean = sum(k * c for k, c in enumerate(hist)) / n
        sd = math.sqrt(sum((k - mean) ** 2 * c for k, c in enumerate(hist)) / n)
        ks_rows.append((label, mean, sd, ks_vs_binomial(hist, pmf)))
        tails: list[float] = []
        for z in Z_LEVELS:
            emp = two_sided_tail(hist, z)
            ref = binomial_tails[z]
            se = math.sqrt(ref * (1.0 - ref) / n)
            zscore = (emp - ref) / se if se > 0 else 0.0
            worst_abs_z = max(worst_abs_z, abs(zscore))
            tails.append(emp)
            rows.append([slug, label, z, emp, ref, gaussian_tails[z], emp - ref, se, zscore])
        table_rows.append((label, tails))

    base.write_csv(
        os.path.join(GENERATED_DIR, "tail_study_1e6.csv"),
        ["target", "label", "z", "empirical_tail", "binomial_tail", "gaussian_tail",
         "empirical_minus_binomial", "se_binomial", "z_score"],
        rows,
    )

    def fmt(p: float) -> str:
        return f"{p * 1000:.3f}"

    with open(os.path.join(GENERATED_DIR, "tail_study_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{l" + "r" * len(Z_LEVELS) + "}\n\\hline\n")
        handle.write("Target & " + " & ".join(f"$z={z:g}$" for z in Z_LEVELS) + " \\\\\n\\hline\n")
        handle.write("Gaussian & " + " & ".join(fmt(gaussian_tails[z]) for z in Z_LEVELS) + " \\\\\n")
        handle.write("Binomial$(256,\\tfrac12)$ & " + " & ".join(fmt(binomial_tails[z]) for z in Z_LEVELS) + " \\\\\n\\hline\n")
        for label, tails in table_rows:
            handle.write(f"{label} & " + " & ".join(fmt(t) for t in tails) + " \\\\\n")
        handle.write("\\hline\n\\end{tabular}\n")

    with open(os.path.join(GENERATED_DIR, "tail_study_ks_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrr}\n\\hline\n")
        handle.write("Target & Mean & SD & KS$_{\\mathrm{Bin}}$ \\\\\n\\hline\n")
        for label, mean, sd, ks in ks_rows:
            handle.write(f"{label} & {mean:.4f} & {sd:.4f} & {ks:.5f} \\\\\n")
        handle.write("\\hline\n\\end{tabular}\n")

    with open(os.path.join(GENERATED_DIR, "tail_study_metadata.txt"), "w", encoding="utf-8") as handle:
        handle.write(f"n_tail={N_TAIL}\nchunk={CHUNK}\nrandom_seed={RANDOM_SEED}\n")
        handle.write(f"ks_critical_5pct={1.36 / math.sqrt(N_TAIL):.6f}\n")
        handle.write(f"max_ks_binomial={max(r[3] for r in ks_rows):.6f}\n")
        handle.write(f"worst_abs_tail_zscore={worst_abs_z:.4f}\n")
        for z in Z_LEVELS:
            handle.write(f"binomial_tail_z{z:g}={binomial_tails[z]:.7f}\n")
            handle.write(f"gaussian_tail_z{z:g}={gaussian_tails[z]:.7f}\n")


if __name__ == "__main__":
    main()
