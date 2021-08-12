const { expect } = require("chai");
const { ethers } = require("hardhat");
const { utils } = require('ethers');
const [owner, addr1, addr2, addr3, addr4] = await ethers.getSigners();

const Token = await hre.ethers.getContractFactory("HunniERC20");
const TokenD = await Token.deploy();
const TokenDAddr = TokenD.address;

const TokenPresale = await hre.ethers.getContractFactory("HunniPresale");
const TokenPresaleD = await TokenPresale.deploy(TokenDAddr);
const TokenPresaleDAddr = TokenPresaleD.address;

const totalSupply = await TokenD.callStatic.balanceOf(owner.address);
await TokenD.approve(TokenPresaleDAddr, totalSupply);

await TokenPresaleD.setRate(1000);
await TokenPresaleD.allocate('10000000000000000000000000');
await TokenD.balanceOf(TokenPresaleDAddr);

await TokenPresaleD.connect(addr1).claim({value: utils.parseEther("1.0")});
await TokenD.balanceOf(addr1.address);
