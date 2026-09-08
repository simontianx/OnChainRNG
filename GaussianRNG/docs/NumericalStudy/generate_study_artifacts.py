#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import os
import random
import string
from dataclasses import dataclass
from statistics import NormalDist
from typing import Callable

MASK64 = (1 << 64) - 1
NUM_BITS = 256
BLOCK_SIZE_BITS = 16
NUM_BLOCKS = NUM_BITS // BLOCK_SIZE_BITS
N_SAMPLES = 10_000
MAX_LAG = 30
CDF_SAMPLE_SIZE = 3_000
QQ_SUBSAMPLE = 500
SEQUENCE_SCATTER_LIMIT = 3_000
RANDOM_SEED = 20260415
ASCII_CHARS = string.ascii_letters + string.punctuation + string.digits
BONFERRONI_Z = NormalDist().inv_cdf(1.0 - 0.05 / (2 * NUM_BITS))
TAIL_Z_LEVELS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
SUMMARY_TAIL_LEVELS = [1.0, 2.0, 3.0]
QUANTILE_LEVELS = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated")

ROUND_CONSTANTS = [
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808A,
    0x8000000080008000,
    0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008A,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000A,
    0x000000008000808B,
    0x800000000000008B,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A,
    0x800000008000000A,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
]

ROTATION_OFFSETS = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14],
]


@dataclass(frozen=True)
class Experiment:
    slug: str
    label: str
    sequential: bool
    generator: Callable[[int, random.Random], bytes]


@dataclass(frozen=True)
class SequenceExperiment:
    slug: str
    label: str
    seed_data: bytes


def rotl64(value: int, shift: int) -> int:
    shift %= 64
    return ((value << shift) | (value >> (64 - shift))) & MASK64


def keccak_f1600(state: list[int]) -> None:
    for rc in ROUND_CONSTANTS:
        c = [state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20] for x in range(5)]
        d = [c[(x - 1) % 5] ^ rotl64(c[(x + 1) % 5], 1) for x in range(5)]

        for x in range(5):
            for y in range(5):
                state[x + 5 * y] ^= d[x]

        b = [0] * 25
        for x in range(5):
            for y in range(5):
                b[y + 5 * ((2 * x + 3 * y) % 5)] = rotl64(state[x + 5 * y], ROTATION_OFFSETS[x][y])

        for x in range(5):
            for y in range(5):
                state[x + 5 * y] = b[x + 5 * y] ^ ((~b[(x + 1) % 5 + 5 * y]) & b[(x + 2) % 5 + 5 * y] & MASK64)

        state[0] ^= rc


