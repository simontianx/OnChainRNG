# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 10:48:22 2021

@author: Simon
"""


#%%

def drawGraph1(df, figureId):
    
    plt.figure(figureId);
    line_mid, = plt.plot(df[:,0], label='Avg')
    plt.xlabel("Digit Index")
    plt.ylabel("Probability")
    plt.xlim(0, 256)
    plt.hlines(0.5, 0, 256, linestyles='dashed', colors='red')
    line_up, = plt.plot(df[:,0] + 1.96 * df[:,1], label="95% CB Upper")
    line_down, = plt.plot(df[:,0] - 1.96 * df[:,1], label="95% CB Lower")
    plt.legend(
        handles=(line_mid, line_up, line_down),
        labels=('Avg', '95% CB Upper', '95% CB Lower'),
        loc='upper right')


#%%

asciichars = string.ascii_letters + string.punctuation + string.digits;

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars)), n);
    return "".join(sentence)

nNums = 100000
results4_1 = [helper(getStr(100)) for x in range(nNums)];
results4_1_2 = np.array(results4_1);

rslt4_1 = np.array([(np.mean(results4_1_2[:,i]), np.std(results4_1_2[:,i])/np.sqrt(nNums)) for i in range(256)])

drawGraph1(rslt4_1, 41)

#%%

asciichars_1 = string.ascii_letters + string.punctuation;

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars_1)), n);
    return "".join(sentence)

nNums = 10000
results4_2 = [helper(getStr(5)) for x in range(nNums)];
results4_2_2 = np.array(results4_2);

rslt4_2 = np.array([(np.mean(results4_2_2[:,i]), np.std(results4_2_2[:,i])/np.sqrt(nNums)) for i in range(256)])

drawGraph1(rslt4_2, 42)

#%%
asciichars_2 = string.ascii_letters + string.digits;

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars_2)), n);
    return "".join(sentence)

nNums = 10000
results4_3 = [helper(getStr(5)) for x in range(nNums)];
results4_3_2 = np.array(results4_3);

rslt4_3 = np.array([(np.mean(results4_3_2[:,i]), np.std(results4_3_2[:,i])/np.sqrt(nNums)) for i in range(256)])

drawGraph1(rslt4_3, 43)

#%%
asciichars_3 = string.ascii_letters;

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars_3)), n);
    return "".join(sentence)

nNums = 10000
results4_4 = [helper(getStr(5)) for x in range(nNums)];
results4_4_2 = np.array(results4_4);

rslt4_4 = np.array([(np.mean(results4_4_2[:,i]), np.std(results4_4_2[:,i])/np.sqrt(nNums)) for i in range(256)])

drawGraph1(rslt4_4, 44)

#%%
asciichars_4 = string.digits;

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars_4)), n);
    return "".join(sentence)

nNums = 10000
results4_5 = [helper(getStr(5)) for x in range(nNums)];
results4_5_2 = np.array(results4_5);

rslt4_5 = np.array([(np.mean(results4_5_2[:,i]), np.std(results4_5_2[:,i])/np.sqrt(nNums)) for i in range(256)])

drawGraph1(rslt4_5, 44)


#%%

def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars)), n);
    return "".join(sentence)


nNums = 100000;
tmp = [getStr(10) for x in np.arange(nNums)];
