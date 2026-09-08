import csv
import math
import os
import traceback

import originpro as op


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "origin_exports")
LOG_PATH = os.path.join(BASE_DIR, "origin_render.log")
DONE_PATH = os.path.join(BASE_DIR, "origin_render_done.txt")
ERROR_PATH = os.path.join(BASE_DIR, "origin_render_error.txt")
PROJECT_PATH = os.path.join(BASE_DIR, "origin_render.opju")

BLUE = "#1F5AA6"
ROSE = "#C44536"
GOLD = "#B7791F"
MUTED = "#6B7280"
INK = "#1F2430"

# Origin PDF exports use a 300 dpi width argument, so convert the current
# publication figure widths from points to export pixels explicitly.
EXPORT_DPI = 300.0
POINTS_PER_INCH = 72.0
PUB_CDF_WIDTH_PX = round(532 * EXPORT_DPI / POINTS_PER_INCH)
PUB_QQ_WIDTH_PX = round(813 * EXPORT_DPI / POINTS_PER_INCH)
PUB_TAIL_WIDTH_PX = round(813 * EXPORT_DPI / POINTS_PER_INCH)
PUB_ACF_WIDTH_PX = round(777 * EXPORT_DPI / POINTS_PER_INCH)

SHORT_EXPERIMENT = {
    "Experiment 1.1: Sequential uint256 values": "Seq. uint256",
    "Experiment 1.2: Shifted uint256 values": "Shifted uint256",
    "Experiment 2.1: Prefixed sequential strings": "Prefixed seq. strings",
    "Experiment 2.2: Prefixed shifted strings": "Prefixed shifted strings",
    "Experiment 3.1: Random ASCII strings up to length 7": "ASCII strings <= 7",
    "Experiment 3.2: Random ASCII strings up to length 32": "ASCII strings <= 32",
}

SHORT_SEQUENCE = {
    "Sequence 1: repeated hashing from uint256 seed 1": "Seed = 1",
    "Sequence 2: repeated hashing from uint256 seed 2^128+1": "Seed = 2^128 + 1",
    "Sequence 3: repeated hashing from string seed Transaction Number: 1": "Seed = Transaction Number: 1",
    "Sequence 4: repeated hashing from string seed Sequence Seed: alpha-2026": "Seed = alpha-2026",
}


def reset_logs():
    for path in (LOG_PATH, DONE_PATH, ERROR_PATH):
        if os.path.exists(path):
            os.remove(path)


