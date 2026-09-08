uniformity <- read.csv("../NumericalStudy/generated/uniformity.csv", stringsAsFactors = FALSE)
pairwise <- read.csv("../NumericalStudy/generated/pairwise_metrics.csv", stringsAsFactors = FALSE)
input_corr <- read.csv("../NumericalStudy/generated/input_correlations.csv", stringsAsFactors = FALSE)
acf_data <- read.csv("../NumericalStudy/generated/autocorrelation.csv", stringsAsFactors = FALSE)
cdf_data <- read.csv("../NumericalStudy/generated/popcount_cdf.csv", stringsAsFactors = FALSE)
popcount_samples <- read.csv("../NumericalStudy/generated/popcount_samples.csv", stringsAsFactors = FALSE)
normalization <- read.csv("../NumericalStudy/generated/normalization_metrics.csv", stringsAsFactors = FALSE)
qq_data <- read.csv("../NumericalStudy/generated/popcount_qq.csv", stringsAsFactors = FALSE)
tail_data <- read.csv("../NumericalStudy/generated/popcount_tail_curves.csv", stringsAsFactors = FALSE)
distribution_metrics <- read.csv("../NumericalStudy/generated/popcount_distribution_metrics.csv", stringsAsFactors = FALSE)
sequence_acf <- read.csv("../NumericalStudy/generated/sequence_autocorrelation.csv", stringsAsFactors = FALSE)
sequence_scatter <- read.csv("../NumericalStudy/generated/sequence_scatter.csv", stringsAsFactors = FALSE)
sequence_summary <- read.csv("../NumericalStudy/generated/sequence_summary_metrics.csv", stringsAsFactors = FALSE)
cross_vm_summary <- read.csv("../NumericalStudy/generated/cross_vm_summary_metrics.csv", stringsAsFactors = FALSE)

dir.create("figures", showWarnings = FALSE)

ink <- "#1F2430"
muted <- "#6B7280"
grid_col <- "#D9DDE3"
blue <- "#1F5AA6"
teal <- "#0F766E"
gold <- "#B7791F"
rose <- "#C44536"
violet <- "#6D5BD0"
fill_blue <- grDevices::adjustcolor(blue, alpha.f = 0.14)
fill_gold <- grDevices::adjustcolor(gold, alpha.f = 0.18)
fill_rose <- grDevices::adjustcolor(rose, alpha.f = 0.18)
point_blue <- grDevices::adjustcolor(blue, alpha.f = 0.65)

short_experiment <- function(label) {
  mapping <- c(
    "Experiment 1.1: Sequential uint256 values" = "Seq. uint256",
    "Experiment 1.2: Shifted uint256 values" = "Shifted uint256",
    "Experiment 2.1: Prefixed sequential strings" = "Prefixed seq. strings",
    "Experiment 2.2: Prefixed shifted strings" = "Prefixed shifted strings",
    "Experiment 3.1: Random ASCII strings up to length 7" = "ASCII strings <= 7",
    "Experiment 3.2: Random ASCII strings up to length 32" = "ASCII strings <= 32"
  )
  ifelse(label %in% names(mapping), mapping[label], label)
}

short_sequence <- function(label) {
  mapping <- c(
    "Sequence 1: repeated hashing from uint256 seed 1" = "Seed = 1",
    "Sequence 2: repeated hashing from uint256 seed 2^128+1" = "Seed = 2^128 + 1",
    "Sequence 3: repeated hashing from string seed Transaction Number: 1" = "Seed = `Transaction Number: 1`",
    "Sequence 4: repeated hashing from string seed Sequence Seed: alpha-2026" = "Seed = `alpha-2026`"
  )
  ifelse(label %in% names(mapping), mapping[label], label)
}

short_vm <- function(label) {
  mapping <- c(
    "Keccak-256" = "Keccak-256",
    "SHA-256" = "SHA-256",
    "Fair-bit control (256-bit)" = "Control 256-bit",
    "Fair-bit control (512-bit)" = "Control 512-bit"
  )
  ifelse(label %in% names(mapping), mapping[label], label)
}

