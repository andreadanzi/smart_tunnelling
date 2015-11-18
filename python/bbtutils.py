#from scipy.stats import *

import numpy as np
from pylab import *
from scipy.stats import *
import ConfigParser, os
# danzi.tn@20151115 colori per nuove TBM
# danzi.tn@20151118 colori per la nuova TBM
main_colors = ['#1f77b4',  '#ff7f0e', '#ffbb78',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#2ca02c', '#bcbd22', '#dbdb8d', '#B56123', '#aec7e8', '#17becf', '#9edae5','#FCBE01','#44619D']

path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
##########
sCFGName = 'bbt.cfg'
bbtConfig = ConfigParser.RawConfigParser()
bbtConfig.read(sCFGName)

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
ehumi = {'S':{'min':2.2e-4, 'max':6.7e-3},'N':{'min':1.1e-4, 'max':3.3e-3},'F':{'min':5.6e-5, 'max':2.1e-3}}

#frequenza di eventi eccezionali per metro di avanzamento sulla base del fattore geo
egeoi = [(10,30,2.2e-4,6.7e-3),(30,60,1.1e-4,3.3e-3),(60,90,5.6e-5,2.1e-3)]
#probabilita di evento funesto per tipologia
egeoi = [(10,30,0.1,0.9),(30,60,0.05,0.95),(60,90,0.01,0.99)]
#parametri base fattore umano
hi = ['S','N','F']
#tre opzioni S = Sfavorevole, N = Neutro, F = Favorevole
hixk = np.arange(3)
#la distribuzione delle tre opzioni
hipk = (0.2,0.4,0.3)
#Custom made discrete distribution for Human Factor - da chiamare con hi[hcustm.rvs()] restituisce S N o F sulla base della distribuzione
hcustm = rv_discrete(name='custm', values=(hixk, hipk))

class CNorm:
    mean=0
    def __init__(self, mean):
        self.mean = mean
    def rvs(self):
        return self.mean

def get_my_norm_func(mean,std,name=''):
    if mean==-1 or std==0: return mean
    lower = mean - 3*std
    upper = mean + 3*std
    if lower <= 0:
        # print "1 - lower = %f < 0 for %s with input %f and %f" % (lower,name,mean,std)
        lower = mean - 2*std
        upper = mean + 2*std
        if lower <= 0:
            # print "2 -lower = %f < 0 for %s with input %f and %f" % (lower,name,mean,std)
            lower = mean - std
            upper = mean + std
    myNorm = normal(mean, std)
    if myNorm < lower:
        myNorm = lower
    if myNorm > upper:
        myNorm = upper
    if myNorm <=0:
        print "input %f and %f for %s" % (mean,std,name)
    return myNorm

#danzi.tn@20151113 funzione statistica sulla base del numero di iterazioni
def get_my_norm(mean,std,name='',nIter=1000):
    # se la media inesistente o stDev nulla o poche iterazioni, restituisco sempre un valore costante pari alla media
    if mean==-1 or std==0 or nIter<2:
        return CNorm(mean)
    # nel caso di 2 o 3 iterazioni, restituisco un valore discreto
    elif nIter < 4:
        hixk = [mean-std,mean,mean+std]
        #la distribuzione delle tre opzioni
        hipk = (0.2,0.6,0.2)
        #Custom made discrete distribution for Human Factor - da chiamare con hi[hcustm.rvs()] restituisce S N o F sulla base della distribuzione
        myNorm = rv_discrete(name='bbt_%s' % name, values=(hixk, hipk))
        return myNorm
    else:
        lower = mean - 3*std
        upper = mean + 3*std
        if lower <= 0:
            # print "1 - lower = %f < 0 for %s with input %f and %f" % (lower,name,mean,std)
            lower = mean - 2*std
            upper = mean + 2*std
            if lower <= 0:
                # print "2 -lower = %f < 0 for %s with input %f and %f" % (lower,name,mean,std)
                lower = mean - std
                upper = mean + std
        if name=='rmr' or name=='gsi':
            if upper > 100:
                upper = 100
            if lower < 5:
                lower = 5
        a, b = (lower - mean) / std, (upper - mean) / std


        myNorm = truncnorm(a, b, loc=mean, scale=std)
        return myNorm

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

#danzi.tn@20151113 funzione statistica sulla base del numero di iterazioni
def get_my_norm_min_max(vmin,vmax,name='',nIter=1000):
    if vmin==-1 or vmax==-1:
        return CNorm(0.0)
    elif nIter<2:
        return CNorm((vmin+vmax)/2.0)
    elif nIter < 4:
        hixk = [vmin,(vmin+vmax)/2.0,vmax]
        #la distribuzione delle tre opzioni
        hipk = (0.2,0.6,0.2)
        #Custom made discrete distribution for Human Factor - da chiamare con hi[hcustm.rvs()] restituisce S N o F sulla base della distribuzione
        myNorm = rv_discrete(name='bbt_%s' % name, values=(hixk, hipk))
        return myNorm
    else:
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
        return myNorm


# distribuzione binomiale (tempo di ritorno) di eventi ogni l metri che causano ritardo di N giorni, dove N = il doppio del massimo tra i tempi
def evento_eccezionale(l,ecc):
    ret = binom(l,ecc)
    try:
        retval = ret.rvs()
        print "binom %f " % retval
    except ValueError:
        print "something wrong with %f %f" % (l,ecc)
        exit()
    retval = retval*2.0
    return retval

def calcola_ritardo_eventi_straordinari(l):
    hcusti = hcustm.rvs()
    eimin = ehumi[hi[hcusti]]['min']
    eimax = ehumi[hi[hcusti]]['max']
    avg, sigma = get_sigma_95(eimin,eimax)
    tnorm = truncnorm((eimin - avg) / sigma, (eimax - avg) / sigma, loc=avg, scale=sigma)
    ecc = tnorm.rvs()
    return evento_eccezionale(l,ecc)


def geo_ritardo_eventi_straordinari(l,rmr):
    res = [eg for eg in egeoi if  eg[0] < rmr <= eg[1] ]
    for r in res:
        eimin = r[2]
        eimax = r[3]
    avg, sigma = get_sigma_95(eimin,eimax)
    tnorm = truncnorm((eimin - avg) / sigma, (eimax - avg) / sigma, loc=avg, scale=sigma)
    ecc = tnorm.rvs()
    print "ecc %f" % ecc
    return evento_eccezionale(l,ecc)



def outputFigure(sDiagramsFolderPath, sFilename):
    imagefname=os.path.join(sDiagramsFolderPath,sFilename)
    if os.path.exists(imagefname):
        os.remove(imagefname)
    plt.savefig(imagefname,format='png', bbox_inches='tight', pad_inches=0)