def log(message):
    text = str(message)
    with open(LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(text + "\n")
    print(text)


def finish_ok():
    with open(DONE_PATH, "w", encoding="utf-8") as handle:
        handle.write("ok\n")


def finish_error(exc):
    with open(ERROR_PATH, "w", encoding="utf-8") as handle:
        handle.write(str(exc) + "\n")
        handle.write(traceback.format_exc())


def read_rows(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_numeric_rows(filename, numeric_fields):
    rows = read_rows(filename)
    for row in rows:
        for field in numeric_fields:
            row[field] = float(row[field])
    return rows


def page_name(page):
    page.activate()
    return op.get_lt_str("%H")


def set_axis_titles(layer, x_title, y_title):
    layer.axis("x").title = x_title
    layer.axis("y").title = y_title


def apply_axis_limits(layer, x_from, x_to, y_from, y_to):
    layer.axis("x").sfrom = x_from
    layer.axis("x").sto = x_to
    layer.axis("y").sfrom = y_from
    layer.axis("y").sto = y_to


def save_graph(page, filename, width_px):
    path = os.path.join(OUT_DIR, filename)
    exported = page.save_fig(path, type="pdf", width=width_px)
    if not exported:
        raise RuntimeError(f"Origin failed to export {filename}")
    log(f"exported {exported}")
    return exported


def create_sheet(name, columns):
    wks = op.new_sheet("w", lname=name, hidden=True)
    for index, (long_name, axis, values) in enumerate(columns):
        wks.from_list(index, values, lname=long_name, axis=axis)
    return wks


def add_text(layer, text, x, y, color=INK, size=18):
    label = layer.add_label(text, x, y)
    label.color = color
    label.set_int("fontsize", size)
    return label


def style_line(plot, color, width=2, dash=None):
    plot.color = color
    plot.set_cmd(f"-w {width}")
    if dash is not None:
        plot.set_cmd(f"-d {dash}")


def create_cdf_figure():
    rows = read_numeric_rows(
        "popcount_cdf.csv",
        ["popcount", "empirical_cdf", "gaussian_cdf"],
    )
    wks = create_sheet(
        "Popcount CDF",
        [
            ("Popcount", "X", [row["popcount"] for row in rows]),
            ("Empirical CDF", "Y", [row["empirical_cdf"] for row in rows]),
            ("Gaussian CDF", "Y", [row["gaussian_cdf"] for row in rows]),
        ],
    )
    graph = op.new_graph(lname="BRA F6 Popcount CDF", template="line")
    layer = graph[0]
    empirical = layer.add_plot(wks, coly=1, colx=0, type="line")
    gaussian = layer.add_plot(wks, coly=2, colx=0, type="line")
    style_line(empirical, BLUE, width=3)
    style_line(gaussian, ROSE, width=2, dash=2)
    empirical.transparency = 0
    gaussian.transparency = 0
    layer.rescale()
    apply_axis_limits(layer, min(row["popcount"] for row in rows), max(row["popcount"] for row in rows), 0.0, 1.0)
    set_axis_titles(layer, "Popcount", "Cumulative probability")
    legend = layer.label("Legend")
    if legend:
        legend.text = "\\l(1) Empirical CDF\\n\\l(2) Gaussian CDF"
        legend.color = INK
    graph.lname = "Popcount CDF Against Gaussian Reference"
    save_graph(graph, "popcount_cdf_origin.pdf", PUB_CDF_WIDTH_PX)


def group_rows(rows, key):
    grouped = {}
    for row in rows:
        grouped.setdefault(row[key], []).append(row)
    return grouped


def merge_graphs(graph_names, rows, cols, out_name, width_px):
    if not graph_names:
        raise RuntimeError("merge_graphs called with no graph names")
    graph_expr = '"' + '"+char(10)$+"'.join(graph_names) + '"'
    cmd = f'merge_graph option:=specified graphs:={graph_expr} row:={rows} col:={cols} keep:=0;'
    log(f"merge command: {cmd}")
    op.lt_exec(cmd)
    merged_name = op.get_lt_str("%H")
    merged_graph = op.find_graph(merged_name)
    if not merged_graph:
        raise RuntimeError(f"Could not find merged graph after: {cmd}")
    save_graph(merged_graph, out_name, width_px)


def create_qq_panels():
    qq_rows = read_numeric_rows(
        "popcount_qq.csv",
        ["probability", "gaussian_quantile", "empirical_quantile"],
    )
    metric_rows = read_numeric_rows(
        "popcount_distribution_metrics.csv",
        ["ks_distance", "wasserstein_distance", "skewness", "excess_kurtosis", "tail_error_z2"],
    )
    metrics = {row["experiment"]: row for row in metric_rows}
    grouped = group_rows(qq_rows, "experiment")
    all_values = [row["gaussian_quantile"] for row in qq_rows] + [row["empirical_quantile"] for row in qq_rows]
    lo = min(all_values)
    hi = max(all_values)
    pad = (hi - lo) * 0.03
    graph_names = []
    for experiment, rows in grouped.items():
        label = SHORT_EXPERIMENT.get(rows[0]["label"], rows[0]["label"])
        wks = create_sheet(
            f"QQ {experiment}",
            [
                ("Gaussian quantile", "X", [row["gaussian_quantile"] for row in rows]),
                ("Empirical quantile", "Y", [row["empirical_quantile"] for row in rows]),
                ("Reference", "Y", [row["gaussian_quantile"] for row in rows]),
            ],
        )
        graph = op.new_graph(lname=f"QQ {experiment}", template="scatter")
        layer = graph[0]
        points = layer.add_plot(wks, coly=1, colx=0, type="scatter")
        points.color = BLUE
        points.symbol_kind = 2
        points.symbol_size = 6
        points.transparency = 35
        ref = layer.add_plot(wks, coly=2, colx=0, type="line")
        style_line(ref, ROSE, width=2, dash=2)
        layer.rescale()
        apply_axis_limits(layer, lo - pad, hi + pad, lo - pad, hi + pad)
        set_axis_titles(layer, "Gaussian quantile", "Empirical quantile")
        legend = layer.label("Legend")
        if legend:
            legend.remove()
        add_text(layer, label, lo + pad * 0.5, hi, size=16)
        if experiment in metrics:
            add_text(layer, f"KS = {metrics[experiment]['ks_distance']:.3f}", hi - 5 * pad, hi - 2 * pad, color=MUTED, size=14)
        graph_names.append(page_name(graph))
    merge_graphs(graph_names, 2, 3, "popcount_qq_panels_origin.pdf", PUB_QQ_WIDTH_PX)


def create_tail_panels():
    tail_rows = read_numeric_rows(
        "popcount_tail_curves.csv",
        ["z_level", "empirical_tail", "gaussian_tail", "tail_error", "abs_tail_error"],
    )
    metric_rows = read_numeric_rows(
        "popcount_distribution_metrics.csv",
        ["ks_distance", "wasserstein_distance", "skewness", "excess_kurtosis", "tail_error_z2"],
    )
    metrics = {row["experiment"]: row for row in metric_rows}
    grouped = group_rows(tail_rows, "experiment")
    graph_names = []
    for index, (experiment, rows) in enumerate(grouped.items()):
        label = SHORT_EXPERIMENT.get(rows[0]["label"], rows[0]["label"])
        y_min = min(min(row["empirical_tail"], row["gaussian_tail"]) for row in rows)
        y_max = max(max(row["empirical_tail"], row["gaussian_tail"]) for row in rows)
        wks = create_sheet(
            f"Tail {experiment}",
            [
                ("z level", "X", [row["z_level"] for row in rows]),
                ("Empirical tail", "Y", [row["empirical_tail"] for row in rows]),
                ("Gaussian tail", "Y", [row["gaussian_tail"] for row in rows]),
            ],
        )
        graph = op.new_graph(lname=f"Tail {experiment}", template="line")
        layer = graph[0]
        empirical = layer.add_plot(wks, coly=1, colx=0, type="line")
        gaussian = layer.add_plot(wks, coly=2, colx=0, type="line")
        style_line(empirical, BLUE, width=3)
        style_line(gaussian, ROSE, width=2, dash=2)
        empirical.symbol_kind = 2
        empirical.symbol_size = 5
        gaussian.symbol_kind = 3
        gaussian.symbol_size = 5
        layer.rescale()
        layer.yscale = 2
        apply_axis_limits(layer, min(row["z_level"] for row in rows), max(row["z_level"] for row in rows), y_min * 0.75, y_max * 1.2)
        set_axis_titles(layer, "z level", "Two-sided tail probability")
        legend = layer.label("Legend")
        if legend:
            if index == 0:
                legend.text = "\\l(1) Empirical\\n\\l(2) Gaussian"
                legend.color = INK
            else:
                legend.remove()
        add_text(layer, label, min(row["z_level"] for row in rows), y_max * 1.08, size=16)
        if experiment in metrics:
            add_text(layer, f"|Delta T2| = {metrics[experiment]['tail_error_z2']:.3f}", max(row["z_level"] for row in rows) - 0.8, y_max * 1.08, color=MUTED, size=14)
        graph_names.append(page_name(graph))
    merge_graphs(graph_names, 2, 3, "popcount_tail_panels_origin.pdf", PUB_TAIL_WIDTH_PX)


def create_sequence_acf_panels():
    acf_rows = read_numeric_rows(
        "sequence_autocorrelation.csv",
        ["lag", "acf", "abs_acf"],
    )
    summary_rows = read_numeric_rows(
        "sequence_summary_metrics.csv",
        ["mean_popcount", "sd_popcount", "lag1_correlation", "max_abs_acf", "runs_test_z", "tail_error_z2"],
    )
    summary = {row["sequence"]: row for row in summary_rows}
    grouped = group_rows(acf_rows, "sequence")
    acf_limit = max(max(abs(row["acf"]) for row in rows) for rows in grouped.values())
    acf_limit = max(acf_limit, 0.04)
    conf_band = 1.96 / math.sqrt(10000.0)
    graph_names = []
    for sequence, rows in grouped.items():
        label = SHORT_SEQUENCE.get(rows[0]["label"], rows[0]["label"])
        lags = [row["lag"] for row in rows]
        acf_values = [row["acf"] for row in rows]
        upper = [conf_band] * len(rows)
        lower = [-conf_band] * len(rows)
        zero = [0.0] * len(rows)
        wks = create_sheet(
            f"Sequence ACF {sequence}",
            [
                ("Lag", "X", lags),
                ("ACF", "Y", acf_values),
                ("Upper band", "Y", upper),
                ("Lower band", "Y", lower),
                ("Zero", "Y", zero),
            ],
        )
        graph = op.new_graph(lname=f"Sequence ACF {sequence}", template="line")
        layer = graph[0]
        acf_plot = layer.add_plot(wks, coly=1, colx=0, type="line")
        upper_plot = layer.add_plot(wks, coly=2, colx=0, type="line")
        lower_plot = layer.add_plot(wks, coly=3, colx=0, type="line")
        zero_plot = layer.add_plot(wks, coly=4, colx=0, type="line")
        style_line(acf_plot, BLUE, width=2)
        style_line(upper_plot, MUTED, width=1, dash=3)
        style_line(lower_plot, MUTED, width=1, dash=3)
        style_line(zero_plot, ROSE, width=1, dash=2)
        acf_plot.symbol_kind = 0
        upper_plot.symbol_kind = 0
        lower_plot.symbol_kind = 0
        zero_plot.symbol_kind = 0
        layer.rescale()
        apply_axis_limits(layer, min(lags), max(lags), -acf_limit * 1.08, acf_limit * 1.08)
        set_axis_titles(layer, "Lag", "Autocorrelation")
        legend = layer.label("Legend")
        if legend:
            legend.remove()
        add_text(layer, label, min(lags), acf_limit * 0.95, size=16)
        if sequence in summary:
            add_text(layer, f"lag-1 = {summary[sequence]['lag1_correlation']:.3f}", max(lags) - 10, acf_limit * 0.95, color=MUTED, size=14)
        graph_names.append(page_name(graph))
    merge_graphs(graph_names, 2, 2, "sequence_acf_panels_origin.pdf", PUB_ACF_WIDTH_PX)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    reset_logs()
    targets_env = os.environ.get("ORIGIN_TARGETS", "").strip()
    if targets_env:
        targets = {target.strip() for target in targets_env.split(",") if target.strip()}
    else:
        targets = {"BRA-F6", "BRA-F7", "BRA-F8", "BRA-F9"}

    log(f"base_dir={BASE_DIR}")
    log(f"targets={sorted(targets)}")

    if "BRA-F6" in targets:
        create_cdf_figure()
    if "BRA-F7" in targets:
        create_qq_panels()
    if "BRA-F8" in targets:
        create_tail_panels()
    if "BRA-F9" in targets:
        create_sequence_acf_panels()

    op.save(PROJECT_PATH)
    log(f"saved project to {PROJECT_PATH}")
    finish_ok()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        finish_error(exc)
        raise
