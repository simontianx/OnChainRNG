# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 15:16:21 2021

@author: Simon
"""

#%%

from web3 import Web3
import numpy as np
import matplotlib.pyplot as plt

#%%
def keccak256(val):
    """Compute keccak256 hash with the same algorithm used by Solidity"""
    if type(val) == int:
        return Web3.solidityKeccak(['uint256'], [val]).hex();
    elif type(val) == str:
        return Web3.solidityKeccak(['string'], [val]).hex();

def hashToBinary(hashValue):
    """Convert hashed value of type bytes32 into an array of binary digits in a string"""
    tmp = bin(int(hashValue, 16))[2:];
    prefix = '0' * (256 - len(tmp))
    return prefix + tmp;

def split(binaryArray):
    """Split binary digits into separate digits"""
    return [int(char) for char in binaryArray];

def helper(x):
    """Given an input value x, output an array of binary digits"""
    tmp = keccak256(x);
    tmp2 = hashToBinary(tmp);
    tmp3 = split(tmp2);
    return tmp3;

def pearson_r(x, y):
    """Compute Pearson correlation coefficient between two arrays."""
    # Compute correlation matrix: corr_mat
    corr_mat=np.corrcoef(x, y)
 
    # Return entry [0,1]
    return corr_mat[0, 1]

def acf(series):
    """
    http://en.wikipedia.org/wiki/Autocorrelation#Estimation
    """
    n = len(series)
    data = np.asarray(series)
    avg = np.mean(data)
    c0 = np.sum((data - avg) ** 2) / n

    def r(h):
        acf_lag = ((data[:n - h] - avg) * (data[h:] - avg)).sum() / n / c0
        return round(acf_lag, 3)
    
    # Avoiding lag 0 calculation
    x = np.arange(1, 31)
    acf_coeffs = list(map(r, x))
    return acf_coeffs


def drawGraph1(df, figureId):
    c = 3.725
    plt.figure(figureId);
    line_mid, = plt.plot(df[:,0], label='Avg')
    plt.xlabel("Digit Index")
    plt.ylabel("Probability")
    plt.xlim(0, 256)
    plt.ylim(0.46, 0.535)
    plt.hlines(0.5, 0, 256, linestyles='dashed', colors='red')
    line_up, = plt.plot(df[:,0] + c * df[:,1], label="95% CB Upper")
    line_down, = plt.plot(df[:,0] - c * df[:,1], label="95% CB Lower")
    plt.legend(
        handles=(line_up, line_mid, line_down),
        labels=('Upper', 'Avg', 'Lower'),
        loc='lower center',
        ncol=3)


#%%