fmt_num <- function(x) {
  ifelse(abs(x) < 0.01, formatC(x, format = "e", digits = 2), formatC(x, format = "f", digits = 3))
}

open_pdf <- function(path, width, height) {
  pdf(path, width = width, height = height, family = "Helvetica", useDingbats = FALSE)
}

panel_frame <- function(xlim, ylim, xlab, ylab, x_ticks = NULL, y_ticks = NULL, x_labels = NULL, y_labels = NULL) {
  plot.new()
  plot.window(xlim = xlim, ylim = ylim, xaxs = "r", yaxs = "r")
  if (!is.null(x_ticks)) {
    abline(v = x_ticks, col = grid_col, lty = 1, lwd = 0.8)
  }
  if (!is.null(y_ticks)) {
    abline(h = y_ticks, col = grid_col, lty = 1, lwd = 0.8)
  }
  axis(1, at = x_ticks, labels = x_labels, lwd = 0, lwd.ticks = 0.7, col.ticks = muted, col.axis = ink, cex.axis = 0.82)
  axis(2, at = y_ticks, labels = y_labels, las = 1, lwd = 0, lwd.ticks = 0.7, col.ticks = muted, col.axis = ink, cex.axis = 0.82)
  box(bty = "l", col = muted, lwd = 1)
  mtext(xlab, side = 1, line = 2.5, cex = 0.9, col = ink)
  mtext(ylab, side = 2, line = 2.8, cex = 0.9, col = ink)
}

lollipop_panel <- function(values, labels, color, main, xlab) {
  ord <- rev(seq_along(values))
  values <- values[ord]
  labels <- labels[ord]
  n <- length(values)
  max_val <- max(values)
  x_max <- max_val * 1.25
  x_ticks <- pretty(c(0, x_max), n = 4)
  y_ticks <- seq_len(n)

  panel_frame(
    xlim = c(0, x_max),
    ylim = c(0.5, n + 0.5),
    xlab = xlab,
    ylab = "",
    x_ticks = x_ticks,
    y_ticks = y_ticks,
    y_labels = labels
  )

  segments(0, y_ticks, values, y_ticks, col = grDevices::adjustcolor(color, alpha.f = 0.55), lwd = 2.5)
  points(values, y_ticks, pch = 21, bg = color, col = "white", cex = 1.2)
  text(values + x_max * 0.03, y_ticks, labels = fmt_num(values), pos = 4, cex = 0.74, col = ink, xpd = NA)
  title(main = main, line = 0.6, cex.main = 1.0, col.main = ink)
}

open_pdf("figures/cross_vm_overview_pub.pdf", width = 11.5, height = 8.2)
par(mfrow = c(2, 2), mar = c(4.2, 7.8, 2.8, 1.2), oma = c(0.2, 0.2, 0.2, 0.2))
vm_labels <- short_vm(cross_vm_summary$label)
lollipop_panel(cross_vm_summary$max_abs_delta_mu, vm_labels, blue, "Centering Error", expression(max(abs(hat(mu) - n / 2))))
lollipop_panel(cross_vm_summary$max_abs_delta_sigma, vm_labels, teal, "Scaling Deviation", expression(max(abs(hat(sigma) - sqrt(n) / 2))))
lollipop_panel(cross_vm_summary$max_ks_distance, vm_labels, rose, "Gaussian Fit", "Worst KS distance")
lollipop_panel(cross_vm_summary$max_abs_tail_error_z2, vm_labels, gold, "Tail Error at z = 2", expression(max(abs(Delta * T[2]))))
dev.off()

