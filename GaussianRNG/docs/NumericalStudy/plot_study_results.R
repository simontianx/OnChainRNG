uniformity <- read.csv("generated/uniformity.csv", stringsAsFactors = FALSE)
pairwise <- read.csv("generated/pairwise_metrics.csv", stringsAsFactors = FALSE)
input_corr <- read.csv("generated/input_correlations.csv", stringsAsFactors = FALSE)
acf_data <- read.csv("generated/autocorrelation.csv", stringsAsFactors = FALSE)
cdf_data <- read.csv("generated/popcount_cdf.csv", stringsAsFactors = FALSE)
normalization <- read.csv("generated/normalization_metrics.csv", stringsAsFactors = FALSE)
qq_data <- read.csv("generated/popcount_qq.csv", stringsAsFactors = FALSE)
tail_data <- read.csv("generated/popcount_tail_curves.csv", stringsAsFactors = FALSE)
sequence_acf <- read.csv("generated/sequence_autocorrelation.csv", stringsAsFactors = FALSE)
sequence_scatter <- read.csv("generated/sequence_scatter.csv", stringsAsFactors = FALSE)

dir.create("figures", showWarnings = FALSE)

palette_blue <- "#0F4C81"
palette_red <- "#C84C1A"
palette_gold <- "#C79A00"
palette_gray <- "#555555"
palette_green <- "#2E7D32"
panel_fill <- "#E9EEF3"

short_label <- function(label) {
  sub(":.*$", "", label)
}

pdf("figures/uniformity_panels.pdf", width = 12, height = 8)
par(mfrow = c(2, 3), mar = c(3.5, 3.5, 2.8, 1), oma = c(0, 0, 1, 0))
for (experiment in unique(uniformity$experiment)) {
  subset <- uniformity[uniformity$experiment == experiment, ]
  plot(
    subset$bit_index,
    subset$mean,
    type = "l",
    lwd = 1.5,
    col = palette_blue,
    ylim = c(0.46, 0.54),
    xlab = "Bit Index",
    ylab = "Probability",
    main = subset$label[1]
  )
  lines(subset$bit_index, subset$upper, col = palette_gold, lwd = 1)
  lines(subset$bit_index, subset$lower, col = palette_gold, lwd = 1)
  abline(h = 0.5, lty = 2, col = palette_red, lwd = 1.2)
}
mtext("Bit-wise Estimates with Bonferroni Bands", outer = TRUE, line = -1.2, cex = 1.1)
dev.off()

pdf("figures/pairwise_metrics.pdf", width = 12, height = 4)
par(mfrow = c(1, 3), mar = c(4, 4, 2.8, 1))
hist(
  pairwise$rogers_tanimoto,
  breaks = 50,
  col = palette_blue,
  border = "white",
  main = "Rogers-Tanimoto",
  xlab = "Similarity"
)
hist(
  pairwise$phi_correlation,
  breaks = 50,
  col = palette_red,
  border = "white",
  main = "Phi Correlation",
  xlab = "Correlation"
)
hist(
  pairwise$sokal_michener,
  breaks = 50,
  col = palette_gold,
  border = "white",
  main = "Sokal-Michener",
  xlab = "Similarity"
)
dev.off()

pdf("figures/input_correlation_panels.pdf", width = 10, height = 8)
par(mfrow = c(2, 2), mar = c(3.5, 3.5, 2.8, 1), oma = c(0, 0, 1, 0))
max_corr <- max(abs(input_corr$correlation))
for (experiment in unique(input_corr$experiment)) {
  subset <- input_corr[input_corr$experiment == experiment, ]
  plot(
    subset$bit_index,
    subset$correlation,
    type = "l",
    lwd = 1.2,
    col = palette_blue,
    ylim = c(-max_corr, max_corr),
    xlab = "Bit Index",
    ylab = "Pearson r",
    main = subset$label[1]
  )
  abline(h = 0, lty = 2, col = palette_red, lwd = 1.2)
}
mtext("Input-Bit Correlation Across Sequential Experiments", outer = TRUE, line = -1.2, cex = 1.1)
dev.off()

pdf("figures/autocorrelation_panels.pdf", width = 10, height = 8)
par(mfrow = c(2, 2), mar = c(3.5, 3.5, 2.8, 1), oma = c(0, 0, 1, 0))
max_acf <- max(acf_data$max_abs_acf)
for (experiment in unique(acf_data$experiment)) {
  subset <- acf_data[acf_data$experiment == experiment, ]
  plot(
    subset$lag,
    subset$max_abs_acf,
    type = "l",
    lwd = 1.5,
    col = palette_red,
    ylim = c(0, max_acf),
    xlab = "Lag",
    ylab = "Autocorrelation",
    main = subset$label[1]
  )
  lines(subset$lag, subset$mean_abs_acf, col = palette_blue, lwd = 1.5)
  legend(
    "topright",
    legend = c("Max |ACF|", "Mean |ACF|"),
    col = c(palette_red, palette_blue),
    lty = 1,
    lwd = 1.5,
    bty = "n",
    cex = 0.85
  )
}
mtext("Autocorrelation Summary up to Lag 30", outer = TRUE, line = -1.2, cex = 1.1)
dev.off()

pdf("figures/popcount_cdf.pdf", width = 7, height = 5)
plot(
  cdf_data$popcount,
  cdf_data$empirical_cdf,
  type = "s",
  lwd = 1.5,
  col = palette_gray,
  xlab = "Count of 1s",
  ylab = "Cumulative Probability",
  main = "Empirical CDF vs Gaussian Approximation"
)
lines(cdf_data$popcount, cdf_data$gaussian_cdf, col = palette_red, lwd = 2)
legend(
  "bottomright",
  legend = c("Empirical CDF", "Gaussian CDF"),
  col = c(palette_gray, palette_red),
  lty = 1,
  lwd = c(1.5, 2),
  bty = "n"
)
dev.off()

