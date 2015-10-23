import pickle
import sys, os
import numpy as np
from pylab import *
from scipy.stats import *
from bbtutils import *
import sqlite3
from TunnelSegment import *
from collections import namedtuple
from bbtnamedtuples import BbtGeoitem, BbtParameter, BbtProfilo, bbtparameter_factory
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
conn = sqlite3.connect('bbt_mules_2-3.db')
conn.row_factory = bbtparameter_factory
cur = conn.cursor()
print "start querying database  "
bbtresults = cur.execute("SELECT inizio,fine,est,nord,he,hp,co,tipo,g_med,g_stddev,sigma_ci_avg,sigma_ci_stdev,mi_med,mi_stdev,ei_med,ei_stdev,cai_med,cai_stdev,gsi_med,gsi_stdev,rmr_med,rmr_stdev,profilo_id,geoitem_id FROM bbtparameter ORDER BY profilo_id")
# recupero tutti i parametri
bbt_parameters = []
for bbt_parameter in bbtresults:
    bbt_parameters.append(bbt_parameter)
conn.close()
print "start loading and evaluating parameters"
# definisco la TBM
tbm = TBM(10.0, 10.0, 10.0, 0.15, 12, 0.17, 0.03, 2.25, 0.15)
BbtParameterEval =  namedtuple('BbtParameterEval',['fine','he','hp','co','gamma','sigma','mi','ei','cai','gsi','rmr','closure'])
p_eval = zeros(shape=(12,len(bbt_parameters)), dtype=float)
i=0
pPrev = 0
bbt_evalparameters = []
# progress bar
N = len(bbt_parameters)
point = N / 100
increment = N / 20
for bbt_parameter in bbt_parameters:
    p_eval[0][i] = bbt_parameter.fine
    p_eval[1][i] = bbt_parameter.he
    p_eval[2][i] = bbt_parameter.hp
    p_eval[3][i] = bbt_parameter.co
    p_eval[4][i] = get_my_norm_function(bbt_parameter.g_med,bbt_parameter.g_stddev).rvs()
    p_eval[5][i] = get_my_norm_function(bbt_parameter.sigma_ci_avg,bbt_parameter.sigma_ci_stdev).rvs()
    p_eval[6][i] = get_my_norm_function(bbt_parameter.mi_med,bbt_parameter.mi_stdev).rvs()
    p_eval[7][i] = get_my_norm_function(bbt_parameter.ei_med,bbt_parameter.ei_stdev).rvs()
    p_eval[8][i] = get_my_norm_function(bbt_parameter.cai_med,bbt_parameter.cai_stdev).rvs()
    p_eval[9][i] = get_my_norm_function(bbt_parameter.gsi_med,bbt_parameter.gsi_stdev).rvs()
    p_eval[10][i] = get_my_norm_function(bbt_parameter.rmr_med,bbt_parameter.rmr_stdev).rvs()
    p_eval[11][i] = 0
    #tbmseg = TBMSegment(p_eval[4][i], 0.2, p_eval[7][i], p_eval[5][i],0.0,0.0, p_eval[6][i],p_eval[3][i],p_eval[3][i], 0.5, 1.0, p_eval[9][i], p_eval[10][i], 'Mech', (5**2)*math.pi, 10, 10, tbm.Slen, 0.0, 1.5,  tbm)
    # p_eval[10][i] = tbmseg.TunnelClosure(10.0)
    if pPrev != bbt_parameter.geoitem_id:
        plot((p_eval[0][i], p_eval[0][i]), (0, p_eval[1][i]),'y-', linewidth=0.3)
        pPrev = bbt_parameter.geoitem_id
    pEval = BbtParameterEval(p_eval[0][i],p_eval[1][i],p_eval[2][i],p_eval[3][i],p_eval[4][i],p_eval[5][i],p_eval[6][i],p_eval[7][i],p_eval[8][i],p_eval[9][i],p_eval[10][i],p_eval[11][i])
    bbt_evalparameters.append(pEval)
    if(i % (5 * point) == 0):
        sys.stdout.write("\r[" + "=" * (i / increment) +  " " * ((N - i)/ increment) + "]" +  str(i / point) + "%")
        sys.stdout.flush()
    i += 1

output = open('bbtdata.pkl', 'wb')
pickle.dump(bbt_evalparameters, output)
output.close()
print "\nparameters pickled in %s " % path
print "Plotting profile and related stuff"
plot(p_eval[0],p_eval[1], linewidth=2, color='black')
plot(p_eval[0],p_eval[2], linewidth=3, color='r')
plot(p_eval[0],p_eval[5])
plot(p_eval[0],p_eval[7])
axis([max(p_eval[0])*1.1,min(p_eval[0])*0.9,0,max(p_eval[1])+1])
show()

lmax = max(p_eval[0]) - min(p_eval[0])
deltal = 10
seg = len(p_eval[0])
print "Lunghezza dello scavo da %f a %f L=%f, %f segmenti di lunghezza %f " % ( min(p_eval[0]), max(p_eval[0]) , lmax, seg, deltal )
#######################
gi = zeros(shape=(seg,), dtype=float)
gti = zeros(shape=(seg,), dtype=float)


def calcola_giorni_avanzamento():
    ti = 0
    i=0
    m=(0.2*tnorm_r1.rvs() + 0.6*tnorm_r2.rvs() + 0.2*tnorm_r3.rvs() + tnorm_r4.rvs())
    for g in gi:
        v = g*m
        ti += v
        gti[i] += v
        i += 1
    return ti


#N = 1024*32
sys.stdout.flush()
N = 1024*4
point = N / 100
increment = N / 20
bi = zeros(shape=(N,), dtype=float)
bj = zeros(shape=(N,), dtype=float)
for k in range(N):
    bi[k] = calcola_ritardo_eventi_straordinari(lmax)
    #bj[k] = calcola_giorni_avanzamento() + bi[k]
    if(k % (5 * point) == 0):
        sys.stdout.write("\r[" + "=" * (k / increment) +  " " * ((N - k)/ increment) + "]" +  str(k / point) + "%")
        sys.stdout.flush()



title("Ritardi per Eventi Straordinari")
hist(bi, bins=50)
bi_mean = np.nanmean(bi)
bi_std = np.nanstd(bi)
bi_min = min(bi)
bi_max = max(bi)
axis([0,500,0,bi_max])

"""
subplot(211)
title("Tempo avanzamento")
hist(bj, bins=100)
bj_mean = np.nanmean(bj)
axvline(bj_mean,linewidth=4, color='g',label='media')
bj_std = np.nanstd(bj)
bj_min = min(bj)
bj_max = max(bj)
totnorm = norm(bj_mean,bj_std)
totint = totnorm.interval(0.95)
axvline(totint[0],linewidth=2,linestyle='--', color='y',label='min95')
axvline(totint[1],linewidth=2,linestyle='--' , color='r',label='max95')
axis([0,bj_max+365,0,height])

subplot(212)
title("Dettaglio avanzamento")
for i in range(seg):
    gti[i] = gti[i]/float(N)
cgti = np.cumsum(gti)
plot(grange,gti, linewidth=1)
axis([0,seg,0,max(gti)+1])
"""


show()