open_pdf("figures/cross_vm_dependence_pub.pdf", width = 11.5, height = 8.2)
par(mfrow = c(2, 2), mar = c(4.2, 7.8, 2.8, 1.2), oma = c(0.2, 0.2, 0.2, 0.2))
lollipop_panel(cross_vm_summary$max_abs_input_corr, vm_labels, blue, "Input-Output Dependence", "Worst |input corr.|")
lollipop_panel(cross_vm_summary$max_abs_bit_acf, vm_labels, rose, "Within-Output Lag Structure", "Worst bit-level |ACF|")
lollipop_panel(cross_vm_summary$max_abs_lag1, vm_labels, teal, "Sequence Lag-1 Dependence", "Worst |lag-1 corr.|")
lollipop_panel(cross_vm_summary$max_abs_sequence_acf, vm_labels, gold, "Repeated-Sequence Dependence", "Worst sequence |ACF|")
dev.off()

open_pdf("figures/uniformity_panels_pub.pdf", width = 11.3, height = 7.9)
par(mfrow = c(2, 3), mar = c(3.5, 3.8, 2.7, 1.0), oma = c(0.2, 0.2, 0.4, 0.2))
for (experiment in unique(uniformity$experiment)) {
  subset <- uniformity[uniformity$experiment == experiment, ]
  y_ticks <- seq(0.46, 0.54, by = 0.02)
  panel_frame(
    xlim = range(subset$bit_index),
    ylim = c(0.46, 0.54),
    xlab = "Bit index",
    ylab = "Estimated P(bit = 1)",
    x_ticks = c(0, 64, 128, 192, 255),
    y_ticks = y_ticks
  )
  polygon(
    c(subset$bit_index, rev(subset$bit_index)),
    c(subset$lower, rev(subset$upper)),
    col = fill_gold,
    border = NA
  )
  lines(subset$bit_index, subset$mean, col = blue, lwd = 1.7)
  abline(h = 0.5, lty = 2, lwd = 1.1, col = rose)
  title(main = short_experiment(subset$label[1]), line = 0.4, cex.main = 0.95, col.main = ink)
  max_bias <- max(abs(subset$mean - 0.5))
  mtext(sprintf("max |p-hat - 0.5| = %.3f", max_bias), side = 3, line = -0.9, adj = 1, cex = 0.73, col = muted)
}
dev.off()

open_pdf("figures/pairwise_metrics_pub.pdf", width = 11.0, height = 4.2)
par(mfrow = c(1, 3), mar = c(4.0, 4.0, 2.7, 0.8))
plot_density_panel <- function(values, fill_col, line_col, main, xlab, reference = NULL) {
  d <- density(values)
  x_ticks <- pretty(range(d$x), n = 5)
  y_ticks <- pretty(c(0, max(d$y)), n = 4)
  panel_frame(range(d$x), c(0, max(d$y) * 1.05), xlab, "Density", x_ticks = x_ticks, y_ticks = y_ticks)
  polygon(c(d$x, rev(d$x)), c(d$y, rep(0, length(d$y))), col = fill_col, border = NA)
  lines(d$x, d$y, col = line_col, lwd = 2.0)
  if (!is.null(reference)) {
    abline(v = reference, col = muted, lty = 2, lwd = 1.2)
  }
  title(main = main, line = 0.5, cex.main = 0.98, col.main = ink)
}
plot_density_panel(pairwise$rogers_tanimoto, fill_blue, blue, "Rogers-Tanimoto", "Similarity", reference = 1 / 3)
plot_density_panel(pairwise$phi_correlation, fill_rose, rose, "Phi Correlation", "Correlation", reference = 0)
plot_density_panel(pairwise$sokal_michener, fill_gold, gold, "Sokal-Michener", "Similarity", reference = 0.5)
dev.off()

open_pdf("figures/input_correlation_panels_pub.pdf", width = 10.8, height = 8.0)
par(mfrow = c(2, 2), mar = c(3.4, 3.8, 2.7, 1.0), oma = c(0.2, 0.2, 0.4, 0.2))
max_corr <- max(abs(input_corr$correlation))
for (experiment in unique(input_corr$experiment)) {
  subset <- input_corr[input_corr$experiment == experiment, ]
  y_ticks <- pretty(c(-max_corr, max_corr), n = 5)
  panel_frame(
    xlim = range(subset$bit_index),
    ylim = c(-max_corr, max_corr),
    xlab = "Bit index",
    ylab = "Pearson r",
    x_ticks = c(0, 64, 128, 192, 255),
    y_ticks = y_ticks
  )
  lines(subset$bit_index, subset$correlation, col = blue, lwd = 1.5)
  abline(h = 0, lty = 2, lwd = 1.1, col = rose)
  title(main = short_experiment(subset$label[1]), line = 0.4, cex.main = 0.95, col.main = ink)
  mtext(sprintf("max |r| = %.3f", max(abs(subset$correlation))), side = 3, line = -0.9, adj = 1, cex = 0.73, col = muted)
}
dev.off()

