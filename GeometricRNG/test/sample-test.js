const { expect } = require("chai");
const { ethers } = require("hardhat");
const { utils } = require('ethers');
const [owner, addr1] = await ethers.getSigners();

const GeometricRNG = await hre.ethers.getContractFactory("GeometricRNG");
const GeometricRNGD = await GeometricRNG.deploy();
const GeometricRNGDAddr = GeometricRNGD.address;
