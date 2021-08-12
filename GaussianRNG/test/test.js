const { expect } = require("chai");
const { ethers } = require("hardhat");
const { utils } = require('ethers');
const [owner, addr1] = await ethers.getSigners();

const GaussianRNG = await hre.ethers.getContractFactory("GaussianRNG");
const GaussianRNGD = await GaussianRNG.deploy();
const GaussianRNGDAddr = GaussianRNGD.address;

await GaussianRNGD.getGaussianRandomNumbers(1, 100);
await GaussianRNGD.reproduceGaussianRandomNumbers(1, 100);

describe("GaussianRNG", function() {
  it("Should return the new number once it's changed", async function() {
    const GaussianRNG = await hre.ethers.getContractFactory("GaussianRNG");
    const GaussianRNGD = await GaussianRNG.deploy();

    await GaussianRNG.deployed();
    expect(await GaussianRNGD.countOnes(1)).to.equal(1);
  });
});
