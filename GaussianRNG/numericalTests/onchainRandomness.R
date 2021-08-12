# onchainRandomness.R

nCategories <- 6

x <- seq(1/nCategories, 1-1/nCategories, by=1/nCategories)

y <- qnorm(x, 128, 8)
y

z <- round(y)  ## it should be p(k <= z) in making the cut.
z

pnorm(z, 128, 8)
