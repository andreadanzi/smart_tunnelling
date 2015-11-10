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


now = datetime.datetime.now()
strnow = now.strftime("%Y%m%d%H%M%S")
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
kpiTbmList = []
for iIterationNo in range(500):
    # Per tutti i Tunnel
    for alnCurr in alnAll:
        # Per tutte le tbm
        for tbmKey in tbms:
            tbmData = tbms[tbmKey]
            # Se la TBM e' conforme al TUnnell
            if alnCurr.tbmKey in tbmData.alignmentCode:
                tbm = TBM(tbmData, 'V')
                kpiTbm = KpiTbm4Tunnel(alnCurr.description,iIterationNo)
                kpiTbm.setKPI4TBM(alnCurr,tbmKey,tbm,projectRefCost)
                bbt_evalparameters = []
                # cerco i segmenti che rientrano tra inizio e fine del Tunnell
                matches_params = [bpar for bpar in bbt_parameters if alnCurr.pkStart <= bpar.inizio and bpar.fine <= alnCurr.pkEnd]
                for bbt_parameter in matches_params:
                    bbtparameter4seg = build_bbtparameter4seg_from_bbt_parameter(bbt_parameter,normfunc_dicts[int(bbt_parameter.fine)])
                    try:
                        tbmsect = TBMSegment(bbtparameter4seg, tbm)
                        kpiTbm.setKPI4SEG(alnCurr,tbmsect,bbtparameter4seg)
                        bbt_evalparameters.append((strnow,iIterationNo,alnCurr.description, tbmKey, bbt_parameter.fine,bbt_parameter.he,bbt_parameter.hp,bbt_parameter.co,bbtparameter4seg.gamma,\
                                                        bbtparameter4seg.sci,bbtparameter4seg.mi,bbtparameter4seg.ei,bbtparameter4seg.cai,bbtparameter4seg.gsi,bbtparameter4seg.rmr,\
                                                        tbmsect.pkCe2Gl(bbt_parameter.fine),\
                                                        tbmsect.TunnelClosureAtShieldEnd*100. ,\
                                                        tbmsect.rockBurst.Val,\
                                                        tbmsect.frontStability.Ns,\
                                                        tbmsect.frontStability.lambdae,\
                                                        tbmsect.penetrationRate*1000. ,\
                                                        tbmsect.penetrationRateReduction*1000. ,\
                                                        tbmsect.contactThrust, \
                                                        tbmsect.torque, \
                                                        tbmsect.frictionForce, \
                                                        tbmsect.requiredThrustForce, \
                                                        tbmsect.availableThrust, \
                                                        tbmsect.dailyAdvanceRate, \
                                                        bbt_parameter.profilo_id, \
                                                        bbt_parameter.geoitem_id, \
                                                        bbt_parameter.title, \
                                                        bbtparameter4seg.sti, \
                                                        bbtparameter4seg.k0, \
                                                        tbmsect.t0, \
                                                        tbmsect.t1, \
                                                        tbmsect.t3, \
                                                        tbmsect.t4, \
                                                        tbmsect.t5 ) )
                    except:
                        print bbt_parameter
                        print bbtparameter4seg
                        exit(-1)
                kpiTbm.updateKPI(alnCurr)
                kpiTbm.saveBbtTbmKpis(sDBPath)
                insert_bbtparameterseval(sDBPath,bbt_evalparameters,iIterationNo)
