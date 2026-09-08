summary_data <- read.csv("generated/cross_vm_summary_metrics.csv", stringsAsFactors = FALSE)
pairwise_data <- read.csv("generated/cross_vm_pairwise_metrics.csv", stringsAsFactors = FALSE)

dir.create("figures", showWarnings = FALSE)

palette_blue <- "#0F4C81"
palette_red <- "#C84C1A"
palette_gold <- "#C79A00"
palette_green <- "#2E7D32"
palette_gray <- "#555555"

short_label <- function(label) {
  gsub(" Randomness Reference", " Ref.", label, fixed = TRUE)
}

labels <- short_label(summary_data$label)
x_positions <- seq_len(nrow(summary_data))

pdf("figures/cross_vm_overview.pdf", width = 12, height = 8)
par(mfrow = c(2, 2), mar = c(6, 4, 2.8, 1))

plot(
  x_positions,
  summary_data$max_abs_delta_mu,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_blue,
  xaxt = "n",
  xlab = "",
  ylab = expression(max(abs(hat(mu) - n / 2))),
  main = "Centering Error"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

plot(
  x_positions,
  summary_data$max_abs_delta_sigma,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_green,
  xaxt = "n",
  xlab = "",
  ylab = expression(max(abs(hat(sigma) - sqrt(n) / 2))),
  main = "Scaling Error"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

plot(
  x_positions,
  summary_data$max_ks_distance,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_red,
  xaxt = "n",
  xlab = "",
  ylab = "Worst KS Distance",
  main = "Gaussian Fit"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

plot(
  x_positions,
  summary_data$max_abs_tail_error_z2,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_gold,
  xaxt = "n",
  xlab = "",
  ylab = expression(max(abs(Delta * T[2]))),
  main = "Tail Error at z = 2"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

dev.off()

pdf("figures/cross_vm_dependence.pdf", width = 12, height = 8)
par(mfrow = c(2, 2), mar = c(6, 4, 2.8, 1))

plot(
  x_positions,
  summary_data$max_abs_input_corr,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_blue,
  xaxt = "n",
  xlab = "",
  ylab = "Worst |Input Corr|",
  main = "Input-Output Dependence"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

plot(
  x_positions,
  summary_data$max_abs_bit_acf,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_red,
  xaxt = "n",
  xlab = "",
  ylab = "Worst Bit-Level |ACF|",
  main = "Within-Output Lag Structure"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

plot(
  x_positions,
  summary_data$max_abs_lag1,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_green,
  xaxt = "n",
  xlab = "",
  ylab = "Worst |Lag-1 Corr|",
  main = "Sequence Dependence"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

plot(
  x_positions,
  summary_data$max_abs_sequence_acf,
  type = "h",
  lwd = 6,
  lend = "butt",
  col = palette_gold,
  xaxt = "n",
  xlab = "",
  ylab = "Worst Sequence |ACF|",
  main = "Repeated-Primitive Sequence"
)
axis(1, at = x_positions, labels = labels, las = 2, cex.axis = 0.85)
abline(h = 0, lty = 2, col = palette_gray)

dev.off()

pair_labels <- short_label(pairwise_data$label)
pair_positions <- seq_len(nrow(pairwise_data))

pdf("figures/cross_vm_pairwise.pdf", width = 12, height = 4.5)
par(mfrow = c(1, 3), mar = c(6, 4, 2.8, 1))

plot(
  pair_positions,
  pairwise_data$mean_rogers_tanimoto,
  type = "h",
  lwd = 8,
  lend = "butt",
  col = palette_blue,
  xaxt = "n",
  xlab = "",
  ylab = "Mean RT",
  main = "Rogers-Tanimoto"
)
axis(1, at = pair_positions, labels = pair_labels, las = 2, cex.axis = 0.85)

plot(
  pair_positions,
  pairwise_data$mean_sokal_michener,
  type = "h",
  lwd = 8,
  lend = "butt",
  col = palette_red,
  xaxt = "n",
  xlab = "",
  ylab = "Mean SM",
  main = "Sokal-Michener"
)
axis(1, at = pair_positions, labels = pair_labels, las = 2, cex.axis = 0.85)

plot(
  pair_positions,
  pairwise_data$max_abs_phi,
  type = "h",
  lwd = 8,
  lend = "butt",
  col = palette_gold,
  xaxt = "n",
  xlab = "",
  ylab = "Max |phi|",
  main = "Phi Correlation"
)
axis(1, at = pair_positions, labels = pair_labels, las = 2, cex.axis = 0.85)

dev.off()
