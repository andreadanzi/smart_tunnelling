#from scipy.stats import *

import numpy as np
from pylab import *
from scipy.stats import *

# funzione che restituisce media e sigma di una gaussiana sulla base di valori minimi e massimi al 95 percentile
def get_sigma_95(min,max):
    if min==-1 or max == -1:
        return -1, 0
    avg = (max+min)/2.0
    sigma = (max-avg)/2.0
    return avg, sigma

#riskvariables (in days/10m)
r1 = {'min':0.6,'max':1.9}
eimin = r1['min']
eimax = r1['max']
avg, sigma = get_sigma_95(eimin,eimax)
tnorm_r1 = truncnorm((eimin - avg) / sigma, (eimax - avg) / sigma, loc=avg, scale=sigma)
r2 = {'min':0.7,'max':2.4}
eimin = r2['min']
eimax = r2['max']
avg, sigma = get_sigma_95(eimin,eimax)
tnorm_r2 = truncnorm((eimin - avg) / sigma, (eimax - avg) / sigma, loc=avg, scale=sigma)
r3 = {'min':0.9,'max':2.8}
eimin = r3['min']
eimax = r3['max']
avg, sigma = get_sigma_95(eimin,eimax)
tnorm_r3 = truncnorm((eimin - avg) / sigma, (eimax - avg) / sigma, loc=avg, scale=sigma)
r4 = {'min':0.5,'max':0.9}
eimin = r4['min']
eimax = r4['max']
avg, sigma = get_sigma_95(eimin,eimax)
tnorm_r4 = truncnorm((eimin - avg) / sigma, (eimax - avg) / sigma, loc=avg, scale=sigma)
ar =[r1,r2,r3,r4]

#parametri base fattore imprevisti
#frequenza di eventi eccezionali per metro di avanzamento sulla base del fattore umano
ei = {'S':{'min':2.2e-4, 'max':6.7e-3},'N':{'min':1.1e-4, 'max':3.3e-3},'F':{'min':5.6e-5, 'max':2.1e-3}}
#parametri base fattore umano
hi = ['S','N','F']
#tre opzioni S = Sfavorevole, N = Neutro, F = Favorevole
hixk = np.arange(3)
#la distribuzione delle tre opzioni
hipk = (0.2,0.4,0.3)
#Custom made discrete distribution for Human Factor - da chiamare con hi[hcustm.rvs()] restituisce S N o F sulla base della distribuzione
hcustm = rv_discrete(name='custm', values=(hixk, hipk))

def get_my_norm_rvs(mean,std,name=''):
    if mean==-1: return mean
    if std > 0:
        lower = mean - 3*std
        upper = mean + 3*std
        if lower < 0:
            # print "1 - lower = %f < 0 for %s with input %f and %f" % (lower,name,mean,std)
            lower = mean - 2*std
            upper = mean + 2*std
            if lower < 0:
                # print "2 -lower = %f < 0 for %s with input %f and %f" % (lower,name,mean,std)
                lower = mean - std
                upper = mean + std
        a, b = (lower - mean) / std, (upper - mean) / std
        myNorm = truncnorm(a, b, loc=mean, scale=std)
        retVal = myNorm.rvs()
    else:
        myNorm = norm(mean, std)
        retVal = myNorm.rvs()
    if retVal < 0:
        print "retVal = %f < 0 for %s ith input %f and %f" % (retVal,name,mean,std)
        retVal = mean - std
    return retVal

def get_my_norm_rvs_min_max(vmin,vmax,name=''):
    mean , std = get_sigma_95(vmin,vmax)
    if mean == -1: return mean
    lower = vmin
    upper = vmax
    if lower < 0:
        # print "2 -lower = %f < 0 for %s with input %f and %f" % (lower,name,mean,std)
        lower = mean - std
        upper = mean + std
    a, b = (lower - mean) / std, (upper - mean) / std
    myNorm = truncnorm(a, b, loc=mean, scale=std)
    retVal = myNorm.rvs()
    if retVal < 0:
        print "retVal = %f < 0 for %s ith input %f and %f" % (retVal,name,mean,std)
        retVal = mean - std
    return retVal


# distribuzione binomiale (tempo di ritorno) di eventi ogni l metri che causano ritardo di N giorni, dove N = il doppio del massimo tra i tempi
def evento_eccezionale(l,ecc):
    ret = binom(l,ecc)
    try:
        retval = ret.rvs()
    except ValueError:
        print "something wrong with %f %f" % (l,ecc)
        exit()
    retval = retval*2*tnorm_r1.rvs()
    return retval

def calcola_ritardo_eventi_straordinari(l):
    hcusti = hcustm.rvs()
    eimin = ei[hi[hcusti]]['min']
    eimax = ei[hi[hcusti]]['max']
    avg, sigma = get_sigma_95(eimin,eimax)
    tnorm = truncnorm((eimin - avg) / sigma, (eimax - avg) / sigma, loc=avg, scale=sigma)
    ecc = tnorm.rvs()
    return evento_eccezionale(l,ecc)
