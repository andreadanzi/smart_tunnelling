import sqlite3, os, csv
import sys, getopt
from tbmconfig import tbms
from bbtutils import *
from bbtnamedtuples import *

import numpy as np
import matplotlib.pyplot as plt
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db
# danzi.tn@20151114 completamento lettura nuovi parametri e TBM
def main(argv):
    sParm = "p,parameter in \n"
    sParameterToShow = ""
    sTbmCode = ""
    for k in parmDict:
        sParm += "\t%s - %s\r\n" % (k,parmDict[k][0])
    sParm += "\n t,tbmcode  in \n"
    for k in tbms:
        sParm += "\t%s - Produttore %s di tipo %s per tunnel %s\r\n" % (k,tbms[k].manifacturer, tbms[k].type, tbms[k].alignmentCode)
    try:
        opts, args = getopt.getopt(argv,"hp:t:",["parameter=","tbmcode="])
    except getopt.GetoptError:
        print "readparameters.py -p <parameter> -t <tbmcode>\r\n where\r\n %s" % sParm
        sys.exit(2)
    if len(opts) < 1:
        print "readparameters.py -p <parameter> -t <tbmcode>\r\n where\r\n %s" % sParm
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "readparameters.py -p <parameter> -t <tbmcode>\r\n where\r\n %s" % sParm
            sys.exit()
        elif opt in ("-p", "--iparameter"):
            sParameterToShow = arg
        elif opt in ("-t", "--tbmcode"):
            sTbmCode = arg
    print 'sParameterToShow is ', sParameterToShow
    print 'sTbmCode is ', sTbmCode
    if sParameterToShow not in parmDict:
        print "Wrong parameter %s!\nreadparameters.py -p <parameter> -t <tbmcode>\r\n where\r\n %s" % (sParameterToShow,sParm)
        sys.exit(2)
    if len(sTbmCode) >0 and sTbmCode not in tbms:
        print "Wrong TBM Code %s!\nreadparameters.py -p <parameter> -t <tbmcode>\r\n where\r\n %s" % (sTbmCode,sParm)
        sys.exit(2)
    # mi metto nella directory corrente
    path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)

    ########## File vari: DB
    sDBName = bbtConfig.get('Database','dbname')
    sDBPath = os.path.join(os.path.abspath('..'), bbtConfig.get('Database','dbfolder'), sDBName)
    if not os.path.isfile(sDBPath):
        print "Errore! File %s inesistente!" % sDBPath
        exit(1)

    ########### Outupt Folder
    sDiagramsFolder = bbtConfig.get('Diagrams','folder')
    sDiagramsFolderPath = os.path.join(os.path.abspath('..'), sDiagramsFolder)
    # mi connetto al database
    conn = sqlite3.connect(sDBPath)
    # definisco il tipo di riga che vado a leggere, bbtparametereval_factory viene definita in bbtnamedtuples
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # quante iterazioni?
    sSql = "select max(BbtParameterEval.iteration_no) as max_iter from BbtParameterEval"
    cur.execute(sSql)
    bbtresult = cur.fetchone()
    M = float(bbtresult[0]) + 1.0
    print "Numero di iterazioni presenti %d" % M
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
    # Legget tutte le TBM
    sSql = """SELECT distinct
            bbtTbmKpi.tbmName
            FROM
            bbtTbmKpi"""
    if len(sTbmCode) > 0:
        sSql = sSql + " WHERE tbmName='%s'" % sTbmCode
    sSql = sSql + " ORDER BY bbtTbmKpi.tbmName"
    cur.execute(sSql)
    bbtresults = cur.fetchall()
    print "Sono presenti %d diverse TBM" % len(bbtresults)
    tbmColors = {}
    for bbtr in bbtresults:
        tbmColors[bbtr[0]] = main_colors.pop(0)
    bShowlTunnel = False
    for tun in tunnelArray:
        print "\r\n%s" % tun
        for tbmKey in tbmColors:
            cur.execute("SELECT * FROM BBtParameterEval  WHERE BBtParameterEval.tunnelNAme = '"+tun+"' AND tbmNAme='"+tbmKey+"' order by BBtParameterEval.iteration_no, BBtParameterEval.fine")
            bbtresults = cur.fetchall()
            # recupero tutti i parametri e li metto in una lista
            N = len(bbtresults)/M # No di segmenti
            pi = zeros(shape=(N,), dtype=float)
            he = zeros(shape=(N,), dtype=float)
            hp = zeros(shape=(N,), dtype=float)
            ti = zeros(shape=(N,), dtype=float)
            parm2show = zeros(shape=(N,M), dtype=float)
            tti = zeros(shape=(N,M), dtype=float)
            xti = zeros(shape=(N,M), dtype=float)
            i = 0
            pj = 0
            prev = 0.0
            outValues =[]
            for bbt_parametereval in bbtresults:
                j = int(bbt_parametereval['iteration_no'])
                if pj != j:
                    pj = j
                    prev = i = 0
                pi[i] = bbt_parametereval['fine']
                xti[i][j] = float(bbt_parametereval['dailyAdvanceRate'])
                tti[i][j] = prev + 10.0/xti[i][j]
                prev = tti[i][j]
                he[i] = bbt_parametereval['he']
                hp[i] = bbt_parametereval['hp']
                pVal = bbt_parametereval[sParameterToShow]
                if pVal == None:
                    pVal = 0
                pVal = float(pVal)
                outValues.append((float(bbt_parametereval['fine']), float(bbt_parametereval['he']),float(bbt_parametereval['hp']),pVal))
                parm2show[i][j] = pVal
                i += 1
            if N==0:
                print "\tPer TBM %s non ci sono dati in %s" % (tbmKey, tun)
            else:
                print "\tPer TBM %s ci sono %d righe" % (tbmKey, len(outValues))
                ylimInf = parmDict[sParameterToShow][2]
                ylimSup = parmDict[sParameterToShow][3]
                ymainInf = min(he)
                fig = plt.figure(figsize=(16, 10), dpi=100)
                ax1 = fig.add_subplot(111)
                ax1.set_ylim(0,max(he)+100)
                title("%s - %s" % (tun,tbmKey))
                ax1.plot(pi,he,'b-', linewidth=1)
                if bShowlTunnel:
                    ax1.plot(pi,hp,'k-', linewidth=1)
                ax1.set_xlabel('Progressiva (m)')
                ax1.set_ylabel('Quota (m)', color='b')
                for tl in ax1.get_yticklabels():
                    tl.set_color('b')
                ##########
                ax2 = ax1.twinx()
                if ylimSup > 0:
                    ax2.set_ylim(ylimInf,ylimSup)
                ax2.plot(pi,parm2show,'r-')
                ax2.set_ylabel("%s (%s)" % (parmDict[sParameterToShow][0],parmDict[sParameterToShow][1]), color='r')
                for tl in ax2.get_yticklabels():
                    tl.set_color('r')
                outputFigure(sDiagramsFolderPath,"bbt_%s_%s_%s.png" % ( tun.replace (" ", "_") , tbmKey,sParameterToShow))
                # esposrto in csv i valori di confronto
                csvfname=os.path.join(sDiagramsFolderPath,"bbt_%s_%s_%s.csv" % ( tun.replace (" ", "_") , tbmKey,sParameterToShow))
                with open(csvfname, 'wb') as f:
                    writer = csv.writer(f,delimiter=";")
                    writer.writerow(('fine','he','hp',sParameterToShow  ))
                    writer.writerows(outValues)
    conn.close()


if __name__ == "__main__":
   main(sys.argv[1:])
