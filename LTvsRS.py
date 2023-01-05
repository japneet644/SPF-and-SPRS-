# All parameters use same notation as paper
n = 160000
m = 32
l = 1000
k = 16
delta = 0.01
ROBUST_FAILURE_PROBABILITY = 0.01
EPSILON = 0.0001
SYSTEMATIC = False
VERBOSE = False
d = 30
zw = 3
zr = 4

import os
import sys
import math
import time
import numpy as np
import random
from itertools import filterfalse
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from random import choices
from random import randrange
from encoder import encode
from decoder import SEF_decode


def SPRS_encode(l,k):
    selection_indexes = random.sample(range(l),k)
    return selection_indexes


def SPRS_decode(blockindices):
    bootstrap = 0
    bandwidth = 0
    decodelen = len(blockindices)
    decodeflag = np.zeros(decodelen)
    bandwidth_all = d*k/(d-2*zw-zr)
    simulataneous, onebyone,counter = np.zeros(25),np.zeros(25),np.zeros(25)
    while bool(blockindices):
        droplets = SPRS_encode(l,k)
        bootstrap = bootstrap + 1
        common = np.intersect1d(blockindices, droplets).tolist() 
        if bool(common):
            bandwidth_individual = 6*len(common)
            bootstrap = bootstrap + d-1
            if bandwidth_all > bandwidth_individual:
                bandwidth = bandwidth + bandwidth_individual
                onebyone[24-(len(blockindices)//40)] = onebyone[24-(len(blockindices)//40)] + 
            else:
                bandwidth = bandwidth + bandwidth_all
                simulataneous[24-(len(blockindices)//40)] = simulataneous[24-(len(blockindices)//40)] + 1
            counter[24-(len(blockindices)//40)] = counter[24-(len(blockindices)//40)] + 1
            for element in common:
                blockindices.remove(element)
    return bootstrap, bandwidth, simulataneous/counter, onebyone/counter

iter = 300
bootstrapped_nodes = np.zeros(iter)
bd = np.zeros(iter)
simulataneous = np.zeros(25)
onebyone =  np.zeros(25)
simulataneous_var = np.zeros(25)
onebyone_var =  np.zeros(25)
for i in range(iter):
    index = list(range(1,l))
    bootstrapped_nodes[i],bd[i],simul, oneby = SPRS_decode(index)
    onebyone = onebyone + oneby
    onebyone_var = onebyone_var + oneby**2
    simulataneous = simulataneous + simul
    simulataneous_var = simulataneous_var + simul**2
    print('SPRS: Bootstrap = ', bootstrapped_nodes[i], ' SPRS bandwidth =', bd[i])
print("SPRS: Bootstrap 99 percentile ",np.percentile(bootstrapped_nodes,99))
print("SPRS bd: ",np.percentile(bd,99))
print(bootstrapped_nodes.tolist())
bootstrapped_nodes = np.zeros(iter)
onebyone_var = onebyone_var/iter - (onebyone/iter)**2
simulataneous_var = simulataneous_var/iter - (simulataneous/iter)**2
plt.errorbar(np.linspace(0,1,25),simulataneous/iter,np.sqrt(simulataneous_var), color='b', linewidth=2, label = 'Fraction of times all blocks \n are decoded simultaneously', fmt='-o', elinewidth=1, capsize=4)
plt.errorbar(np.linspace(0,1,25),onebyone/iter,     np.sqrt(onebyone_var)     , color='r', linewidth=2, label = 'Fraction of times avaliable \n blocks are decoded one by one',fmt='-o', elinewidth=1, capsize=4)
plt.xlabel('Fraction of blocks decoded in the epoch',fontsize=12,fontweight='bold')
# plt.ylabel('',fontsize=12,fontweight='bold')
plt.legend(fontsize=12)
plt.savefig('./figure_3.png', bbox_inches='tight')
plt.show()
print(simulataneous)

