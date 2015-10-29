import pickle
import sys, os, datetime
import numpy as np
from pylab import *
from scipy.stats import *
from bbtutils import *
from bbt_database import *
from TunnelSegment import *
from collections import namedtuple
from bbtnamedtuples import *

########## funzione che prende i parametri, calcolo il resto sulla base di RBM e TunnelSegment e restituisce la relativa lista di valori
def evaluate_parameters(bbt_parameters, iter_no=0):
    print "evaluate_parameters - start loading and evaluating parameters"
    tbm = TBM('DS', 300., 6.42, 6.62, .1, 38., 19.*.0254/2., .020, .1, 5.,  315., 11970., 35626., 42223., 4375., 6343., 4000., 0.15, 'P')

    dimarray = len(bbt_parameters)
    varnum = 30
    vplot = zeros(shape=(varnum, dimarray), dtype=float)
    vcheck = zeros(shape=(dimarray,  varnum), dtype=float)
    i=0
    bbt_evalparameters = []
    # progress bar
    N = len(bbt_parameters)
    point = N / 100
    increment = N / 20
    now = datetime.datetime.now()
    strnow = now.strftime("%Y%m%d%H%M%S")
    for bbt_parameter in bbt_parameters:
        vplot[0][i] = 0
        vplot[1][i] = iter_no #iteration_no
        vplot[2][i] = bbt_parameter.fine
        vplot[3][i] = bbt_parameter.he
        vplot[4][i] = bbt_parameter.hp
        co = vplot[5][i] = bbt_parameter.co
        gamma = vplot[6][i] = get_my_norm_rvs(bbt_parameter.g_med,bbt_parameter.g_stddev,'gamma')
        sigma = vplot[7][i] = get_my_norm_rvs(bbt_parameter.sigma_ci_avg,bbt_parameter.sigma_ci_stdev,'sigma')
        mi = vplot[8][i] = get_my_norm_rvs(bbt_parameter.mi_med,bbt_parameter.mi_stdev,'mi')
        ei = vplot[9][i] = get_my_norm_rvs(bbt_parameter.ei_med,bbt_parameter.ei_stdev,'ei')
        vplot[10][i] = get_my_norm_rvs(bbt_parameter.cai_med,bbt_parameter.cai_stdev,'cai')
        gsi = vplot[11][i] = get_my_norm_rvs(bbt_parameter.gsi_med,bbt_parameter.gsi_stdev,'gsi')
        rmr = vplot[12][i] = get_my_norm_rvs(bbt_parameter.rmr_med,bbt_parameter.rmr_stdev,'rmr')
        tbmsect = TBMSegment(gamma, .2, ei*1000., sigma, 5.,0., mi, co, co, .5, 1., gsi, rmr, 'Mech', (tbm.SdiamMax**2)*math.pi/4., tbm.SdiamMax, tbm.SdiamMax, tbm.Slen, 0., tbm.Slen,  tbm)
        vplot[13][i] = tbmsect.pkCe2Gl(bbt_parameter.fine)
        vplot[14][i] = tbmsect.TunnelClosureAtShieldEnd*100. #in cm
        vplot[15][i] = tbmsect.rockBurst.Val
        vplot[16][i] = tbmsect.frontStability.Ns
        vplot[17][i] = tbmsect.frontStability.lambdae
        vplot[18][i] = tbmsect.penetrationRate*1000. #in mm/giro
        vplot[19][i] = tbmsect.penetrationRateReduction*1000. #in mm/giro
        vplot[20][i] = tbmsect.contactThrust
        vplot[21][i] = tbmsect.torque
        vplot[22][i] = tbmsect.frictionForce
        vplot[23][i] = tbmsect.requiredThrustForce
        vplot[24][i] = tbmsect.availableThrust
        vplot[25][i] = tbmsect.dailyAdvanceRate
        vplot[26][i] = bbt_parameter.profilo_id
        vplot[27][i] = bbt_parameter.geoitem_id
        vplot[28][i] = get_my_norm_rvs_min_max(bbt_parameter.sigma_ti_min,bbt_parameter.sigma_ti_max,'sigma_ti')
        vplot[29][i] = get_my_norm_rvs_min_max(bbt_parameter.k0_min,bbt_parameter.k0_max,'k0')

        list_val = []
        list_val.append(strnow)
        list_val.append(0)
        for j in range(2,len(vplot[:,i])):
            list_val.append(vplot[j][i])
            if j==27:
                list_val.append(bbt_parameter.title)
        pEval = BbtParameterEval(*list_val)
        bbt_evalparameters.append(pEval)
        if(i % (5 * point) == 0):
            sys.stdout.write("\r[" + "=" * (i / increment) +  " " * ((N - i)/ increment) + "]" +  str(i / point) + "%")
            sys.stdout.flush()
        i += 1
    return bbt_evalparameters

#### stampa
def plot_parametereval(bbt_evalparameters):
    pPrev = 0
    vplot2=[]
    vplot3=[]
    vplot4=[]
    vplotval=[]
    for bbt_parametereval in bbt_evalparameters:
        if pPrev != bbt_parametereval.geoitem_id:
            plot((bbt_parametereval.fine, bbt_parametereval.fine), (0, bbt_parametereval.he),'y-', linewidth=0.3)
            pPrev = bbt_parametereval.geoitem_id
        vplot2.append(bbt_parametereval.fine)
        vplot3.append(bbt_parametereval.he)
        vplot4.append(bbt_parametereval.hp)
        vplotval.append(bbt_parametereval.dailyAdvanceRate)

    print "\nPlotting profile and related stuff"
    plot(vplot2,vplot3, linewidth=2, color='black')
    plot(vplot2, vplot4, linewidth=3, color='r')
    plot(vplot2,vplotval)
    axis([max(vplot2)*1.1,min(vplot2)*0.9,0,max(vplot3)+1])
    show()

########## Mi metto nella directory corrente
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
########## File vari: DB
sDBName = 'bbt_mules_2-3.db'
sDBPath = os.path.join(os.path.abspath('..'),'db', sDBName)
if not os.path.isfile(sDBPath):
    print "Errore! File %s inesistente!" % sDBPath
    exit(1)
########## Leggo dal DB BbtParameter
bbt_parameters = get_bbtparameters(sDBPath)
########## Eseguo calcolo sulla base di TunnelSegment
bbt_evalparameters = evaluate_parameters(bbt_parameters,0)
########## Stampo
plot_parametereval(bbt_evalparameters)
# salvo valori di valutazione
insert_bbtparameterseval(sDBPath,bbt_evalparameters)
exit(-1)
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
