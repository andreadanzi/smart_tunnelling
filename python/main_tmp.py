import math
from TunnelSegment import TBM
from TunnelSegment import TBMSegment
from pylab import *


"""
# (gamma, ni, e, ucs, sigmat, psi, mi, overburden, groundwaterdepth, k0min, k0max, rcType, rcValue, excavType, excavArea, excavWidth, excavHeight, refLength, pi, lunsupported)
xx = TBMSegment(26.8, 0.2, 300, 70,  5.0,0.0, 20.0,33.2436,33.2436, 0.5, 1.0, 20, 22, 'Mech', (5**2)*math.pi, 10, 10, tbm.Slen, 0.0, 1.5,  tbm)
print(xx.TunnelClosureAtShieldEnd, xx.Tbm.OverExcavation, xx.PressureOnShield,  xx.Xcontact)#, x.Gamma, x.Ei, x.Mi, x.Gsi, x.L, x.H, x.Mb, x.S, x.A)
x = 0.0
step = 0.05 # in m
reflen = tbm.Slen*1.5
dimarray = int(reflen / step)
vplot = zeros(shape=(3, dimarray), dtype=float)
i = 0
while x <= reflen:
    vplot[0][i] = x
    vplot[1][i] = xx.LDP_Panet_1995(x)
    vplot[2][i] = xx.LDP_Vlachopoulos_2009(x)
    i +=1
    x+=step

plot(vplot[0], vplot[1])
plot(vplot[0], vplot[2])
show()
"""

# andrea: pickle serve per serializzare e deserializzare oggetti che stanno in memoria, per poterli scivere su un file per poi riutilizzarli
import pickle, os, pprint
from collections import namedtuple
# BbtParameterEval e il tipo dato con cui ho serializzato i dati, e un contenitore di valori che puoi richiamare con il nome dl campo
BbtParameterEval =  namedtuple('BbtParameterEval',['fine','he','hp','co','gamma','sigma','mi','ei','cai','gsi'])
# ricavo il percorso della directory contenente il file corrente (main.py)
path = os.path.dirname(os.path.realpath(__file__))
# mi metto nella directory corrente
os.chdir(path)
# leggo il file serializzato (bbtdata.pkl) che ti ho messo nella stessa directory sul Drive
pkl_file = open('bbtdata.pkl', 'rb')
# carico un file mettendo il contenuto nell'oggettto bbt_evalparameters che e una lista di BbtParameterEval
bbt_evalparameters = pickle.load(pkl_file)
#          (slen, sdiammin, sdiammax, overexcav, cno, cr, ct, cs, friction)
tbm = TBM(10.0, 6.42, 6.62, 0.1, 12, 0.3, 0.03, 2.25, 0.15)

#for p in bbt_evalparameters:
for i in range(1):
    p = bbt_evalparameters[i]
    # qui puoi instanziare i tuoi TBMSegment usando p.fine, p.he, p.hp, p.co, p.gamma, p.sigma, p.mi, p.ei, p.cai, p.gsi
    # (gamma, ni, e, ucs, sigmat, psi, mi, overburden, groundwaterdepth, k0min, k0max, gsi, rmr, excavType, excavArea, excavWidth, excavHeight, refLength, pi, lunsupported, tbm)
    tbmsect = TBMSegment(p.gamma, 0.2, p.ei*1000.0, p.sigma, 5.0,0.0, p.mi, p.co, p.co, 0.5, 1.0, p.gsi, 0.0, 'Mech', (tbm.SdiamMax**2)*math.pi, tbm.SdiamMax, tbm.SdiamMax, tbm.Slen, 0.0, tbm.Slen,  tbm)
    print(tbmsect.TunnelClosureAtShieldEnd, tbmsect.Tbm.OverExcavation)#PressureOnShield,  tbmsect.Xcontact)#, x.Gamma, x.Ei, x.Mi, x.Gsi, x.L, x.H, x.Mb, x.S, x.A)
    x = 0.0
    step = 0.05 # in m
    reflen = tbm.Slen*1.5
    dimarray = int(reflen / step)
    vplot = zeros(shape=(3, dimarray), dtype=float)
    i = 0
    while x <= reflen:
        vplot[0][i] = x
        vplot[1][i] = tbmsect.LDP_Panet_1995(x)
        vplot[2][i] = tbmsect.LDP_Vlachopoulos_2009(x)
        i +=1
        x+=step

    plot(vplot[0], vplot[1])
    plot(vplot[0], vplot[2])
    show()

    print "%d -> Fine segmento=%f , Quota=%f, Quota Progetto=%f, Copertura=%f, Gamma=%f, Sigma=%f, Mi=%f, Ei=%f, CAI=%f, GSI=%f" % (i, p.fine, p.he, p.hp, p.co, p.gamma, p.sigma, p.mi, p.ei, p.cai, p.gsi)

# Nel caso puoi buttare il contenuto in un file csv: delimiter e' il separatore, da leggere con excel o file di testo
import csv
with open('bbtdata.csv', 'wb') as f:
    writer = csv.writer(f,delimiter=",")
    writer.writerows(bbt_evalparameters)