pdf("figures/normalization_errors.pdf", width = 10, height = 4.5)
par(mfrow = c(1, 2), mar = c(5, 4, 2.8, 1))
x_positions <- seq_len(nrow(normalization))
labels <- short_label(normalization$label)
plot(
  x_positions,
  normalization$delta_mu,
  type = "h",
  lwd = 5,
  lend = "butt",
  col = palette_blue,
  xaxt = "n",
  xlab = "",
  ylab = expression(hat(mu) - 128),
  main = "Mean Normalization Error"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_red, lwd = 1.2)
plot(
  x_positions,
  normalization$delta_sigma,
  type = "h",
  lwd = 5,
  lend = "butt",
  col = palette_green,
  xaxt = "n",
  xlab = "",
  ylab = expression(hat(sigma) - 8),
  main = "SD Normalization Error"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_red, lwd = 1.2)
dev.off()

pdf("figures/popcount_qq_panels.pdf", width = 12, height = 8)
par(mfrow = c(2, 3), mar = c(3.5, 3.5, 2.8, 1), oma = c(0, 0, 1, 0))
for (experiment in unique(qq_data$experiment)) {
  subset <- qq_data[qq_data$experiment == experiment, ]
  low <- min(subset$gaussian_quantile, subset$empirical_quantile)
  high <- max(subset$gaussian_quantile, subset$empirical_quantile)
  plot(
    subset$gaussian_quantile,
    subset$empirical_quantile,
    pch = 16,
    cex = 0.45,
    col = palette_blue,
    bg = panel_fill,
    xlab = "Gaussian Quantile",
    ylab = "Empirical Quantile",
    main = subset$label[1],
    xlim = c(low, high),
    ylim = c(low, high)
  )
  abline(0, 1, lty = 2, col = palette_red, lwd = 1.3)
}
mtext("QQ Diagnostics for Popcount Against N(128, 8^2)", outer = TRUE, line = -1.2, cex = 1.1)
dev.off()

pdf("figures/popcount_tail_panels.pdf", width = 12, height = 8)
par(mfrow = c(2, 3), mar = c(3.5, 3.5, 2.8, 1), oma = c(0, 0, 1, 0))
for (experiment in unique(tail_data$experiment)) {
  subset <- tail_data[tail_data$experiment == experiment, ]
  ymax <- max(subset$empirical_tail, subset$gaussian_tail)
  plot(
    subset$z_level,
    subset$empirical_tail,
    type = "o",
    pch = 16,
    lwd = 1.5,
    col = palette_blue,
    ylim = c(0, ymax),
    xlab = "z Threshold",
    ylab = "Two-sided Tail Probability",
    main = subset$label[1]
  )
  lines(subset$z_level, subset$gaussian_tail, type = "o", pch = 17, lwd = 1.5, col = palette_red)
  legend(
    "topright",
    legend = c("Empirical", "Gaussian"),
    col = c(palette_blue, palette_red),
    pch = c(16, 17),
    lty = 1,
    lwd = 1.5,
    bty = "n",
    cex = 0.8
  )
}
mtext("Tail Probability Diagnostics for |(S-128)/8|", outer = TRUE, line = -1.2, cex = 1.1)
dev.off()

pdf("figures/sequence_acf_panels.pdf", width = 10, height = 8)
par(mfrow = c(2, 2), mar = c(3.5, 3.5, 2.8, 1), oma = c(0, 0, 1, 0))
max_seq_acf <- max(sequence_acf$abs_acf)
for (sequence_name in unique(sequence_acf$sequence)) {
  subset <- sequence_acf[sequence_acf$sequence == sequence_name, ]
  plot(
    subset$lag,
    subset$acf,
    type = "h",
    lwd = 2,
    col = palette_blue,
    ylim = c(-max_seq_acf, max_seq_acf),
    xlab = "Lag",
    ylab = "Autocorrelation",
    main = subset$label[1]
  )
  abline(h = 0, lty = 2, col = palette_red, lwd = 1.2)
}
mtext("Repeated-Hash Sequence Autocorrelation of Popcount", outer = TRUE, line = -1.2, cex = 1.1)
dev.off()

pdf("figures/sequence_scatter_panels.pdf", width = 10, height = 8)
par(mfrow = c(2, 2), mar = c(3.5, 3.5, 2.8, 1), oma = c(0, 0, 1, 0))
scatter_col <- rgb(15/255, 76/255, 129/255, alpha = 0.2)
for (sequence_name in unique(sequence_scatter$sequence)) {
  subset <- sequence_scatter[sequence_scatter$sequence == sequence_name, ]
  plot(
    subset$popcount_t,
    subset$popcount_t_plus_1,
    pch = 16,
    cex = 0.35,
    col = scatter_col,
    xlab = expression(S[t]),
    ylab = expression(S[t+1]),
    main = subset$label[1],
    xlim = range(c(subset$popcount_t, subset$popcount_t_plus_1)),
    ylim = range(c(subset$popcount_t, subset$popcount_t_plus_1))
  )
  abline(0, 1, lty = 2, col = palette_red, lwd = 1.2)
}
mtext("Lag-1 Scatter for Repeated-Hash Popcount Sequences", outer = TRUE, line = -1.2, cex = 1.1)
dev.off()
