import sys, getopt
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
from tbmkpi import FrictionCoeff
# danzi.tn@20151114 gestione main e numero di iterazioni da linea comando
def main_loop(nIter):
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
        normfunc_dict = build_normfunc_dict(bbt_parameter,nIter)
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

    # danzi.tn@20151115 recepimento modifiche su InfoAlignment fatte da Garbriele
    #LEGGO I PARAMETRI DA FILE DI CONFIGURAZIONE
    fCShiledMin = bbtConfig.getfloat('Alignment','frictionCShiledMin')
    fCShiledMode = bbtConfig.getfloat('Alignment','frictionCShiledMode')
    fCShiledMax = bbtConfig.getfloat('Alignment','frictionCShiledMax')
    #CREO OGGETTO
    fcShield = FrictionCoeff(fCShiledMin,fCShiledMode,fCShiledMax)

    #LEGGO I PARAMETRI DA FILE DI CONFIGURAZIONE
    fCCutterdMin = bbtConfig.getfloat('Alignment','frictionCCutterMin')
    fCCutterMode = bbtConfig.getfloat('Alignment','frictionCCutterMode')
    fCCutterMax = bbtConfig.getfloat('Alignment','frictionCCutterMax')
    #CREO OGGETTO
    fcCutter =  FrictionCoeff(fCCutterdMin,fCCutterMode,fCCutterMax)

    alnAll = []
    aln=InfoAlignment('Galleria di linea direzione Sud', 'GLSUD', inizio_GLSUD, fine_GLSUD,fCCutterMode, fCShiledMode)
    alnAll.append(aln)
    aln=InfoAlignment('Cunicolo esplorativo direzione Nord', 'CE', delta_GLEST_CE - fine_CE, delta_GLEST_CE - inizio_CE , fCCutterMode, fCShiledMode)
    alnAll.append(aln)
    aln=InfoAlignment('Galleria di linea direzione Nord', 'GLNORD',inizio_GLEST, fine_GLEST, fCCutterMode, fCShiledMode)
    alnAll.append(aln)
    kpiTbmList = []
    for iIterationNo in range(nIter):
        # Per tutti i Tunnel
        print "iteration %d" % iIterationNo
        for alnCurr in alnAll:
            # Per tutte le tbm
            print "Galleria %s" % alnCurr.description
            for tbmKey in tbms:
                tbmData = tbms[tbmKey]
                print "TBM %s" % tbmKey
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
                        # danzi.tn@20151115 recepimento modifiche su InfoAlignment fatte da Garbriele
                        if iIterationNo > 2:
                            alnCurr.frictionCoeff = fcShield.rvs()
                            alnCurr.fiRi = fcCutter.rvs()
                        else:
                            alnCurr.frictionCoeff = fCShiledMode
                            alnCurr.fiRi = fCCutterMode
                        tbmsect = TBMSegment(bbtparameter4seg, tbm, alnCurr.fiRi, alnCurr.frictionCoeff)
                        kpiTbm.setKPI4SEG(alnCurr,tbmsect,bbtparameter4seg)
                        #danzi.tn@20151114 inseriti nuovi parametri calcolati su TunnelSegment
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
                                                        tbmsect.t5, \
                                                        tbmsect.InSituCondition.SigmaV, \
                                                        tbmsect.Excavation.Radius, \
                                                        tbmsect.Rock.E, \
                                                        tbmsect.MohrCoulomb.psi, \
                                                        tbmsect.Rock.Ucs, \
                                                        tbmsect.InSituCondition.Gsi, \
                                                        tbmsect.HoekBrown.Mi, \
                                                        tbmsect.HoekBrown.D, \
                                                        tbmsect.HoekBrown.Mb, \
                                                        tbmsect.HoekBrown.S, \
                                                        tbmsect.HoekBrown.A, \
                                                        tbmsect.HoekBrown.Mr, \
                                                        tbmsect.HoekBrown.Sr, \
                                                        tbmsect.HoekBrown.Ar, \
                                                        tbmsect.UrPi_HB(0.), \
                                                        tbmsect.Rpl, \
                                                        tbmsect.Picr, \
                                                        tbmsect.LDP_Vlachopoulos_2009(0.), \
                                                        tbmsect.LDP_Vlachopoulos_2009(tbm.Slen), \
                                                         ) )
                    kpiTbm.updateKPI(alnCurr)
                    kpiTbm.saveBbtTbmKpis(sDBPath)
                    insert_bbtparameterseval(sDBPath,bbt_evalparameters,iIterationNo)

    print "############################# Fine"



def main(argv):
    nIter = 0
    try:
        opts, args = getopt.getopt(argv,"hn:",["iteration_no="])
    except getopt.GetoptError:
        print "main_loop.py -n <number of iteration (positive integer)>"
        sys.exit(2)
    if len(opts) < 1:
        print "main_loop.py -n <number of iteration (positive integer)>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "main_loop.py -n <number of iteration (positive integer)>"
            sys.exit()
        elif opt in ("-n", "--iteration_no"):
            try:
                nIter = int(arg)
            except ValueError:
                print "main_loop.py -n <number of iteration (positive integer)>"
                sys.exit(2)
    if nIter > 0:
        main_loop(nIter)
    else:
        print "main_loop.py -n <number of iteration (positive integer)>"

if __name__ == "__main__":
   main(sys.argv[1:])
