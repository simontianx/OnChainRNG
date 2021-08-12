# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 09:51:37 2021

@author: Simon
"""

#%%

from web3 import Web3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import string

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
hashedValue = keccak256(123);

hashedValue

val = hashToBinary('0x26700e13983fefbd9cf16da2ed70fa5c6798ac55062a4803121a869731e308d2')

split(val)

#%%
## Hash values from Solidity
## keccak256(abi.encodePacked(0));
'0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563'

## Hash values by the function defined above
## keccak256(0)
'0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563'

#%%

"""
Type 1: numerical values
Type 1.1: 0, 1, ..., 10000
Type 1.2: 2^128 + (0, 1, ..., 10000)
Type 2: string + numerical values
Type 2.1: "Transaction Number: " + 0, 1, ..., 10000
Type 2.2: "Transaction Number: " + 0, 1, ..., 10000 + 2^128
Type 3: Strings
Type 3.1: any permutation and combination of arbitrary length of ASCII characters
Type 3.2: any permutation and combination of arbitrary length of ASCII characters
"""

#%%
## Type 1.1:

results1_1 = [helper(x) for x in range(10000)];
results1_1_2 = np.array(results1_1);

rslt1_1 = np.array([(np.mean(results1_1_2[:,i]), np.std(results1_1_2[:,i])/np.sqrt(10000)) for i in range(256)])

drawGraph1(rslt1_1, 1)

#%%%
plt.figure(1);
line_mid, = plt.plot(rslt1_1[:,0], label='Avg')
plt.xlabel("Digit Index")
plt.ylabel("Probability")
plt.xlim(0, 256)
plt.ylim(0.475, 0.54)
plt.hlines(0.5, 0, 256, linestyles='dashed', colors='red')
line_up, = plt.plot(rslt1_1[:,0] + 1.96 * rslt1_1[:,1], label="95% CB Upper")
line_down, = plt.plot(rslt1_1[:,0] - 1.96 * rslt1_1[:,1], label="95% CB Lower")
plt.legend(
    handles=(line_mid, line_up, line_down),
    labels=('Avg', 'Upper', 'Lower'),
    loc='lower center',
    ncol=3)

acfs1_1 = acf(results1_1_2[:, 0])
plt.figure(2);
plt.plot(acfs1_1)
plt.xlabel("Lag")
plt.ylabel("Autocorrelation")
plt.hlines(0, 0, 30, linestyles='dashed', colors='red')


# Do tests on autocorrelations

#%%
## Type 1.2:
    
results1_2 = [helper(x + 2 ** 128) for x in range(10000)];
results1_2_2 = np.array(results1_2);

rslt1_2 = np.array([(np.mean(results1_2_2[:,i]), np.std(results1_2_2[:,i])/np.sqrt(10000)) for i in range(256)])

drawGraph1(rslt1_2, 3)
plt.figure(3);
plt.plot(rslt1_2[:,0])
plt.plot(rslt1_2[:,0] + 3.725 * rslt1_2[:,1])
plt.plot(rslt1_2[:,0] - 3.725 * rslt1_2[:,1])

plt.figure(4);
acfs1_2 = acf(results1_2_2[:, 0])
plt.plot(acfs1_2)

#%%
pearson_r(rslt[:,0], rslt1_2[:,0])
pearson_r(rslt[:,1], rslt1_2[:,1])
    
    
#%%
mgrid = np.meshgrid(np.arange(256), np.arange(256));

pairs = [(mgrid[0][i][j], mgrid[1][i][j]) for i in np.arange(256) for j in np.arange(256) if i < j]

correlations1_1 = [(pair, pearson_r(results1_1_2[:, pair[0]], results1_1_2[:, pair[1]])) for pair in pairs];

corrs1_1 = [y for (x, y) in correlations1_1];

np.mean(corrs1_1)
np.max(corrs1_1)
np.min(corrs1_1)
np.median(corrs1_1)
np.var(corrs1_1)


correlations1_1_2 = [(i, pearson_r(results1_1_2[:, i], np.arange(10000))) for i in np.arange(256)];

correlations1_1_2
corrs1_1_2 = [y for (x, y) in correlations1_1_2];

corrs1_1_2

np.mean(corrs1_1_2)
np.max(corrs1_1_2)
np.min(corrs1_1_2)
np.median(corrs1_1_2)
np.std(corrs1_1_2)


#%%
acfs = [(i, acf(results2[:, i])) for i in np.arange(256)];

acfs1 = acfs[0]

plt.plot(acfs1[1])

#%%
# Test of cross-correlations: 
# Test of auto-correlations: 
# Test of distributions: J-B Test


#%%
## Type 2:



