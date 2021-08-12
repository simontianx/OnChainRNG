# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 21:05:13 2021

@author: Simon
"""

#%%
## Type 2.1:

results2_1 = [helper("Transaction Number: " + str(x)) for x in range(10000)];
results2_1_2 = np.array(results2_1);

rslt2_1 = np.array([(np.mean(results2_1_2[:,i]), np.std(results2_1_2[:,i])/np.sqrt(10000)) for i in range(256)])

drawGraph1(rslt2_1, 5)
plt.figure(5);
plt.plot(rslt2_1[:,0])
plt.plot(rslt2_1[:,0] + 1.96 * rslt2_1[:,1])
plt.plot(rslt2_1[:,0] - 1.96 * rslt2_1[:,1])

plt.figure(6);
acfs2_1 = acf(results2_1_2[:, 0])
plt.plot(acfs2_1)

#%%
## Type 2.2:
    
results2_2 = [helper("Transaction Number: " + str(x + 2 ** 128)) for x in range(10000)];
results2_2_2 = np.array(results2_2);

rslt2_2 = np.array([(np.mean(results2_2_2[:,i]), np.std(results2_2_2[:,i])/np.sqrt(10000)) for i in range(256)])

drawGraph1(rslt2_2, 7)
plt.figure(7);
plt.plot(rslt2_2[:,0])
plt.plot(rslt2_2[:,0] + 1.96 * rslt2_2[:,1])
plt.plot(rslt2_2[:,0] - 1.96 * rslt2_2[:,1])

plt.figure(8);
acfs2_2 = acf(results2_2_2[:, 0])
plt.plot(acfs2_2)

#%%
pearson_r(rslt[:,0], rslt1_2[:,0])
pearson_r(rslt[:,1], rslt1_2[:,1])