open_pdf("figures/autocorrelation_panels_pub.pdf", width = 10.8, height = 8.0)
par(mfrow = c(2, 2), mar = c(3.4, 3.8, 2.7, 1.0), oma = c(0.2, 0.2, 0.4, 0.2))
max_acf <- max(acf_data$max_abs_acf)
for (i in seq_along(unique(acf_data$experiment))) {
  experiment <- unique(acf_data$experiment)[i]
  subset <- acf_data[acf_data$experiment == experiment, ]
  y_ticks <- pretty(c(0, max_acf), n = 4)
  panel_frame(
    xlim = range(subset$lag),
    ylim = c(0, max_acf),
    xlab = "Lag",
    ylab = "|ACF| summary",
    x_ticks = c(1, 10, 20, 30),
    y_ticks = y_ticks
  )
  lines(subset$lag, subset$max_abs_acf, col = rose, lwd = 1.8)
  lines(subset$lag, subset$mean_abs_acf, col = blue, lwd = 1.8, lty = 1)
  title(main = short_experiment(subset$label[1]), line = 0.4, cex.main = 0.95, col.main = ink)
  if (i == 1) {
    legend("topright", legend = c("Max |ACF|", "Mean |ACF|"), col = c(rose, blue), lty = 1, lwd = 1.8, bty = "n", cex = 0.78, text.col = ink)
  }
}
dev.off()

open_pdf("figures/normalization_errors_pub.pdf", width = 10.4, height = 4.8)
par(mfrow = c(1, 2), mar = c(4.2, 7.8, 2.8, 1.0), oma = c(0.2, 0.2, 0.2, 0.2))
norm_labels <- short_experiment(normalization$label)
lollipop_panel(normalization$delta_mu, norm_labels, blue, "Centering Relative to 128", expression(hat(mu) - 128))
lollipop_panel(abs(normalization$delta_sigma), norm_labels, teal, "Scaling Deviation Relative to 8", expression(abs(hat(sigma) - 8)))
dev.off()

open_pdf("figures/popcount_cdf_pub.pdf", width = 7.4, height = 5.2)
x_ticks <- pretty(range(cdf_data$popcount), n = 5)
y_ticks <- seq(0, 1, by = 0.2)
panel_frame(range(cdf_data$popcount), c(0, 1), "Popcount", "Cumulative probability", x_ticks = x_ticks, y_ticks = y_ticks)
lines(cdf_data$popcount, cdf_data$empirical_cdf, type = "s", col = blue, lwd = 1.8)
lines(cdf_data$popcount, cdf_data$gaussian_cdf, col = rose, lwd = 1.8, lty = 2)
legend("bottomright", legend = c("Empirical CDF", "Gaussian CDF"), col = c(blue, rose), lty = c(1, 2), lwd = 1.8, bty = "n", cex = 0.85, text.col = ink)
title(main = "Popcount CDF Against Gaussian Reference", line = 0.6, cex.main = 1.0, col.main = ink)
dev.off()

