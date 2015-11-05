from TunnelSegment import *
from tbmconfig import *
from pylab import *
import matplotlib.pyplot as plt
from bbt_database import *
import sqlite3, os,  csv , datetime
from bbtutils import *
from bbtnamedtuples import *
from tbmkpi import *
from collections import namedtuple
from pprint import pprint


# mi metto nella directory corrente
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

########## File vari: DB
sDBName = bbtConfig.get('Database','dbname')
sDBPath = os.path.join(os.path.abspath('..'), bbtConfig.get('Database','dbfolder'), sDBName)
if not os.path.isfile(sDBPath):
    print "Errore! File %s inesistente!" % sDBPath
    exit(1)
bbt_parameters = get_bbtparameters(sDBPath)
if len(bbt_parameters) == 0:
    print "Attenzione! Nel DB %s non ci sono i dati necessari!" % sDBPath
    exit(2)

# lista delle funzioni random per ogni profilo
normfunc_dicts = []
for bbt_parameter in bbt_parameters:
    normfunc_dict = build_normfunc_dict(bbt_parameter)
    normfunc_dicts.append(normfunc_dict)

#differenza tra CE e GLNORD
deltaCEGLN = 59488
#inizializzo le info sui tracciati
alnAll = []
aln=InfoAlignment('Cunicolo esplorativo direzione Nord', 'CE', 13290., 27217.)
alnAll.append(aln)
aln=InfoAlignment('Galleria di linea direzione Nord', 'GLNORD', deltaCEGLN-32088.0, deltaCEGLN-44191.75)
alnAll.append(aln)
aln=InfoAlignment('Galleria di linea direzione Sud', 'GLSUD', 49082.867, 54015.)
#alnAll.append(aln)

iIterationNo = 0
# va modificato in BbtParameterEval che ha solo fine e non la lunghezza
length = 10.0
kpiTbmList = []
for alnCurr in alnAll:
    # mi tengo gli estremi
    pkMinCurr = min(alnCurr.pkStart, alnCurr.pkEnd)
    pkMaxCurr = max(alnCurr.pkStart, alnCurr.pkEnd)
    # leggo tutte le tbm
    for tbmKey in tbms:
        tbmData = tbms[tbmKey]
        if alnCurr.tbmKey in tbmData.alignmentCode:
            tbm = TBM(tbmData, 'V')
            kpiTbm = KpiTbm4Tunnel(alnCurr.description,iIterationNo)
            kpiTbm.setKPI4TBM(tbmKey,tbm)
            p_i = 0
            for bbt_parameter in bbt_parameters:
                bbtparameter4seg = build_bbtparameter4seg_from_bbt_parameter(bbt_parameter,normfunc_dicts[p_i])
                pkMinSegm = min(bbtparameter4seg.inizio, bbtparameter4seg.fine)
                pkMaxSegm = max(bbtparameter4seg.inizio, bbtparameter4seg.fine)
                # shift di progressive, mettere criterio di scelta
                segmToAnalize = pkMinSegm <= pkMaxCurr and pkMaxSegm >= pkMinCurr
                if segmToAnalize:
                    try:
                        tbmsect = TBMSegment(bbtparameter4seg, tbm)
                        kpiTbm.setKPI4SEG(tbmsect,bbtparameter4seg)
                    except:
                        print bbtparameter4seg.fine
                        print bbtparameter4seg.rmr
                        exit(-1)
                p_i += 1
            kpiTbm.updateKPI(alnCurr)
            kpiTbmList.append(kpiTbm)

for kpiTbm in kpiTbmList:
    lst = kpiTbm.saveBbtTbmKpis(sDBPath)