def keccak256(data: bytes) -> bytes:
    rate_bytes = 136
    state = [0] * 25
    offset = 0

    while offset + rate_bytes <= len(data):
        block = data[offset : offset + rate_bytes]
        for lane_index in range(rate_bytes // 8):
            lane = int.from_bytes(block[8 * lane_index : 8 * lane_index + 8], "little")
            state[lane_index] ^= lane
        keccak_f1600(state)
        offset += rate_bytes

    tail = bytearray(data[offset:])
    tail.append(0x01)
    while len(tail) < rate_bytes:
        tail.append(0)
    tail[-1] ^= 0x80

    for lane_index in range(rate_bytes // 8):
        lane = int.from_bytes(tail[8 * lane_index : 8 * lane_index + 8], "little")
        state[lane_index] ^= lane
    keccak_f1600(state)

    output = bytearray()
    while len(output) < 32:
        for lane_index in range(rate_bytes // 8):
            output.extend(state[lane_index].to_bytes(8, "little"))
        if len(output) >= 32:
            break
        keccak_f1600(state)

    return bytes(output[:32])


def packed_uint256(value: int) -> bytes:
    return value.to_bytes(32, "big", signed=False)


def packed_string(value: str) -> bytes:
    return value.encode("utf-8")


def random_ascii_string(rng: random.Random, max_length: int) -> str:
    length = rng.randint(2, max_length)
    return "".join(rng.choice(ASCII_CHARS) for _ in range(length))


def bits_from_digest(digest: bytes) -> list[int]:
    return [1 if byte & (0x80 >> offset) else 0 for byte in digest for offset in range(8)]


def popcount_from_digest(digest: bytes) -> int:
    return sum(byte.bit_count() for byte in digest)


def block_popcounts_from_digest(digest: bytes) -> list[int]:
    block_bytes = BLOCK_SIZE_BITS // 8
    return [
        sum(byte.bit_count() for byte in digest[start : start + block_bytes])
        for start in range(0, NUM_BITS // 8, block_bytes)
    ]


def sample_correlation(left: list[int], right: list[int]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    ss_left = sum((value - mean_left) ** 2 for value in left)
    ss_right = sum((value - mean_right) ** 2 for value in right)
    if ss_left == 0.0 or ss_right == 0.0:
        return 0.0
    covariance = sum((lval - mean_left) * (rval - mean_right) for lval, rval in zip(left, right))
    return covariance / math.sqrt(ss_left * ss_right)


def pearson_correlation_with_index(bit_count: int, weighted_sum: int) -> float:
    sum_x = N_SAMPLES * (N_SAMPLES - 1) / 2
    sum_x2 = (N_SAMPLES - 1) * N_SAMPLES * (2 * N_SAMPLES - 1) / 6
    ss_x = sum_x2 - (sum_x * sum_x) / N_SAMPLES
    ss_y = bit_count - (bit_count * bit_count) / N_SAMPLES
    if ss_y <= 0:
        return 0.0
    covariance = weighted_sum - (sum_x * bit_count) / N_SAMPLES
    return covariance / math.sqrt(ss_x * ss_y)


def acf_from_column(column: int, bit_count: int, lag: int) -> float:
    p_hat = bit_count / N_SAMPLES
    c0 = p_hat * (1.0 - p_hat)
    if c0 == 0.0:
        return 0.0

    mask = (1 << (N_SAMPLES - lag)) - 1
    lead = column & mask
    lagged = (column >> lag) & mask
    lead_count = lead.bit_count()
    lagged_count = lagged.bit_count()
    joint_count = (lead & lagged).bit_count()

    numerator = joint_count - p_hat * (lead_count + lagged_count) + (N_SAMPLES - lag) * (p_hat ** 2)
    return numerator / (N_SAMPLES * c0)


def write_csv(path: str, header: list[str], rows: list[list[object]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def format_cell(value: float | None) -> str:
    if value is None:
        return "--"
    return f"{value:.4f}"


def sample_quantile(sorted_values: list[int], probability: float) -> float:
    if probability <= 0.0:
        return float(sorted_values[0])
    if probability >= 1.0:
        return float(sorted_values[-1])

    position = (len(sorted_values) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return float(sorted_values[lower_index])

    weight = position - lower_index
    return (1.0 - weight) * sorted_values[lower_index] + weight * sorted_values[upper_index]


def sample_skewness(values: list[int], mean_value: float, sd_value: float) -> float:
    if sd_value == 0.0:
        return 0.0
    return sum(((value - mean_value) / sd_value) ** 3 for value in values) / len(values)


def sample_excess_kurtosis(values: list[int], mean_value: float, sd_value: float) -> float:
    if sd_value == 0.0:
        return 0.0
    return sum(((value - mean_value) / sd_value) ** 4 for value in values) / len(values) - 3.0


def ks_distance_from_normal(sorted_values: list[int], normal_dist: NormalDist) -> float:
    n_values = len(sorted_values)
    distance = 0.0
    for index, value in enumerate(sorted_values, start=1):
        gaussian_cdf = normal_dist.cdf(value)
        distance = max(distance, abs(index / n_values - gaussian_cdf))
        distance = max(distance, abs((index - 1) / n_values - gaussian_cdf))
    return distance


def wasserstein_distance_from_normal(sorted_values: list[int], normal_dist: NormalDist) -> float:
    n_values = len(sorted_values)
    total = 0.0
    for index, value in enumerate(sorted_values, start=1):
        probability = (index - 0.5) / n_values
        total += abs(value - normal_dist.inv_cdf(probability))
    return total / n_values


def binomial_reference_cdf(n_bits: int) -> list[float]:
    total = 2 ** n_bits
    cumulative = 0
    cdf: list[float] = []
    for k in range(n_bits + 1):
        cumulative += math.comb(n_bits, k)
        cdf.append(cumulative / total)
    return cdf


def lattice_counts(sorted_values: list[int], n_bits: int) -> list[int]:
    counts = [0] * (n_bits + 1)
    for value in sorted_values:
        counts[value] += 1
    return counts


def ks_distance_from_binomial(sorted_values: list[int], binomial_cdf: list[float]) -> float:
    # Both laws live on the lattice {0,...,n}, so the supremum is attained at lattice points.
    n_values = len(sorted_values)
    counts = lattice_counts(sorted_values, len(binomial_cdf) - 1)
    distance = 0.0
    cumulative = 0
    for k, count in enumerate(counts):
        cumulative += count
        distance = max(distance, abs(cumulative / n_values - binomial_cdf[k]))
    return distance


def wasserstein_distance_from_binomial(sorted_values: list[int], binomial_cdf: list[float]) -> float:
    # W1 between two lattice laws with unit spacing is the sum of |F_emp(k) - F_ref(k)|.
    n_values = len(sorted_values)
    counts = lattice_counts(sorted_values, len(binomial_cdf) - 1)
    total = 0.0
    cumulative = 0
    for k, count in enumerate(counts):
        cumulative += count
        total += abs(cumulative / n_values - binomial_cdf[k])
    return total


def ks_floor_binomial_vs_normal(binomial_cdf: list[float], normal_dist: NormalDist) -> float:
    # Same two-sided convention as ks_distance_from_normal, applied to the exact binomial law.
    distance = 0.0
    previous = 0.0
    for k, cdf_value in enumerate(binomial_cdf):
        gaussian_cdf = normal_dist.cdf(k)
        distance = max(distance, abs(cdf_value - gaussian_cdf), abs(previous - gaussian_cdf))
        previous = cdf_value
    return distance


def lag_autocorrelation(values: list[int], lag: int) -> float:
    if lag <= 0 or lag >= len(values):
        return 0.0
    mean_value = sum(values) / len(values)
    denominator = sum((value - mean_value) ** 2 for value in values)
    if denominator == 0.0:
        return 0.0
    numerator = sum(
        (values[index] - mean_value) * (values[index - lag] - mean_value)
        for index in range(lag, len(values))
    )
    return numerator / denominator


def runs_test_zscore(values: list[int], threshold: float = 128.0) -> float:
    indicators = [1 if value >= threshold else 0 for value in values]
    n1 = sum(indicators)
    n0 = len(indicators) - n1
    if len(indicators) < 2 or n1 == 0 or n0 == 0:
        return 0.0

    runs = 1
    for index in range(1, len(indicators)):
        if indicators[index] != indicators[index - 1]:
            runs += 1

    expected_runs = 1.0 + 2.0 * n1 * n0 / len(indicators)
    variance = (2.0 * n1 * n0 * (2.0 * n1 * n0 - len(indicators))) / (
        (len(indicators) ** 2) * (len(indicators) - 1)
    )
    if variance <= 0.0:
        return 0.0
    return (runs - expected_runs) / math.sqrt(variance)


def generate_repeated_hash_popcounts(seed_data: bytes, n_steps: int) -> list[int]:
    current = keccak256(seed_data)
    popcounts: list[int] = []
    for _ in range(n_steps):
        popcounts.append(popcount_from_digest(current))
        current = keccak256(current)
    return popcounts


def validate_keccak() -> None:
    known_vectors = {
        bytes.fromhex("00"): "bc36789e7a1e281436464229828f817d6612f7b477d66591ff96a9e064bcc98a",
        packed_uint256(1): "b10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6",
        packed_string("Transaction Number: 1"): "f2de198d741e209c31fb5675c5b7ddd6b1fa3bbab08423d1078f3d7059121fac",
    }
    for data, expected in known_vectors.items():
        observed = keccak256(data).hex()
        if observed != expected:
            raise RuntimeError(f"Keccak validation failed: expected {expected}, got {observed}")


def main() -> None:
    validate_keccak()
    os.makedirs(GENERATED_DIR, exist_ok=True)

    rng = random.Random(RANDOM_SEED)
    standard_normal = NormalDist()
    target_normal = NormalDist(mu=128, sigma=8)
    binomial_cdf = binomial_reference_cdf(NUM_BITS)
    binomial_normal_ks_floor = ks_floor_binomial_vs_normal(binomial_cdf, target_normal)

    experiments = [
        Experiment(
            slug="exp1_seq_uint",
            label="Experiment 1.1: Sequential uint256 values",
            sequential=True,
            generator=lambda i, _: packed_uint256(i),
        ),
        Experiment(
            slug="exp1_shifted_uint",
            label="Experiment 1.2: Shifted uint256 values",
            sequential=True,
            generator=lambda i, _: packed_uint256((1 << 128) + i),
        ),
        Experiment(
            slug="exp2_prefixed_seq",
            label="Experiment 2.1: Prefixed sequential strings",
            sequential=True,
            generator=lambda i, _: packed_string(f"Transaction Number: {i}"),
        ),
        Experiment(
            slug="exp2_prefixed_shifted",
            label="Experiment 2.2: Prefixed shifted strings",
            sequential=True,
            generator=lambda i, _: packed_string(f"Transaction Number: {(1 << 128) + i}"),
        ),
        Experiment(
            slug="exp3_random_ascii_7",
            label="Experiment 3.1: Random ASCII strings up to length 7",
            sequential=False,
            generator=lambda _i, shared_rng: packed_string(random_ascii_string(shared_rng, 7)),
        ),
        Experiment(
            slug="exp3_random_ascii_32",
            label="Experiment 3.2: Random ASCII strings up to length 32",
            sequential=False,
            generator=lambda _i, shared_rng: packed_string(random_ascii_string(shared_rng, 32)),
        ),
    ]
    sequence_experiments = [
        SequenceExperiment(
            slug="seq_uint_seed_1",
            label="Sequence 1: repeated hashing from uint256 seed 1",
            seed_data=packed_uint256(1),
        ),
        SequenceExperiment(
            slug="seq_uint_seed_shifted",
            label="Sequence 2: repeated hashing from uint256 seed 2^128+1",
            seed_data=packed_uint256((1 << 128) + 1),
        ),
        SequenceExperiment(
            slug="seq_string_seed_tx",
            label="Sequence 3: repeated hashing from string seed Transaction Number: 1",
            seed_data=packed_string("Transaction Number: 1"),
        ),
        SequenceExperiment(
            slug="seq_string_seed_alpha",
            label="Sequence 4: repeated hashing from string seed Sequence Seed: alpha-2026",
            seed_data=packed_string("Sequence Seed: alpha-2026"),
        ),
    ]

    experiment_labels = {experiment.slug: experiment.label for experiment in experiments}
    columns_by_experiment: dict[str, list[int]] = {}
    bit_counts_by_experiment: dict[str, list[int]] = {}
    popcounts_by_experiment: dict[str, list[int]] = {}
    block_popcounts_by_experiment: dict[str, list[list[int]]] = {}
    weighted_sums_by_experiment: dict[str, list[int]] = {}

    for experiment in experiments:
        columns = [0] * NUM_BITS
        bit_counts = [0] * NUM_BITS
        popcounts: list[int] = []
        block_popcounts: list[list[int]] = []
        weighted_sums = [0] * NUM_BITS

        for sample_index in range(N_SAMPLES):
            digest = keccak256(experiment.generator(sample_index, rng))
            popcount = sum(byte.bit_count() for byte in digest)
            popcounts.append(popcount)
            block_popcounts.append(block_popcounts_from_digest(digest))
            bitmask = 1 << sample_index

            for bit_index, bit in enumerate(bits_from_digest(digest)):
                if bit:
                    bit_counts[bit_index] += 1
                    columns[bit_index] |= bitmask
                    if experiment.sequential:
                        weighted_sums[bit_index] += sample_index

        columns_by_experiment[experiment.slug] = columns
        bit_counts_by_experiment[experiment.slug] = bit_counts
        popcounts_by_experiment[experiment.slug] = popcounts
        block_popcounts_by_experiment[experiment.slug] = block_popcounts
        weighted_sums_by_experiment[experiment.slug] = weighted_sums

    uniformity_rows: list[list[object]] = []
    input_corr_rows: list[list[object]] = []
    acf_rows: list[list[object]] = []
    popcount_rows: list[list[object]] = []
    summary_rows: list[list[object]] = []
    normalization_rows: list[list[object]] = []
    distribution_rows: list[list[object]] = []
    quantile_rows: list[list[object]] = []
    qq_rows: list[list[object]] = []
    tail_rows: list[list[object]] = []
    sequence_summary_rows: list[list[object]] = []
    sequence_acf_rows: list[list[object]] = []
    sequence_scatter_rows: list[list[object]] = []
    block_correlation_rows: list[list[object]] = []
    block_correlation_summary_rows: list[list[object]] = []

    for experiment in experiments:
        bit_counts = bit_counts_by_experiment[experiment.slug]
        popcounts = popcounts_by_experiment[experiment.slug]
        p_hats = [bit_count / N_SAMPLES for bit_count in bit_counts]

        mean_popcount = sum(popcounts) / len(popcounts)
        variance = sum((value - mean_popcount) ** 2 for value in popcounts) / len(popcounts)
        sd_popcount = math.sqrt(variance)

        mu_hat = sum(p_hats)
        sigma_hat_sq = sum(value * (1.0 - value) for value in p_hats)
        sigma_hat = math.sqrt(sigma_hat_sq)
        delta_mu = mu_hat - 128.0
        delta_sigma = sigma_hat - 8.0
        sum_squared_bit_bias = sum((value - 0.5) ** 2 for value in p_hats)
        # Shift of the practical standardized output caused by the summed bit bias.
        centering_shift_z = delta_mu / 8.0
        # Ratio of the observed popcount variance to the independence-implied variance.
        # Under independent bits this is 1; dependence moves it away from 1.
        variance_ratio = variance / sigma_hat_sq
        normalization_rows.append(
            [
                experiment.slug,
                experiment.label,
                mu_hat,
                sigma_hat,
                delta_mu,
                delta_sigma,
                sum_squared_bit_bias,
                centering_shift_z,
                sd_popcount,
                variance_ratio,
            ]
        )

        max_abs_bias = 0.0
        for bit_index, p_hat in enumerate(p_hats):
            se = math.sqrt(p_hat * (1.0 - p_hat) / N_SAMPLES)
            lower = p_hat - BONFERRONI_Z * se
            upper = p_hat + BONFERRONI_Z * se
            max_abs_bias = max(max_abs_bias, abs(p_hat - 0.5))
            uniformity_rows.append(
                [experiment.slug, experiment.label, bit_index, p_hat, se, lower, upper]
            )

        sorted_popcounts = sorted(popcounts)
        popcount_ks = ks_distance_from_normal(sorted_popcounts, target_normal)
        popcount_wasserstein = wasserstein_distance_from_normal(sorted_popcounts, target_normal)
        popcount_ks_binomial = ks_distance_from_binomial(sorted_popcounts, binomial_cdf)
        popcount_wasserstein_binomial = wasserstein_distance_from_binomial(sorted_popcounts, binomial_cdf)
        popcount_skewness = sample_skewness(popcounts, mean_popcount, sd_popcount)
        popcount_excess_kurtosis = sample_excess_kurtosis(popcounts, mean_popcount, sd_popcount)

        max_abs_input_corr = None
        max_abs_acf = None

        if experiment.sequential:
            correlations: list[float] = []
            for bit_index, bit_count in enumerate(bit_counts):
                correlation = pearson_correlation_with_index(
                    bit_count,
                    weighted_sums_by_experiment[experiment.slug][bit_index],
                )
                correlations.append(correlation)
                input_corr_rows.append(
                    [experiment.slug, experiment.label, bit_index, correlation]
                )
            max_abs_input_corr = max(abs(value) for value in correlations)

            max_abs_acf = 0.0
            columns = columns_by_experiment[experiment.slug]
            for lag in range(1, MAX_LAG + 1):
                lag_values = [acf_from_column(columns[bit_index], bit_counts[bit_index], lag) for bit_index in range(NUM_BITS)]
                lag_max = max(abs(value) for value in lag_values)
                lag_mean_abs = sum(abs(value) for value in lag_values) / NUM_BITS
                max_abs_acf = max(max_abs_acf, lag_max)
                acf_rows.append(
                    [experiment.slug, experiment.label, lag, lag_max, lag_mean_abs]
                )

        for probability in QUANTILE_LEVELS:
            empirical_quantile = sample_quantile(sorted_popcounts, probability)
            gaussian_quantile = target_normal.inv_cdf(probability)
            quantile_rows.append(
                [
                    experiment.slug,
                    experiment.label,
                    probability,
                    empirical_quantile,
                    gaussian_quantile,
                    empirical_quantile - gaussian_quantile,
                ]
            )

        qq_step = max(1, len(sorted_popcounts) // QQ_SUBSAMPLE)
        for index in range(qq_step - 1, len(sorted_popcounts), qq_step):
            probability = (index + 0.5) / len(sorted_popcounts)
            qq_rows.append(
                [
                    experiment.slug,
                    experiment.label,
                    probability,
                    target_normal.inv_cdf(probability),
                    sorted_popcounts[index],
                ]
            )

        tail_error_summary: dict[float, float] = {}
        for z_level in TAIL_Z_LEVELS:
            threshold = z_level * 8.0
            empirical_tail = sum(1 for value in popcounts if abs(value - 128.0) >= threshold) / len(popcounts)
            gaussian_tail = 2.0 * (1.0 - standard_normal.cdf(z_level))
            tail_error = empirical_tail - gaussian_tail
            tail_rows.append(
                [
                    experiment.slug,
                    experiment.label,
                    z_level,
                    empirical_tail,
                    gaussian_tail,
                    tail_error,
                    abs(tail_error),
                ]
            )
            if z_level in SUMMARY_TAIL_LEVELS:
                tail_error_summary[z_level] = abs(tail_error)

        distribution_rows.append(
            [
                experiment.slug,
                experiment.label,
                mean_popcount,
                sd_popcount,
                popcount_skewness,
                popcount_excess_kurtosis,
                popcount_ks,
                popcount_wasserstein,
                popcount_ks_binomial,
                popcount_wasserstein_binomial,
                tail_error_summary[1.0],
                tail_error_summary[2.0],
                tail_error_summary[3.0],
            ]
        )

        summary_rows.append(
            [
                experiment.slug,
                experiment.label,
                max_abs_bias,
                mean_popcount,
                sd_popcount,
                max_abs_input_corr if max_abs_input_corr is not None else "",
                max_abs_acf if max_abs_acf is not None else "",
                mu_hat,
                sigma_hat,
            ]
        )

        block_columns = [
            [row[block_index] for row in block_popcounts_by_experiment[experiment.slug]]
            for block_index in range(NUM_BLOCKS)
        ]
        block_abs_correlations: list[float] = []
        for left in range(NUM_BLOCKS):
            for right in range(left + 1, NUM_BLOCKS):
                correlation = sample_correlation(block_columns[left], block_columns[right])
                block_abs_correlations.append(abs(correlation))
                block_correlation_rows.append(
                    [experiment.slug, experiment.label, left, right, correlation, abs(correlation)]
                )

        block_correlation_summary_rows.append(
            [
                experiment.slug,
                experiment.label,
                sum(block_abs_correlations) / len(block_abs_correlations),
                max(block_abs_correlations),
            ]
        )

    base_columns = columns_by_experiment["exp1_seq_uint"]
    base_counts = bit_counts_by_experiment["exp1_seq_uint"]
    pairwise_rows: list[list[object]] = []
    for left in range(NUM_BITS):
        left_count = base_counts[left]
        for right in range(left + 1, NUM_BITS):
            right_count = base_counts[right]
            s11 = (base_columns[left] & base_columns[right]).bit_count()
            s10 = left_count - s11
            s01 = right_count - s11
            s00 = N_SAMPLES - s11 - s10 - s01
            mismatch = s10 + s01
            rt = (s11 + s00) / (N_SAMPLES + mismatch)
            sm = (s11 + s00) / N_SAMPLES
            denominator = math.sqrt((s10 + s11) * (s01 + s00) * (s11 + s01) * (s00 + s10))
            phi = 0.0 if denominator == 0 else (s11 * s00 - s10 * s01) / denominator
            pairwise_rows.append([left, right, rt, phi, sm])

    cdf_source = popcounts_by_experiment["exp3_random_ascii_32"][:CDF_SAMPLE_SIZE]
    cdf_rows: list[list[object]] = []
    ks_distance = 0.0
    for rank, popcount in enumerate(sorted(cdf_source), start=1):
        empirical_cdf = rank / CDF_SAMPLE_SIZE
        gaussian_cdf = target_normal.cdf(popcount)
        ks_distance = max(ks_distance, abs(empirical_cdf - gaussian_cdf))
        cdf_rows.append([popcount, empirical_cdf, gaussian_cdf])

    for experiment in experiments:
        for sample_index, popcount in enumerate(popcounts_by_experiment[experiment.slug], start=1):
            popcount_rows.append([experiment.slug, experiment.label, sample_index, popcount])

    for sequence_experiment in sequence_experiments:
        sequence_values = generate_repeated_hash_popcounts(sequence_experiment.seed_data, N_SAMPLES)
        mean_popcount = sum(sequence_values) / len(sequence_values)
        variance = sum((value - mean_popcount) ** 2 for value in sequence_values) / len(sequence_values)
        sd_popcount = math.sqrt(variance)
        lag1_corr = lag_autocorrelation(sequence_values, 1)
        max_abs_acf = 0.0
        for lag in range(1, MAX_LAG + 1):
            acf_value = lag_autocorrelation(sequence_values, lag)
            max_abs_acf = max(max_abs_acf, abs(acf_value))
            sequence_acf_rows.append(
                [sequence_experiment.slug, sequence_experiment.label, lag, acf_value, abs(acf_value)]
            )

        runs_z = runs_test_zscore(sequence_values, threshold=128.0)
        empirical_tail_z2 = sum(1 for value in sequence_values if abs(value - 128.0) >= 16.0) / len(sequence_values)
        gaussian_tail_z2 = 2.0 * (1.0 - standard_normal.cdf(2.0))
        tail_error_z2 = empirical_tail_z2 - gaussian_tail_z2

        sequence_summary_rows.append(
            [
                sequence_experiment.slug,
                sequence_experiment.label,
                mean_popcount,
                sd_popcount,
                lag1_corr,
                max_abs_acf,
                runs_z,
                tail_error_z2,
            ]
        )

        scatter_limit = min(SEQUENCE_SCATTER_LIMIT, len(sequence_values) - 1)
        for index in range(scatter_limit):
            sequence_scatter_rows.append(
                [
                    sequence_experiment.slug,
                    sequence_experiment.label,
                    index + 1,
                    sequence_values[index],
                    sequence_values[index + 1],
                ]
            )

    write_csv(
        os.path.join(GENERATED_DIR, "uniformity.csv"),
        ["experiment", "label", "bit_index", "mean", "se", "lower", "upper"],
        uniformity_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "input_correlations.csv"),
        ["experiment", "label", "bit_index", "correlation"],
        input_corr_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "autocorrelation.csv"),
        ["experiment", "label", "lag", "max_abs_acf", "mean_abs_acf"],
        acf_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "pairwise_metrics.csv"),
        ["left_bit", "right_bit", "rogers_tanimoto", "phi_correlation", "sokal_michener"],
        pairwise_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "popcount_cdf.csv"),
        ["popcount", "empirical_cdf", "gaussian_cdf"],
        cdf_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "popcount_samples.csv"),
        ["experiment", "label", "sample_index", "popcount"],
        popcount_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "summary_metrics.csv"),
        [
            "experiment",
            "label",
            "max_abs_bias",
            "mean_popcount",
            "sd_popcount",
            "max_abs_input_corr",
            "max_abs_acf",
            "mu_hat",
            "sigma_hat",
        ],
        summary_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "normalization_metrics.csv"),
        [
            "experiment",
            "label",
            "mu_hat",
            "sigma_hat",
            "delta_mu",
            "delta_sigma",
            "sum_squared_bit_bias",
            "centering_shift_z",
            "sd_popcount",
            "variance_ratio",
        ],
        normalization_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "popcount_distribution_metrics.csv"),
        [
            "experiment",
            "label",
            "mean_popcount",
            "sd_popcount",
            "skewness",
            "excess_kurtosis",
            "ks_distance",
            "wasserstein_distance",
            "ks_distance_binomial",
            "wasserstein_distance_binomial",
            "tail_error_z1",
            "tail_error_z2",
            "tail_error_z3",
        ],
        distribution_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "popcount_quantiles.csv"),
        [
            "experiment",
            "label",
            "probability",
            "empirical_quantile",
            "gaussian_quantile",
            "difference",
        ],
        quantile_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "popcount_qq.csv"),
        ["experiment", "label", "probability", "gaussian_quantile", "empirical_quantile"],
        qq_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "popcount_tail_curves.csv"),
        ["experiment", "label", "z_level", "empirical_tail", "gaussian_tail", "tail_error", "abs_tail_error"],
        tail_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "sequence_summary_metrics.csv"),
        [
            "sequence",
            "label",
            "mean_popcount",
            "sd_popcount",
            "lag1_correlation",
            "max_abs_acf",
            "runs_test_z",
            "tail_error_z2",
        ],
        sequence_summary_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "sequence_autocorrelation.csv"),
        ["sequence", "label", "lag", "acf", "abs_acf"],
        sequence_acf_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "sequence_scatter.csv"),
        ["sequence", "label", "step", "popcount_t", "popcount_t_plus_1"],
        sequence_scatter_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "block_popcount_correlations.csv"),
        ["experiment", "label", "left_block", "right_block", "correlation", "abs_correlation"],
        block_correlation_rows,
    )
    write_csv(
        os.path.join(GENERATED_DIR, "block_popcount_correlation_summary.csv"),
        ["experiment", "label", "mean_abs_block_correlation", "max_abs_block_correlation"],
        block_correlation_summary_rows,
    )

    with open(os.path.join(GENERATED_DIR, "study_metadata.txt"), "w", encoding="utf-8") as handle:
        handle.write(f"random_seed={RANDOM_SEED}\n")
        handle.write(f"n_samples={N_SAMPLES}\n")
        handle.write(f"max_lag={MAX_LAG}\n")
        handle.write(f"cdf_sample_size={CDF_SAMPLE_SIZE}\n")
        handle.write(f"qq_subsample={QQ_SUBSAMPLE}\n")
        handle.write(f"sequence_scatter_limit={SEQUENCE_SCATTER_LIMIT}\n")
        handle.write(f"bonferroni_z={BONFERRONI_Z:.8f}\n")
        handle.write(f"cdf_source={experiment_labels['exp3_random_ascii_32']}\n")
        handle.write(f"ks_distance={ks_distance:.6f}\n")
        handle.write(f"binomial_normal_ks_floor={binomial_normal_ks_floor:.6f}\n")

    with open(os.path.join(GENERATED_DIR, "summary_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrrrr}\n")
        handle.write("\\hline\n")
        handle.write("Experiment & Max $|\\hat p_i-0.5|$ & Mean Count & SD Count & Max $|r|$ & Max $|\\rho_h|$ \\\\\n")
        handle.write("\\hline\n")
        for slug, label, max_abs_bias, mean_popcount, sd_popcount, max_abs_input_corr, max_abs_acf, _mu_hat, _sigma_hat in summary_rows:
            short_label = label.split(": ", 1)[0]
            handle.write(
                f"{short_label} & {format_cell(max_abs_bias)} & {format_cell(mean_popcount)} & "
                f"{format_cell(sd_popcount)} & {format_cell(max_abs_input_corr or None)} & "
                f"{format_cell(max_abs_acf or None)} \\\\\n"
            )
        handle.write("\\hline\n")
        handle.write("\\end{tabular}\n")

    with open(os.path.join(GENERATED_DIR, "normalization_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrrrrr}\n")
        handle.write("\\hline\n")
        handle.write(
            "Experiment & $\\hat\\mu$ & $\\hat\\mu-128$ & $(\\hat\\mu-128)/8$ & "
            "$\\hat\\sigma$ & $s_S$ & $s_S^2/\\hat\\sigma^2$ \\\\\n"
        )
        handle.write("\\hline\n")
        for (
            slug,
            label,
            mu_hat,
            sigma_hat,
            delta_mu,
            _delta_sigma,
            _sum_squared_bit_bias,
            centering_shift_z,
            sd_popcount,
            variance_ratio,
        ) in normalization_rows:
            short_label = label.split(": ", 1)[0]
            handle.write(
                f"{short_label} & {format_cell(mu_hat)} & {format_cell(delta_mu)} & "
                f"{format_cell(centering_shift_z)} & {format_cell(sigma_hat)} & "
                f"{format_cell(sd_popcount)} & {format_cell(variance_ratio)} \\\\\n"
            )
        handle.write("\\hline\n")
        handle.write("\\end{tabular}\n")

    with open(os.path.join(GENERATED_DIR, "distribution_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrrrrrr}\n")
        handle.write("\\hline\n")
        handle.write(
            "Experiment & KS$_{\\mathcal N}$ & KS$_{\\mathrm{Bin}}$ & $W_1^{\\mathcal N}$ & "
            "$W_1^{\\mathrm{Bin}}$ & Skewness & Excess Kurtosis & $|\\Delta T_2|$ \\\\\n"
        )
        handle.write("\\hline\n")
        for (
            slug,
            label,
            _mean_popcount,
            _sd_popcount,
            popcount_skewness,
            popcount_excess_kurtosis,
            popcount_ks,
            popcount_wasserstein,
            popcount_ks_binomial,
            popcount_wasserstein_binomial,
            _tail_error_z1,
            tail_error_z2,
            _tail_error_z3,
        ) in distribution_rows:
            short_label = label.split(": ", 1)[0]
            handle.write(
                f"{short_label} & {format_cell(popcount_ks)} & {format_cell(popcount_ks_binomial)} & "
                f"{format_cell(popcount_wasserstein)} & {format_cell(popcount_wasserstein_binomial)} & "
                f"{format_cell(popcount_skewness)} & {format_cell(popcount_excess_kurtosis)} & "
                f"{format_cell(tail_error_z2)} \\\\\n"
            )
        handle.write("\\hline\n")
        handle.write("\\end{tabular}\n")

    with open(os.path.join(GENERATED_DIR, "block_popcount_correlation_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrr}\n")
        handle.write("\\hline\n")
        handle.write("Experiment & Mean block $|r|$ & Max block $|r|$ \\\\\n")
        handle.write("\\hline\n")
        for slug, label, mean_abs_corr, max_abs_corr in block_correlation_summary_rows:
            short_label = label.split(": ", 1)[0]
            handle.write(
                f"{short_label} & {format_cell(mean_abs_corr)} & {format_cell(max_abs_corr)} \\\\\n"
            )
        handle.write("\\hline\n")
        handle.write("\\end{tabular}\n")

    with open(os.path.join(GENERATED_DIR, "sequence_table.tex"), "w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrrrrr}\n")
        handle.write("\\hline\n")
        handle.write(
            "Sequence & Mean Count & SD Count & Lag-1 Corr & Max $|\\rho_h|$ & Runs $z$ & $|\\Delta T_2|$ \\\\\n"
        )
        handle.write("\\hline\n")
        for slug, label, mean_popcount, sd_popcount, lag1_corr, max_abs_acf, runs_z, tail_error_z2 in sequence_summary_rows:
            short_label = label.split(": ", 1)[0]
            handle.write(
                f"{short_label} & {format_cell(mean_popcount)} & {format_cell(sd_popcount)} & "
                f"{format_cell(lag1_corr)} & {format_cell(max_abs_acf)} & {format_cell(runs_z)} & "
                f"{format_cell(abs(tail_error_z2))} \\\\\n"
            )
        handle.write("\\hline\n")
        handle.write("\\end{tabular}\n")


if __name__ == "__main__":
    main()
