# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 15:53:23 2021

@author: Simon
"""

#%%
## Count number of 11

x = hashToBinary(keccak256(123))

def negBin(x):
    n = 2;
    lastChar = x[0]
    for char in x[1:]:
        if char == lastChar and char == '1':
            return n
        else:
            lastChar = char
            n += 1

negBin(x)

#%%
asciichars = string.ascii_letters + string.punctuation + string.digits;

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars)), n);
    return "".join(sentence)

def Helper(x):
    y = hashToBinary(keccak256(x))
    return negBin(y)

nNums = 100000
results3_1 = [Helper(getStr(7)) for x in range(nNums)];
results3_1_2 = np.array(results3_1);

plt.hist(results3_1_2, nbins=100)

#%%
