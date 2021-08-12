# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 21:13:18 2021

@author: Simon
"""


#%%

asciichars = string.ascii_letters + string.punctuation + string.digits;

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars)), n);
    return "".join(sentence)


#%%
## Type 3.1:

nNums = 10000

strs = [getStr(32) for x in range(nNums)];

results3_1 = [helper(getStr(7)) for x in range(nNums)];
results3_1_2 = np.array(results3_1);

rslt3_1 = np.array([(np.mean(results3_1_2[:,i]), np.std(results3_1_2[:,i])/np.sqrt(nNums)) for i in range(256)])

drawGraph1(rslt3_1, 9)

plt.figure(9);
plt.plot(rslt3_1[:,0])
plt.plot(rslt3_1[:,0] + 1.96 * rslt3_1[:,1])
plt.plot(rslt3_1[:,0] - 1.96 * rslt3_1[:,1])

plt.figure(10);
acfs3_1 = acf(results3_1_2[:, 0])
plt.plot(acfs3_1)

#%%
## Type 3.2:
nNums = 10000000
results3_2 = [helper(getStr(32)) for x in np.arange(nNums)];
results3_2_2 = np.array(results3_2);

rslt3_2 = np.array([(np.mean(results3_2_2[:,i]), np.std(results3_2_2[:,i])/np.sqrt(nNums)) for i in np.arange(256)])

drawGraph1(rslt3_2, 11)
plt.figure(11);
plt.plot(rslt3_2[:,0])
plt.plot(rslt3_2[:,0] + 1.96 * rslt3_2[:,1])
plt.plot(rslt3_2[:,0] - 1.96 * rslt3_2[:,1])


plt.figure(12);
acfs3_2 = acf(results3_2_2[:, 0])
plt.plot(acfs3_2)

#%%
pearson_r(rslt[:,0], rslt1_2[:,0])
pearson_r(rslt[:,1], rslt1_2[:,1])

#%%
mgrid = np.meshgrid(np.arange(256), np.arange(256));

pairs = [(mgrid[0][i][j], mgrid[1][i][j]) for i in np.arange(256) for j in np.arange(256) if i < j]

correlations3_1 = [(pair, pearson_r(results3_1_2[:, pair[0]], results3_1_2[:, pair[1]])) for pair in pairs];

corrs3_1 = [y for (x, y) in correlations3_1];

[np.mean(corrs3_1),
np.max(corrs3_1),
np.min(corrs3_1),
np.median(corrs3_1),
np.std(corrs3_1)]

correlations3_1_2 = [(i, pearson_r(results3_1_2[:, i], np.arange(10000))) for i in np.arange(256)];

correlations3_1_2
corrs3_1_2 = [y for (x, y) in correlations3_1_2];

corrs3_1_2

[np.mean(corrs3_1_2),
np.max(corrs3_1_2),
np.min(corrs3_1_2),
np.median(corrs3_1_2),
np.std(corrs3_1_2)]


#%%
mgrid = np.meshgrid(np.arange(256), np.arange(256));

pairs = [(mgrid[0][i][j], mgrid[1][i][j]) for i in np.arange(256) for j in np.arange(256) if i < j]

correlations3_2 = [(pair, pearson_r(results3_2_2[:, pair[0]], results3_2_2[:, pair[1]])) for pair in pairs];

corrs3_2 = [y for (x, y) in correlations3_2];

# Pairwise correlations should be displayed as a heatmap.

[np.mean(corrs3_2),
np.max(corrs3_2),
np.min(corrs3_2),
np.median(corrs3_2),
np.std(corrs3_2)]

correlations3_2_2 = [(i, pearson_r(results3_2_2[:, i], np.arange(10000))) for i in np.arange(256)];

correlations3_2_2
corrs3_2_2 = [y for (x, y) in correlations3_2_2];

corrs3_2_2

[np.mean(corrs3_2_2),
np.max(corrs3_2_2),
np.min(corrs3_2_2),
np.median(corrs3_2_2),
np.std(corrs3_2_2)]


#%%

np.sum([1 if np.abs(x) > 2.955 else 0 for x in (rslt3_2[:,0] - 0.5)/rslt3_2[:,1]])



##
# 1. Draw graphs of pointwise probabilities and confidence intervals for three
# scenarios each of which has two settings. Tabulate summary statistics.
# 2. Calculate autocorrelations among digits in each scenario and test the null
# hypothesis if they are all zero. Heuristic autocorrelations.
# 3. Calculate correlations between input values and outcomes. This is only 
# posssible for Type 1 and 2. and test them.
# 4. 

