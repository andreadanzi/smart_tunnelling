import sqlite3, os #, csv
import sys #, getopt
from tbmconfig import tbms
from bbtutils import *
from bbtnamedtuples import *
from readkpis import *
#from collections import defaultdict
from bbt_database import load_tbm_table, getDBConnection

#import numpy as np
#import matplotlib.pyplot as plt
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db
# danzi.tn@20151114 completamento lettura nuovi parametri e TBM
# danzi.tn@20151114 integrazione KPI in readparameters
# danzi.tn@20151117 plot percentile
# danzi.tn@20151117 plot aggregato per tipologia TBM
# danzi.tn@20151118 filtro per tipologia TBM
def main(argv):
    # mi metto nella directory corrente
    path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)

    ########## File vari: DB
    sDBName = bbtConfig.get('Database','dbname')
    sDBPath = os.path.join(os.path.abspath('..'), bbtConfig.get('Database','dbfolder'), sDBName)
    if not os.path.isfile(sDBPath):
        print "Errore! File %s inesistente!" % sDBPath
        exit(1)

    load_tbm_table(sDBPath, tbms)
    ########### Outupt Folder
    #sDiagramsFolder = bbtConfig.get('Diagrams','folder')
    #sDiagramsFolderPath = os.path.join(os.path.abspath('..'), sDiagramsFolder)
    # mi connetto al database
    conn = getDBConnection(sDBPath)
    # definisco il tipo di riga che vado a leggere, bbtparametereval_factory viene definita in bbtnamedtuples
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # Legge tutti i Tunnell
    sSql = """SELECT distinct
            bbtTbmKpi.tunnelName
            FROM
            bbtTbmKpi
            ORDER BY bbtTbmKpi.tunnelName"""
    cur.execute(sSql)
    bbtresults = cur.fetchall()
    print "Sono presenti %d diverse Gallerie" % len(bbtresults)
    tunnelArray = []
    for bbtr in bbtresults:
        tunnelArray.append(bbtr[0])
    # definisco le tbm di cui mi interessa valutare la performance
    #tbmToCheck = 'CE_DS_BBT_6.74; GL_DS_BBT_10.54; CE_DS_RBS_6.73; GL_DS_HRK_10.64'
    for tun in tunnelArray:
        noSegmTreated=0
        minThrust=20000.
        if tun == 'Galleria di linea direzione Sud':
            noSegmTreated = 0
        elif tun == 'Cunicolo esplorativo direzione Nord':
            noSegmTreated = 48
            minThrust = 12000.
        else:
            noSegmTreated = 39
        # conto il numero di pk presenti in quel tunnel
        sSql = "select count(distinct BbtParameterEval.fine) as pk_no from BbtParameterEval where BbtParameterEval.tunnelName='%s'" % tun
        cur.execute(sSql)
        bbtresult = cur.fetchone()
        pkNo = float(bbtresult[0])
        #allTbmData = []
        print "\r\n%f segmenti in %s" % (pkNo, tun)

        sSql = """SELECT bbtTbmKpi.tbmName, count(*) as cnt, BbtTbm.type, BbtTbm.manufacturer
                FROM
                bbtTbmKpi
                JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
                WHERE bbtTbmKpi.tunnelName = '"""+tun+"""'
                GROUP BY bbtTbmKpi.tbmName, BbtTbm.type, BbtTbm.manufacturer
                ORDER BY bbtTbmKpi.tbmName"""
        cur.execute(sSql)
        bbtresults = cur.fetchall()
        print "Sono presenti %d diverse TBM" % len(bbtresults)
        for tb in bbtresults:
            if 1==1: #tb[0] in tbmToCheck:
                tbmKey = tb[0]
                #tbmCount = float(tb[1])
                # danzi.tn@20151118 calcolo iterazioni per la TBM corrente (non e' detto che siano tutte uguali)
                sSql = "select max(BbtParameterEval.iteration_no) as max_iter from BbtParameterEval WHERE BbtParameterEval.tbmName ='%s'" % tbmKey
                cur.execute(sSql)
                bbtresult = cur.fetchone()
                M = float(bbtresult[0]) + 1.0
                #print "Numero massimo di iterazioni per %s sono %d" % (tbmKey, M)
                # seleziono tutti i segmenti dove l'available thrust e' inferiore al minimo richiesto
                sSql = "SELECT  count(*) as cnt, BbtParameterEval.fine\
                    FROM BbtParameterEval WHERE BbtParameterEval.tunnelName = '%s'\
                    AND BbtParameterEval.tbmName = '%s'\
                    AND BbtParameterEval.availableThrust< %f\
                    GROUP BY BbtParameterEval.fine\
                    ORDER BY cnt DESC" % (tun, tbmKey, minThrust)
                cur.execute(sSql)
                bbtresults = cur.fetchall()
                i = 1
                ptTot = 0.
                ptOut = 0.
                pkOut = 0.
                percMin = 1.
                percMax = 0.
                noOut = False

                for pk in bbtresults:
                    if i>noSegmTreated:
                        ptOut += pk[0] # aggiungo il numero di punti
                        percCur = pk[0]/M*100.
                        percMin = min(percMin, percCur)
                        percMax = max(percMax, percCur)
                        ptTot += M
                        pkOut += 1
                    i+=1
                percApplicazione = pkOut/pkNo*100.
                
                if ptTot>0:
                    percMed = ptOut/ptTot*100
                else:
                    percMin=0.
                    percMed=0.
                    
                print "%s con %s presenta potenziali problemi di blocco in %d sezioni (%f percento del tracciato)" % (tun, tbmKey, pkOut, percApplicazione)
                print "con percentuale minima %f massima %f e media %f" % (percMin, percMax, percMed)
    conn.close()

if __name__ == "__main__":
   main(sys.argv[1:])
