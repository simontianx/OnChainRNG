#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import math
import os
import random
from dataclasses import dataclass
from statistics import NormalDist
from typing import Callable

from generate_study_artifacts import (
    N_SAMPLES,
    MAX_LAG,
    TAIL_Z_LEVELS,
    SUMMARY_TAIL_LEVELS,
    QQ_SUBSAMPLE,
    CDF_SAMPLE_SIZE,
    RANDOM_SEED,
    ASCII_CHARS,
    packed_uint256,
    packed_string,
    random_ascii_string,
    bits_from_digest,
    popcount_from_digest,
    pearson_correlation_with_index,
    acf_from_column,
    sample_quantile,
    sample_skewness,
    sample_excess_kurtosis,
    ks_distance_from_normal,
    wasserstein_distance_from_normal,
    lag_autocorrelation,
    runs_test_zscore,
    keccak256,
    format_cell,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated")


@dataclass(frozen=True)
class InputFamily:
    slug: str
    label: str
    sequential: bool
    generator: Callable[[int, random.Random], bytes]


@dataclass(frozen=True)
class TargetPrimitive:
    slug: str
    label: str
    vm_scope: str
    num_bits: int
    mode: str
    description: str
    hash_fn: Callable[[bytes], bytes] | None = None


def sha256_digest(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def stable_seed(label: str) -> int:
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return RANDOM_SEED ^ int.from_bytes(digest[:8], "big")


def num_bytes_for_bits(num_bits: int) -> int:
    return (num_bits + 7) // 8


def truncate_bits(digest: bytes, num_bits: int) -> bytes:
    byte_count = num_bytes_for_bits(num_bits)
    truncated = bytearray(digest[:byte_count])
    extra_bits = 8 * byte_count - num_bits
    if extra_bits > 0 and truncated:
        truncated[-1] &= (0xFF << extra_bits) & 0xFF
    return bytes(truncated)


def uniform_reference_bytes(rng: random.Random, num_bits: int) -> bytes:
    return truncate_bits(rng.getrandbits(num_bits).to_bytes(num_bytes_for_bits(num_bits), "big"), num_bits)


def target_mean(num_bits: int) -> float:
    return num_bits / 2.0


def target_sd(num_bits: int) -> float:
    return math.sqrt(num_bits) / 2.0


def bonferroni_z(num_bits: int) -> float:
    return NormalDist().inv_cdf(1.0 - 0.05 / (2 * num_bits))


def summarize_pairwise(columns: list[int], bit_counts: list[int], num_bits: int) -> tuple[float, float, float, float]:
    total_pairs = num_bits * (num_bits - 1) // 2
    total_rt = 0.0
    total_sm = 0.0
    total_abs_phi = 0.0
    max_abs_phi = 0.0

    for left in range(num_bits):
        left_count = bit_counts[left]
        for right in range(left + 1, num_bits):
            right_count = bit_counts[right]
            s11 = (columns[left] & columns[right]).bit_count()
            s10 = left_count - s11
            s01 = right_count - s11
            s00 = N_SAMPLES - s11 - s10 - s01
            mismatch = s10 + s01
            rt = (s11 + s00) / (N_SAMPLES + mismatch)
            sm = (s11 + s00) / N_SAMPLES
            denominator = math.sqrt((s10 + s11) * (s01 + s00) * (s11 + s01) * (s00 + s10))
            phi = 0.0 if denominator == 0.0 else (s11 * s00 - s10 * s01) / denominator
            total_rt += rt
            total_sm += sm
            total_abs_phi += abs(phi)
            max_abs_phi = max(max_abs_phi, abs(phi))

    return (
        total_rt / total_pairs,
        total_sm / total_pairs,
        total_abs_phi / total_pairs,
        max_abs_phi,
    )


def make_input_families() -> list[InputFamily]:
    return [
        InputFamily(
            slug="seq_uint",
            label="Sequential uint256 values",
            sequential=True,
            generator=lambda i, _rng: packed_uint256(i),
        ),
        InputFamily(
            slug="shifted_uint",
            label="Shifted uint256 values",
            sequential=True,
            generator=lambda i, _rng: packed_uint256((1 << 128) + i),
        ),
        InputFamily(
            slug="prefixed_seq",
            label="Prefixed sequential strings",
            sequential=True,
            generator=lambda i, _rng: packed_string(f"Transaction Number: {i}"),
        ),
        InputFamily(
            slug="prefixed_shifted",
            label="Prefixed shifted strings",
            sequential=True,
            generator=lambda i, _rng: packed_string(f"Transaction Number: {(1 << 128) + i}"),
        ),
        InputFamily(
            slug="random_ascii_7",
            label="Random ASCII strings up to length 7",
            sequential=False,
            generator=lambda _i, shared_rng: packed_string(random_ascii_string(shared_rng, 7)),
        ),
        InputFamily(
            slug="random_ascii_32",
            label="Random ASCII strings up to length 32",
            sequential=False,
            generator=lambda _i, shared_rng: packed_string(random_ascii_string(shared_rng, 32)),
        ),
    ]


def make_primitives() -> list[TargetPrimitive]:
    return [
        TargetPrimitive(
            slug="keccak256_vm",
            label="Keccak-256",
            vm_scope="EVM, Solana",
            num_bits=256,
            mode="hash",
            description="Shared VM-native Keccak-256 primitive for EVM and Solana",
            hash_fn=keccak256,
        ),
        TargetPrimitive(
            slug="sha256_vm",
            label="SHA-256",
            vm_scope="EVM, Solana",
            num_bits=256,
            mode="hash",
            description="Shared VM-native SHA-256 primitive for EVM and Solana",
            hash_fn=sha256_digest,
        ),
        TargetPrimitive(
            slug="sui_reference_256",
            label="Fair-bit control (256-bit)",
            vm_scope="Sui",
            num_bits=256,
            mode="uniform_reference",
            description="iid fair-bit control (MT19937 uniform bytes); reference model for Sui native randomness at 256 bits",
        ),
        TargetPrimitive(
            slug="sui_reference_512",
            label="Fair-bit control (512-bit)",
            vm_scope="Sui",
            num_bits=512,
            mode="uniform_reference",
            description="iid fair-bit control (MT19937 uniform bytes); reference model for Sui native randomness at 512 bits",
        ),
    ]


def sample_digest(
    primitive: TargetPrimitive,
    family: InputFamily,
    sample_index: int,
    input_rng: random.Random,
    uniform_rng: random.Random,
) -> bytes:
    if primitive.mode == "hash":
        input_bytes = family.generator(sample_index, input_rng)
        return primitive.hash_fn(input_bytes)
    return uniform_reference_bytes(uniform_rng, primitive.num_bits)


def generate_sequence_values(primitive: TargetPrimitive, seed_data: bytes, n_steps: int, sequence_id: str) -> list[int]:
    if primitive.mode == "hash":
        current = primitive.hash_fn(seed_data)
        values: list[int] = []
        for _ in range(n_steps):
            values.append(popcount_from_digest(current))
            current = primitive.hash_fn(current)
        return values

    sequence_rng = random.Random(stable_seed(f"{primitive.slug}:{sequence_id}"))
    return [popcount_from_digest(uniform_reference_bytes(sequence_rng, primitive.num_bits)) for _ in range(n_steps)]


def write_csv(path: str, header: list[str], rows: list[list[object]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    os.makedirs(GENERATED_DIR, exist_ok=True)

    input_families = make_input_families()
    primitives = make_primitives()
    standard_normal = NormalDist()

    family_rows: list[list[object]] = []
    pairwise_rows: list[list[object]] = []
    sequence_rows: list[list[object]] = []
    summary_rows: list[list[object]] = []

    sequence_seeds = [
        ("seed_uint_1", packed_uint256(1)),
        ("seed_uint_shifted", packed_uint256((1 << 128) + 1)),
        ("seed_string_tx", packed_string("Transaction Number: 1")),
        ("seed_string_alpha", packed_string("Sequence Seed: alpha-2026")),
    ]

    for primitive in primitives:
        primitive_target_mean = target_mean(primitive.num_bits)
        primitive_target_sd = target_sd(primitive.num_bits)
        primitive_normal = NormalDist(mu=primitive_target_mean, sigma=primitive_target_sd)
        primitive_bonferroni = bonferroni_z(primitive.num_bits)

        max_abs_bias_overall = 0.0
        max_abs_delta_mu = 0.0
        max_abs_delta_sigma = 0.0
        max_ks = 0.0
        max_wasserstein = 0.0
        max_abs_tail_error_z2 = 0.0
        max_abs_input_corr = 0.0
        max_abs_bit_acf = 0.0

        for family in input_families:
            input_rng = random.Random(stable_seed(f"input:{primitive.slug}:{family.slug}"))
            uniform_rng = random.Random(stable_seed(f"uniform:{primitive.slug}:{family.slug}"))
            columns = [0] * primitive.num_bits
            bit_counts = [0] * primitive.num_bits
            weighted_sums = [0] * primitive.num_bits
            popcounts: list[int] = []

            for sample_index in range(N_SAMPLES):
                digest = sample_digest(primitive, family, sample_index, input_rng, uniform_rng)
                bits = bits_from_digest(digest)[: primitive.num_bits]
                popcounts.append(sum(bits))
                bitmask = 1 << sample_index

                for bit_index, bit in enumerate(bits):
                    if bit:
                        bit_counts[bit_index] += 1
                        columns[bit_index] |= bitmask
                        if family.sequential:
                            weighted_sums[bit_index] += sample_index

            p_hats = [bit_count / N_SAMPLES for bit_count in bit_counts]
            mu_hat = sum(p_hats)
            sigma_hat_sq = sum(value * (1.0 - value) for value in p_hats)
            sigma_hat = math.sqrt(sigma_hat_sq)
            delta_mu = mu_hat - primitive_target_mean
            delta_sigma = sigma_hat - primitive_target_sd
            max_abs_bias = max(abs(p_hat - 0.5) for p_hat in p_hats)
            max_abs_bias_overall = max(max_abs_bias_overall, max_abs_bias)
            max_abs_delta_mu = max(max_abs_delta_mu, abs(delta_mu))
            max_abs_delta_sigma = max(max_abs_delta_sigma, abs(delta_sigma))

            sorted_popcounts = sorted(popcounts)
            mean_popcount = sum(popcounts) / len(popcounts)
            variance = sum((value - mean_popcount) ** 2 for value in popcounts) / len(popcounts)
            sd_popcount = math.sqrt(variance)
            popcount_ks = ks_distance_from_normal(sorted_popcounts, primitive_normal)
            popcount_wasserstein = wasserstein_distance_from_normal(sorted_popcounts, primitive_normal)
            popcount_skewness = sample_skewness(popcounts, mean_popcount, sd_popcount)
            popcount_excess_kurtosis = sample_excess_kurtosis(popcounts, mean_popcount, sd_popcount)
            max_ks = max(max_ks, popcount_ks)
            max_wasserstein = max(max_wasserstein, popcount_wasserstein)

            tail_error_z2_abs = 0.0
            for z_level in TAIL_Z_LEVELS:
                threshold = z_level * primitive_target_sd
                empirical_tail = sum(
                    1 for value in popcounts if abs(value - primitive_target_mean) >= threshold
                ) / len(popcounts)
                gaussian_tail = 2.0 * (1.0 - standard_normal.cdf(z_level))
                tail_error = empirical_tail - gaussian_tail
                if z_level == 2.0:
                    tail_error_z2_abs = abs(tail_error)
            max_abs_tail_error_z2 = max(max_abs_tail_error_z2, tail_error_z2_abs)

            max_family_input_corr = None
            max_family_bit_acf = None
            if family.sequential:
                correlations = []
                for bit_index, bit_count in enumerate(bit_counts):
                    corr = pearson_correlation_with_index(bit_count, weighted_sums[bit_index])
                    correlations.append(corr)
                max_family_input_corr = max(abs(value) for value in correlations)
                max_abs_input_corr = max(max_abs_input_corr, max_family_input_corr)

                max_family_bit_acf = 0.0
                for lag in range(1, MAX_LAG + 1):
                    lag_values = [
                        acf_from_column(columns[bit_index], bit_counts[bit_index], lag)
                        for bit_index in range(primitive.num_bits)
                    ]
                    max_family_bit_acf = max(max_family_bit_acf, max(abs(value) for value in lag_values))
                max_abs_bit_acf = max(max_abs_bit_acf, max_family_bit_acf)

            mean_se = sum(math.sqrt(p_hat * (1.0 - p_hat) / N_SAMPLES) for p_hat in p_hats) / primitive.num_bits
            max_conf_band_half_width = primitive_bonferroni * max(
                math.sqrt(p_hat * (1.0 - p_hat) / N_SAMPLES) for p_hat in p_hats
            )

            family_rows.append(
                [
                    primitive.slug,
                    primitive.label,
                    primitive.vm_scope,
                    primitive.num_bits,
                    family.slug,
                    family.label,
                    primitive_target_mean,
                    primitive_target_sd,
                    mu_hat,
                    sigma_hat,
                    delta_mu,
                    delta_sigma,
                    max_abs_bias,
                    mean_se,
                    max_conf_band_half_width,
                    mean_popcount,
                    sd_popcount,
                    popcount_skewness,
                    popcount_excess_kurtosis,
                    popcount_ks,
                    popcount_wasserstein,
                    tail_error_z2_abs,
                    max_family_input_corr if max_family_input_corr is not None else "",
                    max_family_bit_acf if max_family_bit_acf is not None else "",
                ]
            )

            if family.slug == "seq_uint":
                mean_rt, mean_sm, mean_abs_phi, max_abs_phi = summarize_pairwise(columns, bit_counts, primitive.num_bits)
                pairwise_rows.append(
                    [
                        primitive.slug,
                        primitive.label,
                        primitive.vm_scope,
                        primitive.num_bits,
                        mean_rt,
                        mean_sm,
                        mean_abs_phi,
                        max_abs_phi,
                    ]
                )

        max_abs_lag1 = 0.0
        max_abs_sequence_acf = 0.0
        max_abs_runs_z = 0.0
        max_abs_sequence_tail_error_z2 = 0.0

        for sequence_slug, seed_data in sequence_seeds:
            sequence_values = generate_sequence_values(primitive, seed_data, N_SAMPLES, sequence_slug)
            mean_popcount = sum(sequence_values) / len(sequence_values)
            variance = sum((value - mean_popcount) ** 2 for value in sequence_values) / len(sequence_values)
            sd_popcount = math.sqrt(variance)
            lag1_corr = lag_autocorrelation(sequence_values, 1)
            max_sequence_acf = 0.0
            for lag in range(1, MAX_LAG + 1):
                max_sequence_acf = max(max_sequence_acf, abs(lag_autocorrelation(sequence_values, lag)))
            runs_z = runs_test_zscore(sequence_values, threshold=primitive_target_mean)
            empirical_tail_z2 = sum(
                1 for value in sequence_values if abs(value - primitive_target_mean) >= 2.0 * primitive_target_sd
            ) / len(sequence_values)
            gaussian_tail_z2 = 2.0 * (1.0 - standard_normal.cdf(2.0))
            tail_error_z2 = empirical_tail_z2 - gaussian_tail_z2

            max_abs_lag1 = max(max_abs_lag1, abs(lag1_corr))
            max_abs_sequence_acf = max(max_abs_sequence_acf, max_sequence_acf)
            max_abs_runs_z = max(max_abs_runs_z, abs(runs_z))
            max_abs_sequence_tail_error_z2 = max(max_abs_sequence_tail_error_z2, abs(tail_error_z2))

            sequence_rows.append(
                [
                    primitive.slug,
                    primitive.label,
                    primitive.vm_scope,
                    primitive.num_bits,
                    sequence_slug,
                    mean_popcount,
                    sd_popcount,
                    lag1_corr,
                    max_sequence_acf,
                    runs_z,
                    tail_error_z2,
                ]
            )

        summary_rows.append(
            [
                primitive.slug,
                primitive.label,
                primitive.vm_scope,
                primitive.num_bits,
                primitive_target_mean,
                primitive_target_sd,
                max_abs_bias_overall,
                max_abs_delta_mu,
                max_abs_delta_sigma,
                max_ks,
                max_wasserstein,
                max_abs_tail_error_z2,
                max_abs_input_corr,
                max_abs_bit_acf,
                max_abs_lag1,
                max_abs_sequence_acf,
                max_abs_runs_z,
                max_abs_sequence_tail_error_z2,
                primitive.description,
            ]
        )

    write_csv(
        os.path.join(GENERATED_DIR, "cross_vm_family_metrics.csv"),
        [
            "primitive",
            "label",
            "vm_scope",
            "num_bits",
            "family",
            "family_label",
            "target_mean",
            "target_sd",
            "mu_hat",
            "sigma_hat",
            "delta_mu",
            "delta_sigma",
            "max_abs_bias",
            "mean_standard_error",
            "max_conf_band_half_width",
            "mean_popcount",
            "sd_popcount",
            "skewness",
            "excess_kurtosis",
            "ks_distance",
            "wasserstein_distance",
            "abs_tail_error_z2",
            "max_abs_input_corr",
            "max_abs_bit_acf",
        ],
        family_rows,
    )

    write_csv(
        os.path.join(GENERATED_DIR, "cross_vm_pairwise_metrics.csv"),
        [
            "primitive",
            "label",
            "vm_scope",
            "num_bits",
            "mean_rogers_tanimoto",
            "mean_sokal_michener",
            "mean_abs_phi",
            "max_abs_phi",
        ],
        pairwise_rows,
    )

    write_csv(
        os.path.join(GENERATED_DIR, "cross_vm_sequence_metrics.csv"),
        [
            "primitive",
            "label",
            "vm_scope",
            "num_bits",
            "sequence",
            "mean_popcount",
            "sd_popcount",
            "lag1_correlation",
            "max_abs_acf",
            "runs_test_z",
            "tail_error_z2",
        ],
        sequence_rows,
    )

    write_csv(
        os.path.join(GENERATED_DIR, "cross_vm_summary_metrics.csv"),
        [
            "primitive",
            "label",
            "vm_scope",
            "num_bits",
            "target_mean",
            "target_sd",
            "max_abs_bias",
            "max_abs_delta_mu",
            "max_abs_delta_sigma",
            "max_ks_distance",
            "max_wasserstein_distance",
            "max_abs_tail_error_z2",
            "max_abs_input_corr",
            "max_abs_bit_acf",
            "max_abs_lag1",
            "max_abs_sequence_acf",
            "max_abs_runs_z",
            "max_abs_sequence_tail_error_z2",
            "description",
        ],
        summary_rows,
    )

    with open(os.path.join(GENERATED_DIR, "cross_vm_summary_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrrrrr}\n")
        handle.write("\\hline\n")
        handle.write("Primitive & $n$ & $|\\Delta\\mu|$ & $|\\Delta\\sigma|$ & KS & $|\\Delta T_2|$ & Max $|\\rho_h|$ \\\\\n")
        handle.write("\\hline\n")
        for (
            _slug,
            label,
            _vm_scope,
            num_bits,
            _target_mean,
            _target_sd,
            _max_abs_bias,
            max_abs_delta_mu,
            max_abs_delta_sigma,
            max_ks_distance,
            _max_wasserstein,
            max_abs_tail_error_z2,
            _max_abs_input_corr,
            _max_abs_bit_acf,
            _max_abs_lag1,
            max_abs_sequence_acf,
            _max_abs_runs_z,
            _max_abs_sequence_tail_error_z2,
            _description,
        ) in summary_rows:
            handle.write(
                f"{label} & {num_bits} & {format_cell(max_abs_delta_mu)} & {format_cell(max_abs_delta_sigma)} & "
                f"{format_cell(max_ks_distance)} & {format_cell(max_abs_tail_error_z2)} & "
                f"{format_cell(max_abs_sequence_acf)} \\\\\n"
            )
        handle.write("\\hline\n")
        handle.write("\\end{tabular}\n")

    with open(os.path.join(GENERATED_DIR, "cross_vm_pairwise_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrrr}\n")
        handle.write("\\hline\n")
        handle.write("Primitive & Mean RT & Mean SM & Mean $|\\phi|$ & Max $|\\phi|$ \\\\\n")
        handle.write("\\hline\n")
        for _slug, label, _vm_scope, _num_bits, mean_rt, mean_sm, mean_abs_phi, max_abs_phi in pairwise_rows:
            handle.write(
                f"{label} & {format_cell(mean_rt)} & {format_cell(mean_sm)} & "
                f"{format_cell(mean_abs_phi)} & {format_cell(max_abs_phi)} \\\\\n"
            )
        handle.write("\\hline\n")
        handle.write("\\end{tabular}\n")


if __name__ == "__main__":
    main()
