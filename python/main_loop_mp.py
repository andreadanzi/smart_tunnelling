import sys, getopt, logging
from TunnelSegment import *
from tbmconfig import *
from pylab import *
import matplotlib.pyplot as plt
from bbt_database import *
import sqlite3, os,  csv , datetime, time
from bbtutils import *
from bbtnamedtuples import *
from tbmkpi import *
from collections import namedtuple
from pprint import pprint
from tbmkpi import FrictionCoeff
from multiprocessing import cpu_count
from threading import Thread, Lock
from logging import handlers

# danzi.tn@20151119 profiling logging ed ottimizzazione thread
def createLogger(indx=0,name="main_loop"):
    log_level = bbtConfig.get('MAIN_LOOP','log_level')
    logging.basicConfig(level=eval("logging.%s"%log_level))
    formatter = logging.Formatter('%(levelname)s - %(asctime)s: %(message)s')
    main_logger = logging.getLogger("%s_%02d" % (name,indx))
    main_logger.propagate = False
    mainfh = handlers.RotatingFileHandler("%s_%02d.log" % (name,indx),maxBytes=50000, backupCount=5)
    mainfh.setFormatter(formatter)
    main_logger.addHandler(mainfh)
    return main_logger;


# danzi.tn@20151114 gestione main e numero di iterazioni da linea comando
# danzi.tn@20151117 versione multithread
# danzi.tn@20151118 gestione loop per singola TBM
def mp_producer(idWorker,  nIter,bbt_parameters,normfunc_dicts,loopTbms):
    start_time = time.time()
    now = datetime.datetime.now()
    strnow = now.strftime("%Y%m%d%H%M%S")
    main_logger = createLogger(idWorker,"mp_producer")
    main_logger.info("[%d]############################# Starts at %s" % (idWorker,strnow))
    #with plock:
    #    print "[%d]############################# Starts at %s" % (idWorker,strnow)


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
        iter_start_time = time.time()
        bbttbmkpis = []
        bbt_evalparameters = []
        iCheckEvalparameters = 0
        iCheckBbttbmkpis = 0
        # Per tutti i Tunnel
        main_logger.info("[%d]########### iteration %d - %d" % (idWorker, iIterationNo, idWorker*nIter + iIterationNo))
        #with plock:
        #    print "[%d]########### iteration %d - %d" % (idWorker, iIterationNo, idWorker*nIter + iIterationNo)
        for alnCurr in alnAll:
            for tbmKey in loopTbms:
                tbmData = loopTbms[tbmKey]
                # Se la TBM e' conforme al TUnnell
                if alnCurr.tbmKey in tbmData.alignmentCode:
                    main_logger.debug("[%d] %s - %s" % (idWorker,alnCurr.description, tbmKey ))
                    tbm = TBM(tbmData, 'V')
                    kpiTbm = KpiTbm4Tunnel(alnCurr.description, idWorker*nIter + iIterationNo)
                    iCheckBbttbmkpis += 1
                    kpiTbm.setKPI4TBM(alnCurr,tbmKey,tbm,projectRefCost)
                    # cerco i segmenti che rientrano tra inizio e fine del Tunnell
                    matches_params = [bpar for bpar in bbt_parameters if alnCurr.pkStart <= bpar.inizio and bpar.fine <= alnCurr.pkEnd]
                    main_logger.debug("[%d] Sono interessati %d pk" % (idWorker, len(matches_params) ))
                    for bbt_parameter in matches_params:
                        iCheckEvalparameters += 1
                        bbtparameter4seg = build_bbtparameter4seg_from_bbt_parameter(bbt_parameter,normfunc_dicts[int(bbt_parameter.fine)])
                        # danzi.tn@20151115 recepimento modifiche su InfoAlignment fatte da Garbriele
                        if iIterationNo > 2:
                            alnCurr.frictionCoeff = fcShield.rvs()
                            alnCurr.fiRi = fcCutter.rvs()
                        else:
                            alnCurr.frictionCoeff = fCShiledMode
                            alnCurr.fiRi = fCCutterMode
                        try:
                            tbmsect = TBMSegment(bbtparameter4seg, tbm, alnCurr.fiRi, alnCurr.frictionCoeff)
                        except Exception as e:
                            main_logger.error("[%d] %s, %s per pk %d TBMSegment va in errore: %s" % (idWorker, alnCurr.description, tbmKey, bbt_parameter.fine , e) )
                            main_logger.error("[%d] bbtparameter4seg = %s" % str(bbtparameter4seg))
                            continue
                        kpiTbm.setKPI4SEG(alnCurr,tbmsect,bbtparameter4seg)
                        #danzi.tn@20151114 inseriti nuovi parametri calcolati su TunnelSegment
                        bbt_evalparameters.append((strnow, idWorker*nIter + iIterationNo,alnCurr.description, tbmKey, bbt_parameter.fine,bbt_parameter.he,bbt_parameter.hp,bbt_parameter.co,bbtparameter4seg.gamma,\
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
                    bbttbmkpis += kpiTbm.getBbtTbmKpis()
                    sys.stdout.flush()
        iter_end_time = time.time()
        main_logger.debug("[%d]#### iteration %d - %d terminated in %d seconds" % (idWorker, iIterationNo, idWorker*nIter + iIterationNo, iter_end_time-iter_start_time))
        main_logger.debug("[%d]### Start inserting %d (%d) Parameters and %d (21x%d) KPIs" % (idWorker, len(bbt_evalparameters),iCheckEvalparameters,len(bbttbmkpis),iCheckBbttbmkpis))
        insert_eval4Iter(sDBPath,bbt_evalparameters,bbttbmkpis)
        insert_end_time = time.time()
        main_logger.debug("[%d]]### Insert terminated in %d seconds" % (idWorker,insert_end_time-iter_end_time))
    now = datetime.datetime.now()
    strnow = now.strftime("%Y%m%d%H%M%S")
    end_time = time.time()
    main_logger.info("[%d]############################# Ends at %s (%s seconds)" % (idWorker,strnow, end_time-start_time))
    #with plock:
    #    print "[%d]############################# Ends at %s (%s seconds)" % (idWorker,strnow, end_time-start_time)


if __name__ == "__main__":
    main_logger = createLogger()
    main_logger.info("__main__ Started!")
    mp_np = cpu_count() - 1
    argv = sys.argv[1:]
    nIter = 0
    bPerformTBMClean = False
    sTbmCode =""
    loopTbms = {}
    sParm = "\n t,tbmcode  in \n"
    for k in tbms:
        sParm += "\t%s - Produttore %s di tipo %s per tunnel %s\r\n" % (k,tbms[k].manifacturer, tbms[k].type, tbms[k].alignmentCode)
    try:
        opts, args = getopt.getopt(argv,"hn:dt:",["iteration_no=","deletetbms=","tbmcode="])
    except getopt.GetoptError:
        print "main_loop_mp.py -n <number of iteration (positive integer)> [-t <tbmcode>] \n\tCi sono %d processori disponibili\n%s" % (mp_np, sParm)
        sys.exit(2)
    if len(opts) < 1:
        print "main_loop_mp.py -n <number of iteration (positive integer)> [-t <tbmcode>]\n\tCi sono %d processori disponibili\n%s" % (mp_np, sParm)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "main_loop_mp.py -n <number of iteration (positive integer)> [-t <tbmcode>]\n\tCi sono %d processori disponibili\n%s" % (mp_np, sParm)
            sys.exit()
        elif opt in ("-n", "--iteration_no"):
            try:
                nIter = int(arg)
            except ValueError:
                print "main_loop_mp.py -n <number of iteration (positive integer)> [-t <tbmcode>]\n\tCi sono %d processori disponibili\n%s" % (mp_np, sParm)
                sys.exit(2)
        elif opt in ("-d", "--deletetbms"):
            bPerformTBMClean = True
        elif opt in ("-t", "--tbmcode"):
            sTbmCode = arg

            loopTbms[sTbmCode] = tbms[sTbmCode]
    if nIter > 0:
        number_of_threads = bbtConfig.getint('MAIN_LOOP','number_of_threads')
        wait_before_start = bbtConfig.getint('MAIN_LOOP','wait_before_start')
        mp_np = number_of_threads * mp_np
        main_logger.info("Richieste %d iterazioni" % nIter )
        # mi metto nella directory corrente
        path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(path)
        main_logger.info("Percorso di esecuzione %s" % path )
        ########## File vari: DB
        sDBName = bbtConfig.get('Database','dbname')
        sDBPath = os.path.join(os.path.abspath('..'), bbtConfig.get('Database','dbfolder'), sDBName)
        main_logger.info("Database utilizzato %s" % sDBPath )
        if not os.path.isfile(sDBPath):
            main_logger.error( "Errore! File %s inesistente!" % sDBPath)
        bbt_parameters = get_bbtparameters(sDBPath)
        if len(bbt_parameters) == 0:
            main_logger.error( "Attenzione! Nel DB %s non ci sono i dati necessari!" % sDBPath)

        main_logger.info("Ci sono %d pk" % len(bbt_parameters) )
        # lista delle funzioni random per ogni profilo
        normfunc_dicts = {}
        for bbt_parameter in bbt_parameters:
            normfunc_dict = build_normfunc_dict(bbt_parameter,nIter)
            normfunc_dicts[int(bbt_parameter.fine)] = normfunc_dict
        # danzi.tn@20151116
        if bPerformTBMClean:
            main_logger.info("Richiesta la cancellazione di tutti i dati")
            clean_all_eval_ad_kpi(sDBPath)
            compact_database(sDBPath)

        load_tbm_table(sDBPath, tbms)
        totIterations = mp_np*nIter
        main_logger.info("%d mp_producers, ognuno con %d iterazioni, totale iterazioni attese %d" % (mp_np , nIter, totIterations))
        sys.stdout.flush()
        if len(loopTbms) == 0:
            loopTbms = tbms
        deleteEval4Tbm(sDBPath,loopTbms)
        main_logger.info("Analisi per %d TBM" % len(loopTbms) )
        for tbk in loopTbms:
            main_logger.info( tbk )
        workers = [Thread(target=mp_producer, args=(i, nIter,bbt_parameters,normfunc_dicts,loopTbms))
                        for i in xrange(mp_np)]
        iw = 0
        start_time = time.time()
        for w in workers:
            main_logger.info( "Viene lanciato il thread numero %d" % iw)
            w.start()
            main_logger.info( "....attesa di %d secondi" % wait_before_start)
            time.sleep(wait_before_start)
            iw += 1
        # mp_consumer(nIter,mp_np,sDBPath)
        main_logger.info("Tutti i thread sono stati lanciati")
        for i in range(mp_np):
            workers[i].join()
        end_time = time.time()
        main_logger.info("Tutti i thread terminati, tempo totale %d secondi (in minuti = %f , in ore = %f ore)" % (end_time-start_time,(end_time-start_time)/60.,(end_time-start_time)/3600.))
        main_logger.info("Thread principale terminato")
    else:
        print "main_loop_mp.py -n <number of iteration (positive integer)>\n\tCi sono %d processori disponibili" % mp_np
