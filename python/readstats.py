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

    # definisco numero di iterazioni e numero di pk per ogni tunnel
    sSql = "select max(BbtParameterEval.iteration_no) as max_iter from BbtParameterEval"
    cur.execute(sSql)
    bbtresult = cur.fetchone()
    M = float(bbtresult[0]) + 1.0

    pkCountDict={}
    for tun in tunnelArray:
        sSql = "select count(distinct BbtParameterEval.fine) as pk_no from BbtParameterEval where BbtParameterEval.tunnelName='%s'" % tun
        cur.execute(sSql)
        bbtresult = cur.fetchone()
        pkNo = float(bbtresult[0])
        pkCountDict[tun]=pkNo

    # Legge tutte le TBM disponibili in tbmConfig per creare i dizionari di thrustLim e torqueLim
    thrustLim = {}
    torqueLim = {}
    for tbmName in tbms:
        tbm = tbms[tbmName]
        thrustLim[tbm.name]=tbm.auxiliaryThrustForce
        torqueLim[tbm.name]=tbm.breakawayTorque

    # carico in memoria tutti i record di BbtParmetersEval dove posso avere blocco scudo
    sSql = """SELECT  BbtParameterEval.tunnelName, BbtParameterEval.tbmName, BbtParameterEval.fine, count(*) as cnt
        FROM BbtParameterEval
        WHERE BbtParameterEval.tbmName !='XXX'
        AND ((BbtParameterEval.tbmName LIKE 'CE%' and BbtParameterEval.availableThrust< 3000) OR (BbtParameterEval.tbmName LIKE 'GL%' and BbtParameterEval.availableThrust< 5000))
        GROUP BY BbtParameterEval.tunnelName, BbtParameterEval.tbmName, BbtParameterEval.fine
        ORDER BY BbtParameterEval.tunnelName, BbtParameterEval.tbmName ASC, cnt DESC"""
    cur.execute(sSql)
    bbtresults = cur.fetchall()
    shieldBlockArray = []
    shieldBlockArray.append(('Tunnel', 'TBM', 'PK', 'no blocchi', 'sim x segm', 'tot segmenti', 'sim tot tunnel',  'no blocchi/sim tot tunnel',  'no blocchi/sim segmento'))
    for res in bbtresults:
        shieldBlockArray.append((res[0], res[1], res[2], res[3], M, pkCountDict[res[0]], M*pkCountDict[res[0]], res[3]/M/pkCountDict[res[0]], res[3]/M))
    # interrogo DB per vedere dove il torque e' maggiore di quello di base richiesto
    sSql = """SELECT  BbtParameterEval.tunnelName, BbtParameterEval.tbmName, BbtParameterEval.fine, BbtParameterEval.torque
        FROM BbtParameterEval
        WHERE BbtParameterEval.tbmName !='XXX'
        AND ((BbtParameterEval.tbmName LIKE 'CE%' and BbtParameterEval.torque> 7360) OR (BbtParameterEval.tbmName LIKE 'GL%' and BbtParameterEval.torque> 15900))
        ORDER BY BbtParameterEval.tunnelName, BbtParameterEval.tbmName ASC, BbtParameterEval.fine"""
    cur.execute(sSql)
    bbtresults = cur.fetchall()
    frontBlockArray = []
    frontBlockArray.append(('Tunnel', 'TBM', 'PK', 'no blocchi', 'sim x segm', 'tot segmenti', 'sim tot tunnel',  'no blocchi/sim tot tunnel',  'no blocchi/sim segmento'))
    tunnelRef=''
    tbmRef=''
    pkRef=0
    cntOut = 0
    resCnt = len(bbtresults)
    for i in range(0, resCnt-1):
        res=bbtresults[i]
        tunnel = res[0]
        tbm = res[1]
        pk = res[2]
        toAdd = res[3]>torqueLim[tbm]
        if tunnel == tunnelRef and tbm == tbmRef and pk == pkRef:
            # e' un altro punto da aggiungere
            # aggiurno la somma se toAdd
            if toAdd:
                cntOut+=1
        else:
            # ho iniziato un nuovo record
            # se non e' il primo appendo il risultato ottenuto
            if i>0 and cntOut>0:
                frontBlockArray.append((tunnel, tbm, pk, cntOut, M, pkCountDict[res[0]], M*pkCountDict[res[0]], cntOut/M/pkCountDict[res[0]], cntOut/M))
            # azzero i conteggi e i riferimenti
            tunnelRef=tunnel
            tbmRef=tbm
            pkRef=pk
            cntOut=0
            # aggiurno la somma se toAdd
            if toAdd:
                cntOut+=1
        # se e' l'ultima iterazione aggiungo il risultato
        if i == resCnt-1 and cntOut>0:
            frontBlockArray.append((tunnel, tbm, pk, cntOut, M, pkCountDict[res[0]], M*pkCountDict[res[0]], cntOut/M/pkCountDict[res[0]], cntOut/M))
    conn.close()
    # esposrto in csv
    with open('bloccoFronte.csv', 'wb') as f:
        writer = csv.writer(f,delimiter=",")
        writer.writerows(frontBlockArray)
        
    with open('bloccoScudo.csv', 'wb') as f:
        writer = csv.writer(f,delimiter=",")
        writer.writerows(shieldBlockArray)


if __name__ == "__main__":
   main(sys.argv[1:])
