suppressPackageStartupMessages(library(ggplot2))

cdf_data <- read.csv("../NumericalStudy/generated/popcount_cdf.csv", stringsAsFactors = FALSE)
qq_data <- read.csv("../NumericalStudy/generated/popcount_qq.csv", stringsAsFactors = FALSE)
tail_data <- read.csv("../NumericalStudy/generated/popcount_tail_curves.csv", stringsAsFactors = FALSE)
distribution_metrics <- read.csv("../NumericalStudy/generated/popcount_distribution_metrics.csv", stringsAsFactors = FALSE)
sequence_acf <- read.csv("../NumericalStudy/generated/sequence_autocorrelation.csv", stringsAsFactors = FALSE)
sequence_summary <- read.csv("../NumericalStudy/generated/sequence_summary_metrics.csv", stringsAsFactors = FALSE)

out_dir <- "figures_ggplot2_review"
dir.create(out_dir, showWarnings = FALSE)

ink <- "#1F2430"
muted <- "#5C6675"
grid_col <- "#D5DCE6"
blue <- "#1F5AA6"
teal <- "#0F766E"
gold <- "#B7791F"
rose <- "#C44536"
slate_fill <- "#EEF3F8"

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
    "Sequence 3: repeated hashing from string seed Transaction Number: 1" = "Seed = Transaction Number: 1",
    "Sequence 4: repeated hashing from string seed Sequence Seed: alpha-2026" = "Seed = alpha-2026"
  )
  ifelse(label %in% names(mapping), mapping[label], label)
}

ordered_experiment_levels <- unique(short_experiment(qq_data$label))
ordered_sequence_levels <- unique(short_sequence(sequence_acf$label))

theme_pub <- function() {
  theme_minimal(base_size = 10.5, base_family = "sans") +
    theme(
      plot.title = element_text(face = "bold", size = 12, colour = ink),
      plot.subtitle = element_text(size = 9.6, colour = muted, margin = margin(b = 8)),
      plot.caption = element_text(size = 8.4, colour = muted),
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(colour = grid_col, linewidth = 0.35),
      panel.border = element_rect(colour = grid_col, fill = NA, linewidth = 0.7),
      axis.title = element_text(colour = ink),
      axis.text = element_text(colour = ink),
      strip.background = element_rect(fill = slate_fill, colour = grid_col, linewidth = 0.7),
      strip.text = element_text(face = "bold", colour = ink),
      legend.title = element_blank(),
      legend.text = element_text(colour = ink),
      plot.margin = margin(8, 10, 8, 8)
    )
}

pdf_device <- function(filename, width, height, ...) {
  grDevices::pdf(file = filename, width = width, height = height, family = "Helvetica", useDingbats = FALSE, ...)
}

save_review_plot <- function(plot, filename, width, height) {
  ggplot2::ggsave(
    filename = file.path(out_dir, filename),
    plot = plot,
    width = width,
    height = height,
    device = pdf_device
  )
}

cdf_gap <- max(abs(cdf_data$empirical_cdf - cdf_data$gaussian_cdf))
cdf_plot <- ggplot(cdf_data, aes(x = popcount)) +
  geom_step(aes(y = empirical_cdf, colour = "Empirical CDF"), linewidth = 1.15, lineend = "round") +
  geom_line(aes(y = gaussian_cdf, colour = "Gaussian CDF"), linewidth = 1.0, linetype = "22") +
  annotate(
    "label",
    x = max(cdf_data$popcount) - 2,
    y = 0.16,
    label = sprintf("max |Delta CDF| = %.3f", cdf_gap),
    hjust = 1,
    vjust = 0,
    linewidth = 0,
    fill = slate_fill,
    colour = muted,
    size = 3.1
  ) +
  scale_colour_manual(values = c("Empirical CDF" = blue, "Gaussian CDF" = rose)) +
  scale_x_continuous(breaks = pretty(range(cdf_data$popcount), n = 5), expand = expansion(mult = c(0.01, 0.02))) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.2), labels = scales::label_number(accuracy = 0.1), expand = expansion(mult = c(0, 0.02))) +
  labs(
    title = "Popcount CDF Against Gaussian Reference",
    subtitle = "Empirical mass tracks the Gaussianized reference closely across the central range.",
    x = "Popcount",
    y = "Cumulative probability",
    colour = NULL
  ) +
  theme_pub() +
  theme(legend.position = c(0.76, 0.17))
save_review_plot(cdf_plot, "popcount_cdf_ggplot2_review.pdf", width = 7.4, height = 5.2)

qq_data$facet_label <- factor(short_experiment(qq_data$label), levels = ordered_experiment_levels)
qq_low <- min(c(qq_data$gaussian_quantile, qq_data$empirical_quantile))
qq_high <- max(c(qq_data$gaussian_quantile, qq_data$empirical_quantile))
qq_ticks <- pretty(c(qq_low, qq_high), n = 4)
qq_annotations <- distribution_metrics
qq_annotations$facet_label <- factor(short_experiment(qq_annotations$label), levels = ordered_experiment_levels)
qq_annotations$x <- qq_high - 0.4
qq_annotations$y <- qq_low + 1.1
qq_annotations$label_text <- sprintf("KS = %.3f", qq_annotations$ks_distance)

