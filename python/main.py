import math
from TunnelSegment import TBM

#               (slen, sdiammin, sdiammax, overexcav, cno, cr, ct, cs)
tbm = TBM(11.5, 10.0, 9.9, 0.01, 12, 0.3, 0.03, 2.25)
# (gamma, ni, e, ucs, sigmat, psi, mi, overburden, groundwaterdepth, k0min, k0max, rcType, rcValue, excavType, excavArea, excavWidth, excavHeight, refLength, pi, lunsupported)

from TunnelSegment import TBMSegment
x = TBMSegment(26.8, 0.2, 300, 70,  5.0,0.0, 20.0,33.2436,33.2436, 0.5, 1.0, 20, 22, 'Mech', (5**2)*math.pi, 10, 10, tbm.Slen, 0.0, 1.5,  tbm)
print(x.TunnelClosureAtShieldEnd, x.Tbm.OverExcavation, x.PressureOnShield,  x.Xcontact)#, x.Gamma, x.Ei, x.Mi, x.Gsi, x.L, x.H, x.Mb, x.S, x.A)


## andrea: pickle serve per serializzare e deserializzare oggetti che stanno in memoria, per poterli scivere su un file per poi riutilizzarli
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
# per 100 elementi della lista stampo i parametri
for i in range(100):
    p = bbt_evalparameters[i]
    # qui puoi instanziare i tuoi TBMSegment usando p.fine, p.he, p.hp, p.co, p.gamma, p.sigma, p.mi, p.ei, p.cai, p.gsi
    print "%d -> Fine segmento=%f , Quota=%f, Quota Progetto=%f, Copertura=%f, Gamma=%f, Sigma=%f, Mi=%f, Ei=%f, CAI=%f, GSI=%f" % (i, p.fine, p.he, p.hp, p.co, p.gamma, p.sigma, p.mi, p.ei, p.cai, p.gsi)

# Nel caso puoi buttare il contenuto in un file csv: delimiter e' il separatore, da leggere con excel o file di testo
import csv
with open('bbtdata.csv', 'wb') as f:
    writer = csv.writer(f,delimiter=",")
    writer.writerows(bbt_evalparameters)