open_pdf("figures/popcount_qq_panels_pub.pdf", width = 11.3, height = 7.9)
par(mfrow = c(2, 3), mar = c(3.5, 3.8, 2.7, 1.0), oma = c(0.2, 0.2, 0.4, 0.2))
qq_low <- min(c(qq_data$gaussian_quantile, qq_data$empirical_quantile))
qq_high <- max(c(qq_data$gaussian_quantile, qq_data$empirical_quantile))
for (experiment in unique(qq_data$experiment)) {
  subset <- qq_data[qq_data$experiment == experiment, ]
  metric <- distribution_metrics[distribution_metrics$experiment == experiment, ]
  ticks <- pretty(c(qq_low, qq_high), n = 4)
  panel_frame(c(qq_low, qq_high), c(qq_low, qq_high), "Gaussian quantile", "Empirical quantile", x_ticks = ticks, y_ticks = ticks)
  points(subset$gaussian_quantile, subset$empirical_quantile, pch = 16, col = point_blue, cex = 0.45)
  abline(0, 1, lty = 2, lwd = 1.2, col = rose)
  title(main = short_experiment(subset$label[1]), line = 0.4, cex.main = 0.95, col.main = ink)
  if (nrow(metric) == 1) {
    mtext(sprintf("KS = %.3f", metric$ks_distance), side = 3, line = -0.9, adj = 1, cex = 0.73, col = muted)
  }
}
dev.off()

open_pdf("figures/popcount_tail_panels_pub.pdf", width = 11.3, height = 7.9)
par(mfrow = c(2, 3), mar = c(3.5, 3.8, 2.7, 1.0), oma = c(0.2, 0.2, 0.4, 0.2))
for (experiment in unique(tail_data$experiment)) {
  subset <- tail_data[tail_data$experiment == experiment, ]
  metric <- distribution_metrics[distribution_metrics$experiment == experiment, ]
  y_min <- min(c(subset$empirical_tail, subset$gaussian_tail))
  y_max <- max(c(subset$empirical_tail, subset$gaussian_tail))
  plot(
    subset$z_level,
    subset$empirical_tail,
    type = "n",
    log = "y",
    xlim = range(subset$z_level),
    ylim = c(y_min, y_max),
    xlab = "z threshold",
    ylab = "Two-sided tail probability",
    axes = FALSE,
    xaxs = "r",
    yaxs = "r"
  )
  abline(v = pretty(range(subset$z_level), n = 4), col = grid_col, lwd = 0.8)
  abline(h = c(0.001, 0.01, 0.1, 1), col = grid_col, lwd = 0.8)
  axis(1, at = pretty(range(subset$z_level), n = 4), lwd = 0, lwd.ticks = 0.7, col.ticks = muted, col.axis = ink, cex.axis = 0.82)
  axis(2, at = c(0.001, 0.01, 0.1, 1), labels = c("0.001", "0.01", "0.1", "1"), las = 1, lwd = 0, lwd.ticks = 0.7, col.ticks = muted, col.axis = ink, cex.axis = 0.82)
  box(bty = "l", col = muted, lwd = 1)
  lines(subset$z_level, subset$empirical_tail, col = blue, lwd = 1.8)
  points(subset$z_level, subset$empirical_tail, pch = 16, cex = 0.55, col = blue)
  lines(subset$z_level, subset$gaussian_tail, col = rose, lwd = 1.8, lty = 2)
  points(subset$z_level, subset$gaussian_tail, pch = 17, cex = 0.6, col = rose)
  title(main = short_experiment(subset$label[1]), line = 0.4, cex.main = 0.95, col.main = ink)
  if (nrow(metric) == 1) {
    mtext(sprintf("|Delta T2| = %.3f", metric$tail_error_z2), side = 3, line = -0.9, adj = 1, cex = 0.73, col = muted)
  }
  if (experiment == unique(tail_data$experiment)[1]) {
    legend("topright", legend = c("Empirical", "Gaussian"), col = c(blue, rose), pch = c(16, 17), lty = c(1, 2), lwd = 1.8, bty = "n", cex = 0.75, text.col = ink)
  }
}
dev.off()

