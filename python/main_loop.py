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
normfunc_dicts = {}
for bbt_parameter in bbt_parameters:
    normfunc_dict = build_normfunc_dict(bbt_parameter)
    normfunc_dicts[int(bbt_parameter.fine)] = normfunc_dict

#inizializzo le info sui tracciati dai file di configurazione
inizio_GLEST = bbtConfig.getfloat('Import','inizio_GLEST')
fine_GLEST = bbtConfig.getfloat('Import','fine_GLEST')
inizio_GLSUD = bbtConfig.getfloat('Import','inizio_GLSUD')
fine_GLSUD = bbtConfig.getfloat('Import','fine_GLSUD')
inizio_CE = bbtConfig.getfloat('Import','inizio_CE')
fine_CE = bbtConfig.getfloat('Import','fine_CE')
#differenza tra CE e GLEST in modo tale che GLNORD = delta_GLEST_CE - CE
delta_GLEST_CE =  bbtConfig.getfloat('Import','delta_GLEST_CE')
projectRefCost =  bbtConfig.getfloat('Import','project_ref_cost') # mln di euro

alnAll = []
aln=InfoAlignment('Cunicolo esplorativo direzione Nord', 'CE', delta_GLEST_CE - fine_CE, delta_GLEST_CE - inizio_CE )
alnAll.append(aln)
aln=InfoAlignment('Galleria di linea direzione Nord', 'GLNORD',inizio_GLEST, fine_GLEST)
alnAll.append(aln)
aln=InfoAlignment('Galleria di linea direzione Sud', 'GLSUD', inizio_GLSUD, fine_GLSUD)
alnAll.append(aln)

iIterationNo = 0
kpiTbmList = []
for alnCurr in alnAll:
    print alnCurr.description
    # leggo tutte le tbm
    for tbmKey in tbms:
        tbmData = tbms[tbmKey]
        if alnCurr.tbmKey in tbmData.alignmentCode:
            tbm = TBM(tbmData, 'V')
            kpiTbm = KpiTbm4Tunnel(alnCurr.description,iIterationNo)
            kpiTbm.setKPI4TBM(alnCurr,tbmKey,tbm,projectRefCost)
            matches_params = [bpar for bpar in bbt_parameters if alnCurr.pkStart <= bpar.inizio and bpar.fine <= alnCurr.pkEnd]
            print "\t for %s the number of segments is %d from %f to %f" % (tbmKey, len(matches_params),matches_params[0].fine,matches_params[-1].fine)
            for bbt_parameter in matches_params:
                bbtparameter4seg = build_bbtparameter4seg_from_bbt_parameter(bbt_parameter,normfunc_dicts[int(bbt_parameter.fine)])
                try:
                    tbmsect = TBMSegment(bbtparameter4seg, tbm)
                    kpiTbm.setKPI4SEG(alnCurr,tbmsect,bbtparameter4seg)
                except:
                    print bbt_parameter
                    print bbtparameter4seg
                    exit(-1)
            kpiTbm.updateKPI(alnCurr)
            kpiTbmList.append(kpiTbm)

for kpiTbm in kpiTbmList:
    lst = kpiTbm.saveBbtTbmKpis(sDBPath)
