import sqlite3, os, csv
import sys, getopt
from tbmconfig import tbms
from bbtutils import *
from bbtnamedtuples import *
from readkpis import *
from collections import defaultdict
from bbt_database import load_tbm_table

import numpy as np
import matplotlib.pyplot as plt
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db
# danzi.tn@20151114 completamento lettura nuovi parametri e TBM
# danzi.tn@20151114 integrazione KPI in readparameters
# danzi.tn@20151117 plot percentile
# danzi.tn@20151117 plot aggregato per tipologia TBM
def main(argv):
    sParm = "p,parameter in \n"
    sParameterToShow = ""
    sTbmCode = ""
    sTypeToGroup = ""
    bPrintHist = False
    bShowProfile = False
    bShowRadar = False
    bShowKPI = False
    bShowAllKpi = False
    bShowDetailKPI = False
    bGroupTypes = False
    bShowAdvance = False
    for k in parmDict:
        sParm += "\t%s - %s\r\n" % (k,parmDict[k][0])
    sParm += "\n t,tbmcode  in \n"
    for k in tbms:
        sParm += "\t%s - Produttore %s di tipo %s per tunnel %s\r\n" % (k,tbms[k].manifacturer, tbms[k].type, tbms[k].alignmentCode)
    sParm += "\n\t-r => generazione diagramma Radar per tutte le TBM\n"
    sParm += "\n\t-k => generazione diagrammi KPI G, P e V\n"
    sParm += "\n\t-a => generazione diagrammi KPI G + P + V\n"
    sParm += "\n\t-d => generazione diagrammi KPI di Dettaglio\n"
    sParm += "\n\t-i => generazione delle distribuzioni per ogni tipo di KPI selezionato\n"
    sParm += "\n\t-c => raggruppamento per tipologia di TBM\n"
    sParm += "\n\t-m => per tipologia di TBM indicata viene eseguito raggruppamento per Produttore\n"
    try:
        opts, args = getopt.getopt(argv,"hp:t:rkadicm:",["parameter=","tbmcode=","radar","kpi","allkpi","detailkpi","histograms","tbmtype","manufacturer"])
    except getopt.GetoptError:
        print "readparameters.py -p <parameter> [-t <tbmcode>] [-rkai]\r\n where\r\n %s" % sParm
        sys.exit(2)
    if len(opts) < 1:
        print "readparameters.py -p <parameter> [-t <tbmcode>] [-rkai]\r\n where\r\n %s" % sParm
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "readparameters.py -p <parameter> [-t <tbmcode>] [-rkai]\r\n where\r\n %s" % sParm
            sys.exit()
        elif opt in ("-p", "--iparameter"):
            sParameterToShow = arg
            bShowProfile = True
            if sParameterToShow =='adv':
                bShowAdvance = True
        elif opt in ("-t", "--tbmcode"):
            sTbmCode = arg
        elif opt in ("-r", "--radar"):
            bShowRadar = True
        elif opt in ("-k", "--kpi"):
            bShowKPI = True
        elif opt  in ("-a", "--allkpi"):
            bShowAllKpi = True
        elif opt in ("-d", "--detailkpi"):
            bShowDetailKPI = True
        elif opt in ("-i", "--histograms"):
            bPrintHist = True
        elif opt in ("-c", "--tbmtype"):
            bGroupTypes = True
        elif opt in ("-m", "--manufacturer"):
            sTypeToGroup = arg
            bGroupTypes = True

    if len(sParameterToShow) >0 and sParameterToShow not in parmDict:
        print "Wrong parameter %s!\nreadparameters.py -p <parameter> [-t <tbmcode>] [-rkai]\r\n where\r\n %s" % (sParameterToShow,sParm)
        sys.exit(2)
    if len(sTbmCode) >0 and sTbmCode not in tbms:
        print "Wrong TBM Code %s!\nreadparameters.py -p <parameter> -t <tbmcode> [-rkai]\r\n where\r\n %s" % (sTbmCode,sParm)
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

    load_tbm_table(sDBPath, tbms)
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
    print "Numero massimo di iterazioni presenti %d" % M
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
    # Legge tutte le TBM
    sSql = """SELECT bbtTbmKpi.tbmName, BbtTbm.type, BbtTbm.manufacturer, count(*) as cnt
            FROM
            bbtTbmKpi
			JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
			GROUP BY bbtTbmKpi.tbmName, BbtTbm.type, BbtTbm.manufacturer
            ORDER BY bbtTbmKpi.tbmName"""
    if bGroupTypes:
        sSql = """SELECT BbtTbm.type, count(*) as cnt
                FROM
                bbtTbmKpi
    			JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
    			GROUP BY BbtTbm.type
                ORDER BY BbtTbm.type"""
    cur.execute(sSql)
    bbtresults = cur.fetchall()
    # associare un colore diverso ad ogni TBM
    tbmColors = {}
    for bbtr in bbtresults:
        tbmColors[bbtr[0]] = main_colors.pop(0)
    bShowlTunnel = False
    for tun in tunnelArray:
        allTbmData = []
        print "\r\n%s" % tun
        sSql = """SELECT bbtTbmKpi.tbmName, count(*) as cnt, BbtTbm.type, BbtTbm.manufacturer
                FROM
                bbtTbmKpi
                JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
                WHERE bbtTbmKpi.tunnelName = '"""+tun+"""'
                GROUP BY bbtTbmKpi.tbmName, BbtTbm.type, BbtTbm.manufacturer
                ORDER BY bbtTbmKpi.tbmName"""
        # Filtro sulla eventuale TBM passata come parametro
        if len(sTbmCode) > 0:
            sSql = """SELECT bbtTbmKpi.tbmName, count(*) as cnt, BbtTbm.type, BbtTbm.manufacturer
                    FROM
                    bbtTbmKpi
        			JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
                    WHERE bbtTbmKpi.tunnelName = '"""+tun+"""' AND BbtTbm.name = '"""+sTbmCode+"""'
        			GROUP BY bbtTbmKpi.tbmName, BbtTbm.type, BbtTbm.manufacturer
                    ORDER BY bbtTbmKpi.tbmName"""
        if bGroupTypes:
            sSql = """SELECT BbtTbm.type, count(*) as cnt_tbmtype
                    FROM
                    BbtTbm
					WHERE
					BbtTbm.name IN (
                    SELECT DISTINCT BbtTbmKpi.tbmName
					FROM bbtTbmKpi
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""')
        			GROUP BY BbtTbm.type
                    ORDER BY BbtTbm.type"""
        cur.execute(sSql)
        bbtresults = cur.fetchall()
        print "Sono presenti %d diverse TBM" % len(bbtresults)
        for tb in bbtresults:
            tbmKey = tb[0]
            tbmCount = float(tb[1])
            if bShowProfile:
                # danzi.tn@20151118 calcolo iterazioni per la TBM corrente (non e' detto che siano tutte uguali)
                sSql = "select max(BbtParameterEval.iteration_no) as max_iter from BbtParameterEval WHERE BbtParameterEval.tbmName ='%s'" % tbmKey
                if bGroupTypes:
                    sSql = "select max(BbtParameterEval.iteration_no) as max_iter from BbtParameterEval JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName WHERE BbtTbm.type ='%s'" % tbmKey
                cur.execute(sSql)
                bbtresult = cur.fetchone()
                M = float(bbtresult[0]) + 1.0
                print "Numero massimo di iterazioni per %s sono %d" % (tbmKey, M)

                sSql = "SELECT BBtParameterEval.*, BBtParameterEval.t1 +BBtParameterEval.t3 +BBtParameterEval.t4 +BBtParameterEval.t5 as tsum, 1 as adv FROM BBtParameterEval  WHERE BBtParameterEval.tunnelNAme = '"+tun+"' AND tbmNAme='"+tbmKey+"' order by BBtParameterEval.iteration_no, BBtParameterEval.fine"
                if bGroupTypes:
                    sSql = "SELECT BBtParameterEval.*, BBtParameterEval.t1 +BBtParameterEval.t3 +BBtParameterEval.t4 +BBtParameterEval.t5 as tsum, 1 as adv FROM BBtParameterEval JOIN BbtTbm on BbtTbm.name = BBtParameterEval.tbmName WHERE BBtParameterEval.tunnelNAme = '"+tun+"' AND BbtTbm.type='"+tbmKey+"' order by BBtParameterEval.iteration_no, BBtParameterEval.fine, BbtTbm.type"
                cur.execute(sSql)
                bbtresults = cur.fetchall()
                # recupero tutti i parametri e li metto in una lista
                N = len(bbtresults)/M # No di segmenti
                pi = zeros(shape=(N,), dtype=float)
                he = zeros(shape=(N,), dtype=float)
                hp = zeros(shape=(N,), dtype=float)
                ti = zeros(shape=(N,), dtype=float)
                parm2show = zeros(shape=(N,M), dtype=float)
                mean2Show = zeros(shape=(N,3), dtype=float)
                tti = zeros(shape=(N,M), dtype=float)
                xti = zeros(shape=(N,M), dtype=float)
                i = 0
                pj = 0
                prev = 0.0
                outValues =[]
                if tun not in ('Galleria di linea direzione Sud'):
                    bbtresults.reverse()
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
                    if bShowAdvance:
                        pVal = tti[i][j]
                        if bGroupTypes:
                            pVal = pVal/tbmCount
                    outValues.append([int(bbt_parametereval['iteration_no']),float(bbt_parametereval['fine']), float(bbt_parametereval['he']),float(bbt_parametereval['hp']),pVal])
                    parm2show[i][j] = pVal
                    i += 1
                for i in range(int(N)):
                    pki_mean = np.nanmean(parm2show[i,:])
                    pki_std = np.nanstd(parm2show[i,:])
                    mean2Show[i][0] = pki_mean - 2*pki_std
                    mean2Show[i][1] = pki_mean
                    mean2Show[i][2] = pki_mean + 2*pki_std
                i=0
                for outVal in outValues:
                    outValues[i].append(mean2Show[i%N][1])
                    outValues[i].append(mean2Show[i%N][0])
                    outValues[i].append(mean2Show[i%N][2])
                    i += 1
                if N==0:
                    print "\tPer TBM %s non ci sono dati in %s" % (tbmKey, tun)
                else:
                    ylimInf = parmDict[sParameterToShow][2]
                    ylimSup = parmDict[sParameterToShow][3]
                    ymainInf = min(he)
                    fig = plt.figure(figsize=(32, 20), dpi=100)
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
                    ax2.yaxis.grid(True)
                    if ylimSup > 0:
                        ax2.set_ylim(ylimInf,ylimSup)
                    ax2.plot(pi,parm2show,'r.',markersize=1.0)
                    ax2.plot(pi,mean2Show[:,0],'m-',linewidth=0.5, alpha=0.4)
                    ax2.plot(pi,mean2Show[:,1],'g-',linewidth=2, alpha=0.6)
                    ax2.plot(pi,mean2Show[:,2],'c-',linewidth=0.5, alpha=0.4)
                    ax2.set_ylabel("%s (%s)" % (parmDict[sParameterToShow][0],parmDict[sParameterToShow][1]), color='r')
                    for tl in ax2.get_yticklabels():
                        tl.set_color('r')
                    outputFigure(sDiagramsFolderPath,"bbt_%s_%s_%s.png" % ( tun.replace (" ", "_") , tbmKey,sParameterToShow))
                    plt.close(fig)
                    # esposrto in csv i valori di confronto
                    csvfname=os.path.join(sDiagramsFolderPath,"bbt_%s_%s_%s.csv" % ( tun.replace (" ", "_") , tbmKey,sParameterToShow))
                    with open(csvfname, 'wb') as f:
                        writer = csv.writer(f,delimiter=";")
                        writer.writerow(('iterazione','fine','he','hp',sParameterToShow,'media','min95' ,'max95' ))
                        writer.writerows(outValues)
            if bShowKPI:
                print "%s %s" % (tun, tbmKey)
                allTbmData += plotKPIS(cur,sDiagramsFolderPath,tun,tbmKey,tbmColors,bGroupTypes, sTypeToGroup, bPrintHist)
            if bShowAllKpi:
                allTbmData += plotTotalsKPIS(cur,sDiagramsFolderPath,tun,tbmKey,tbmColors,bGroupTypes, sTypeToGroup, bPrintHist)
            if bShowDetailKPI:
                allTbmData += plotDetailKPIS(cur,sDiagramsFolderPath,tun,tbmKey,tbmColors,bGroupTypes, sTypeToGroup, bPrintHist)
        if len(allTbmData) > 0:
            dictKPI = defaultdict(list)
            dictDescr = {}
            listToExport = []
            for item in allTbmData:
                key = item[0]
                dictDescr[key] = item[-1]
                dictKPI[key].append( item[1:-1] )
                listToExport.append(item[:4])
            # esposrto in csv i valori di confronto
            csvfname=os.path.join(sDiagramsFolderPath,"bbt_%s_all_data.csv" %  tun.replace (" ", "_") )
            with open(csvfname, 'wb') as f:
                writer = csv.writer(f,delimiter=";")
                writer.writerow(('kpi','tbm','medie','sigma'  ))
                writer.writerows(listToExport)
            for key in dictKPI:
                keyDescr = dictDescr[key]
                allTbmData = dictKPI[key]
                fig = plt.figure(figsize=(22, 10), dpi=75)
                ax = fig.add_subplot(111)
                ax.yaxis.grid(True)
                tbmNames = map(lambda y:y[0],allTbmData)
                tbmMeans = map(lambda y:y[1],allTbmData)
                tbmSigmas = map(lambda y:y[2],allTbmData)
                tbmDatas = map(lambda y:y[3],allTbmData)
                ax.set_xticks([y+1 for y in range(len(tbmDatas)) ])
                ax.set_xlabel('TBMs')
                ax.set_ylabel("%s - %s" % (key,keyDescr))
                ax.set_title("%s, comparazione %s " % (tun,keyDescr))
                xind = np.arange(len(tbmDatas))
                plotColors =[]
                for tk in tbmNames:
                    plotColors.append(tbmColors[tk])
                if len(tbmDatas[0]) < 3:
                    #Stampa per quando len(tbmDatas) < 3
                    width = 0.35
                    plt.bar(xind, tbmMeans, width,color=plotColors, yerr=tbmSigmas)
                    plt.xticks(xind + width/2., tbmNames)
                else:
                    try:
                        violin_parts = violinplot(tbmDatas,showmeans = True, points=50)
                        idx = 0
                        indMin = np.argmin(tbmMeans)
                        for vp in violin_parts['bodies']:
                            vp.set_facecolor(tbmColors[tbmNames[idx]])
                            vp.set_edgecolor(tbmColors[tbmNames[idx]])
                            vp.set_alpha(0.4)
                            if idx==indMin:
                                vp.set_edgecolor('y')
                                vp.set_linewidth(2)
                            idx +=1

                        plt.setp(ax, xticks=[y+1 for y in range(len(tbmDatas))],xticklabels=tbmNames)
                    except Exception as e:
                        print "Impossibile generare violin di %s per: %s" % ( key ,e)
                        width = 0.35
                        plt.bar(xind, tbmMeans, width,color=plotColors, yerr=tbmSigmas)
                        plt.xticks(xind + width/2., tbmNames)

                outputFigure(sDiagramsFolderPath,"bbt_%s_%s_comp.png" % (tun.replace (" ", "_") , key))
                plt.close(fig)


    if bShowRadar:
        plotRadarKPIS(cur,tunnelArray,sDiagramsFolderPath,tbmColors,bGroupTypes, sTypeToGroup)
    conn.close()

if __name__ == "__main__":
   main(sys.argv[1:])