open_pdf("figures/integer_scaled_output_pub.pdf", width = 7.4, height = 5.2)
integer_subset <- popcount_samples[popcount_samples$experiment == "exp3_random_ascii_32", ]
integer_output <- 125 * integer_subset$popcount - 16000
mass_table <- table(integer_output)
mass_x <- as.numeric(names(mass_table))
mass_y <- as.numeric(mass_table) / length(integer_output)
y_ticks <- pretty(c(0, max(mass_y)), n = 5)
x_ticks <- seq(-4000, 4000, by = 1000)
panel_frame(
  range(mass_x),
  c(0, max(mass_y) * 1.12),
  expression(Z[256,1000]),
  "Empirical probability mass",
  x_ticks = x_ticks,
  y_ticks = y_ticks
)
segments(mass_x, 0, mass_x, mass_y, col = grDevices::adjustcolor(blue, alpha.f = 0.70), lwd = 1.4)
points(mass_x, mass_y, pch = 16, cex = 0.45, col = blue)
abline(v = 0, lty = 2, lwd = 1.0, col = rose)
title(main = "Integer-Scaled Output Distribution", line = 0.6, cex.main = 1.0, col.main = ink)
mtext("Representative family: random ASCII strings <= 32; lattice spacing = 125", side = 3, line = -1.0, adj = 1, cex = 0.74, col = muted)
dev.off()

open_pdf("figures/sequence_acf_panels_pub.pdf", width = 10.8, height = 8.0)
par(mfrow = c(2, 2), mar = c(3.4, 3.8, 2.7, 1.0), oma = c(0.2, 0.2, 0.4, 0.2))
acf_limit <- max(abs(sequence_acf$acf))
acf_limit <- max(acf_limit, 0.04)
conf_band <- 1.96 / sqrt(10000)
for (sequence_name in unique(sequence_acf$sequence)) {
  subset <- sequence_acf[sequence_acf$sequence == sequence_name, ]
  summary_row <- sequence_summary[sequence_summary$sequence == sequence_name, ]
  y_ticks <- pretty(c(-acf_limit, acf_limit), n = 5)
  panel_frame(
    xlim = range(subset$lag),
    ylim = c(-acf_limit, acf_limit),
    xlab = "Lag",
    ylab = "Autocorrelation",
    x_ticks = c(1, 10, 20, 30),
    y_ticks = y_ticks
  )
  segments(subset$lag, 0, subset$lag, subset$acf, col = blue, lwd = 1.6)
  abline(h = 0, lty = 2, lwd = 1.0, col = rose)
  abline(h = c(-conf_band, conf_band), lty = 3, lwd = 1.0, col = muted)
  title(main = short_sequence(subset$label[1]), line = 0.4, cex.main = 0.92, col.main = ink)
  if (nrow(summary_row) == 1) {
    mtext(sprintf("lag-1 = %.3f", summary_row$lag1_correlation), side = 3, line = -0.9, adj = 1, cex = 0.73, col = muted)
  }
}
dev.off()

open_pdf("figures/sequence_scatter_panels_pub.pdf", width = 10.8, height = 8.0)
par(mfrow = c(2, 2), mar = c(3.4, 3.8, 2.7, 1.0), oma = c(0.2, 0.2, 0.4, 0.2))
scatter_lim <- range(c(sequence_scatter$popcount_t, sequence_scatter$popcount_t_plus_1))
for (sequence_name in unique(sequence_scatter$sequence)) {
  subset <- sequence_scatter[sequence_scatter$sequence == sequence_name, ]
  summary_row <- sequence_summary[sequence_summary$sequence == sequence_name, ]
  ticks <- pretty(scatter_lim, n = 4)
  panel_frame(scatter_lim, scatter_lim, expression(S[t]), expression(S[t+1]), x_ticks = ticks, y_ticks = ticks)
  points(subset$popcount_t, subset$popcount_t_plus_1, pch = 16, cex = 0.33, col = grDevices::adjustcolor(blue, alpha.f = 0.18))
  abline(0, 1, lty = 2, lwd = 1.1, col = rose)
  title(main = short_sequence(subset$label[1]), line = 0.4, cex.main = 0.92, col.main = ink)
  if (nrow(summary_row) == 1) {
    mtext(sprintf("lag-1 = %.3f", summary_row$lag1_correlation), side = 3, line = -0.9, adj = 1, cex = 0.73, col = muted)
  }
}
dev.off()