qq_plot <- ggplot(qq_data, aes(x = gaussian_quantile, y = empirical_quantile)) +
  geom_abline(intercept = 0, slope = 1, colour = rose, linewidth = 0.8, linetype = "22") +
  geom_point(colour = blue, alpha = 0.42, size = 0.85) +
  geom_label(
    data = qq_annotations,
    aes(x = x, y = y, label = label_text),
    inherit.aes = FALSE,
    hjust = 1,
    vjust = 0,
    linewidth = 0,
    fill = slate_fill,
    colour = muted,
    size = 2.8
  ) +
  coord_fixed(xlim = c(qq_low, qq_high), ylim = c(qq_low, qq_high), expand = FALSE) +
  scale_x_continuous(breaks = qq_ticks) +
  scale_y_continuous(breaks = qq_ticks) +
  facet_wrap(~ facet_label, ncol = 3) +
  labs(
    title = "Popcount QQ Panels",
    subtitle = "Each panel compares empirical weight quantiles to the ideal Gaussianized reference.",
    x = "Gaussian quantile",
    y = "Empirical quantile"
  ) +
  theme_pub()
save_review_plot(qq_plot, "popcount_qq_panels_ggplot2_review.pdf", width = 11.3, height = 7.9)

tail_empirical <- tail_data[, c("experiment", "label", "z_level", "empirical_tail")]
names(tail_empirical)[4] <- "tail_probability"
tail_empirical$series <- "Empirical"

tail_gaussian <- tail_data[, c("experiment", "label", "z_level", "gaussian_tail")]
names(tail_gaussian)[4] <- "tail_probability"
tail_gaussian$series <- "Gaussian"

tail_long <- rbind(tail_empirical, tail_gaussian)
tail_long$facet_label <- factor(short_experiment(tail_long$label), levels = ordered_experiment_levels)
tail_annotations <- distribution_metrics
tail_annotations$facet_label <- factor(short_experiment(tail_annotations$label), levels = ordered_experiment_levels)
tail_annotations$x <- 2.95
tail_annotations$y <- 0.45
tail_annotations$label_text <- sprintf("|Delta T2| = %.3f", tail_annotations$tail_error_z2)

tail_plot <- ggplot(tail_long, aes(x = z_level, y = tail_probability, colour = series, shape = series, linetype = series)) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.8, stroke = 0.2) +
  geom_label(
    data = tail_annotations,
    aes(x = x, y = y, label = label_text),
    inherit.aes = FALSE,
    hjust = 1,
    vjust = 1,
    linewidth = 0,
    fill = slate_fill,
    colour = muted,
    size = 2.8
  ) +
  scale_colour_manual(values = c("Empirical" = blue, "Gaussian" = rose)) +
  scale_shape_manual(values = c("Empirical" = 16, "Gaussian" = 17)) +
  scale_linetype_manual(values = c("Empirical" = "solid", "Gaussian" = "22")) +
  scale_x_continuous(breaks = c(0.5, 1, 1.5, 2, 2.5, 3), expand = expansion(mult = c(0.02, 0.02))) +
  scale_y_log10(
    breaks = c(1, 0.1, 0.01, 0.001),
    labels = scales::label_number(accuracy = 0.001)
  ) +
  facet_wrap(~ facet_label, ncol = 3) +
  labs(
    title = "Popcount Tail Panels",
    subtitle = "The tail diagnostic shows where empirical weight probabilities diverge from the Gaussian reference.",
    x = "z threshold",
    y = "Two-sided tail probability"
  ) +
  theme_pub() +
  theme(legend.position = c(0.86, 0.9))
save_review_plot(tail_plot, "popcount_tail_panels_ggplot2_review.pdf", width = 11.3, height = 7.9)

sequence_acf$facet_label <- factor(short_sequence(sequence_acf$label), levels = ordered_sequence_levels)
acf_limit <- max(abs(sequence_acf$acf))
acf_limit <- max(acf_limit, 0.04)
conf_band <- 1.96 / sqrt(10000)
acf_annotations <- sequence_summary
acf_annotations$facet_label <- factor(short_sequence(acf_annotations$label), levels = ordered_sequence_levels)
acf_annotations$x <- max(sequence_acf$lag) - 1
acf_annotations$y <- acf_limit * 0.92
acf_annotations$label_text <- sprintf("lag-1 = %.3f", acf_annotations$lag1_correlation)

acf_plot <- ggplot(sequence_acf, aes(x = lag, y = acf)) +
  geom_hline(yintercept = 0, colour = rose, linewidth = 0.7, linetype = "22") +
  geom_hline(yintercept = c(-conf_band, conf_band), colour = muted, linewidth = 0.6, linetype = "33") +
  geom_segment(aes(xend = lag, y = 0, yend = acf), colour = blue, linewidth = 0.55, lineend = "round") +
  geom_point(colour = blue, size = 1.2) +
  geom_label(
    data = acf_annotations,
    aes(x = x, y = y, label = label_text),
    inherit.aes = FALSE,
    hjust = 1,
    vjust = 1,
    linewidth = 0,
    fill = slate_fill,
    colour = muted,
    size = 2.8
  ) +
  facet_wrap(~ facet_label, ncol = 2) +
  scale_x_continuous(breaks = c(1, 10, 20, 30), expand = expansion(mult = c(0.01, 0.02))) +
  scale_y_continuous(limits = c(-acf_limit, acf_limit), breaks = pretty(c(-acf_limit, acf_limit), n = 5)) +
  labs(
    title = "Repeated-Sequence ACF Panels",
    subtitle = "Autocorrelation remains visually small and inside the nominal confidence band across tested seeds.",
    x = "Lag",
    y = "Autocorrelation"
  ) +
  theme_pub()
save_review_plot(acf_plot, "sequence_acf_panels_ggplot2_review.pdf", width = 10.8, height = 8.0)
