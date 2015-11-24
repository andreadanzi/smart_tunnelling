import sqlite3, os, csv
from bbtutils import *
import matplotlib.mlab as mlab
from bbtnamedtuples import *
from collections import defaultdict
from sets import Set
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db
# These are the colors that will be used in the plot
# danzi.tn@20151124 output SVG
def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts


# danzi.tn@20151118 filtro per tipologia TBM (sTypeToGroup)
def radar_data(kpiArray,tunnelArray,cur,tbmColors,bGroupTypes, sTypeToGroup):
    data = []
    data.append(kpiArray)
    # Raggruppa per ogni tunnel gli Indicatori
    sKpis = "','".join(kpiArray)
    for tn in tunnelArray:
        tbmGroups = defaultdict(list)
        kpiArr = []
        sSql = """SELECT
            bbtTbmKpi.kpiKey,
            avg(bbtTbmKpi.totalImpact) as val
            FROM

            bbtTbmKpi
            WHERE
            bbtTbmKpi.tunnelName = '"""+tn+"""'
            AND bbtTbmKpi.kpiKey in ('"""+sKpis+"""')
            group by
            bbtTbmKpi.kpiKey
            having val > 0
            order by bbtTbmKpi.kpiKey"""
        cur.execute(sSql)
        bbtresults = cur.fetchall()
        for bbtr in bbtresults:
            kpiArr.append(bbtr[0])
        sHavingKpis = "','".join(kpiArr)
        sSql = """SELECT
            bbtTbmKpi.kpiKey,
            bbtTbmKpi.tbmName,
            avg(bbtTbmKpi.totalImpact) as val
            FROM

            bbtTbmKpi
            WHERE
            bbtTbmKpi.tunnelName = '"""+tn+"""'
            AND bbtTbmKpi.kpiKey in ('"""+sHavingKpis+"""')
            group by
            bbtTbmKpi.kpiKey,
            bbtTbmKpi.tbmName
            order by bbtTbmKpi.tbmName, bbtTbmKpi.kpiKey"""
        if len(sTypeToGroup) > 0:
            sSql = """SELECT
                bbtTbmKpi.kpiKey,
                bbtTbmKpi.tbmName,
                avg(bbtTbmKpi.totalImpact) as val
                FROM
                bbtTbmKpi
                JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
                WHERE
                bbtTbmKpi.tunnelName = '"""+tn+"""'
                AND bbtTbmKpi.kpiKey in ('"""+sHavingKpis+"""')
                AND BbtTbm.type = '"""+sTypeToGroup+"""'
                group by
                bbtTbmKpi.kpiKey,
                bbtTbmKpi.tbmName
                order by bbtTbmKpi.tbmName, bbtTbmKpi.kpiKey"""
        elif bGroupTypes:
            sSql = """SELECT
                bbtTbmKpi.kpiKey,
                BbtTbm.type,
                avg(bbtTbmKpi.totalImpact) as val
                FROM
                bbtTbmKpi
                JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
                WHERE
                bbtTbmKpi.tunnelName = '"""+tn+"""'
                AND bbtTbmKpi.kpiKey in ('"""+sHavingKpis+"""')
                group by
                bbtTbmKpi.kpiKey,
                BbtTbm.type
                order by BbtTbm.type, bbtTbmKpi.kpiKey"""

        cur.execute(sSql)
        bbtresults = cur.fetchall()
        for bbtr in bbtresults:
            sTbmHidden = replaceTBMName(bbtr[1])
            tbmGroups[sTbmHidden].append((float(bbtr[2]),bbtr[0]))
        data.append((tn,tbmGroups))

    return data

def plotRadarKPIS(cur,tunnelArray,sDiagramsFolderPath,tbmColors,bGroupTypes, sTypeToGroup):
    plotArray = []
    kpiPArray = ['P1','P2','P3','P4','P5','P6']
    kpiPdata = radar_data(kpiPArray,tunnelArray,cur,tbmColors,bGroupTypes, sTypeToGroup)
    plotArray.append(kpiPdata)
    kpiGArray = ['G1','G2','G5','G6','G7','G8','G11','G12','G13']
    kpiGdata = radar_data(kpiGArray,tunnelArray,cur,tbmColors,bGroupTypes, sTypeToGroup)
    plotArray.append(kpiGdata)
    kpiVArray = ['V1','V2','V3','V4','V5','V6']
    kpiVdata = radar_data(kpiVArray,tunnelArray,cur,tbmColors,bGroupTypes, sTypeToGroup)
    plotArray.append(kpiVdata)
    fig = plt.figure(figsize=(30, 20), dpi=200)
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    pltIndex = 1
    for pltItem in plotArray:
        spoke_labels = pltItem.pop(0)
        for n, (title, key_list) in enumerate(pltItem):
            plot_data = []
            color_data = []
            tbm_name = []
            pkeys = []
            for tmb in key_list:
                pkeys = map(lambda y:y[1],key_list[tmb])
                plot_data.append(key_list[tmb])
                color_data.append(tbmColors[tmb])
                tbm_name.append(tmb)
            theta = radar_factory(len(pkeys), frame='polygon')
            ax = fig.add_subplot(3, 3, pltIndex, projection='radar')
            plt.xticks(theta,pkeys)
            for d, color in zip(plot_data, color_data):
                pd = map(lambda y:y[0],d)
                pk = map(lambda y:y[1],d)
                ax.plot(theta , pd, color=color, linewidth=1.3)
                ax.fill(theta, pd, facecolor=color, alpha=0.15)

            if pltIndex in range(4):
                ax.set_title(title, weight='bold', size='medium', position=(0.1, 1.1), horizontalalignment='center', verticalalignment='center')
                plt.subplot(3, 3, pltIndex)
                legend = plt.legend(tbm_name, loc=(-0.7, 0.4), labelspacing=0.1, title="Codici TBM")
                plt.setp(legend.get_texts(), fontsize='small')
            ax.set_varlabels(pkeys)

            pltIndex += 1

    plt.figtext(0.5, 0.965, 'Valutazione TBM su 3 gallerie BBT Mules 2 - 3',
                ha='center', color='black', weight='bold', size='large')
    sFileName = "radar_bbt_2015.svg"
    if bGroupTypes:
        sFileName = "radar_bbt_2015_by_types.svg"
    if len(sTypeToGroup)>0:
        sFileName = "radar_bbt_2015_%s.svg" % sTypeToGroup
    outputFigure(sDiagramsFolderPath,sFileName,format="svg")
    plt.close(fig)


def plotKPIS(cur,sDiagramsFolderPath,tun,tbmName,tbmColors,bGroupTypes, sTypeToGroup,bPrintHist=False):
    kpiDescrDict = {'G':'Geologia', 'P':'Produzione', 'V':'Parametri Vari'}
    num_bins = 20
    # print "#### %s" % tun
    # Legget tutti i KPI di quel tunnel
    sSql = """SELECT  SUBSTR(BbtTbmKpi.kpiKey,1,1)  as kpiKey , count(*)
            FROM
            bbtTbmKpi
            WHERE
            bbtTbmKpi.tunnelName = '"""+tun+"""'
			GROUP BY SUBSTR(BbtTbmKpi.kpiKey,1,1)"""
    cur.execute(sSql)
    bbtKpiresults = cur.fetchall()
    kpiNo = len(bbtKpiresults)
    kpiKeyList = defaultdict(list)
    currentKpi = ""
    currentTbm = ""
    all_data = []
    for bbtKpi in bbtKpiresults:
        sSql = """SELECT  BbtTbmKpi.tbmName, count(*)
                FROM
                bbtTbmKpi
                WHERE
                bbtTbmKpi.tunnelName = '"""+tun+"""'
                AND BbtTbmKpi.kpiKey LIKE '"""+ bbtKpi[0]+"""%'
    			"""
        if len(tbmName)>0:
            sSql = sSql + " AND BbtTbmKpi.tbmName = '%s'" % tbmName
        sSql = sSql + " GROUP BY BbtTbmKpi.tbmName ORDER BY BbtTbmKpi.tbmName "
        if bGroupTypes:
            sSql = """SELECT BbtTbm.type  , count(*) as cnt_tbmtype
                    FROM
                    BbtTbm
					WHERE
					BbtTbm.name IN (
                    SELECT DISTINCT BbtTbmKpi.tbmName
					FROM bbtTbmKpi
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""'
                    AND BbtTbmKpi.kpiKey LIKE '"""+ bbtKpi[0]+"""%')
        			"""
            if len(tbmName)>0:
                sSql = sSql + " AND BbtTbm.type = '%s'" % tbmName
            sSql = sSql + " GROUP BY BbtTbm.type ORDER BY BbtTbm.type "
        cur.execute(sSql)
        bbtTBMresults = cur.fetchall()
        tbmNo = len(bbtTBMresults)
        bViolin = False
        for bbtTbm in bbtTBMresults:
            sSql = """SELECT  sum(BbtTbmKpi.totalImpact), BbtTbmKpi.iterationNo
                    FROM
                    bbtTbmKpi
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""'
                    AND BbtTbmKpi.kpiKey like '"""+ bbtKpi[0]+"""%'
                    AND BbtTbmKpi.tbmName = '"""+ bbtTbm[0]+"""'
                    GROUP BY BbtTbmKpi.iterationNo
                    ORDER BY BbtTbmKpi.iterationNo """
            if bGroupTypes:
                sSql = "SELECT  sum(BbtTbmKpi.totalImpact) / %s , BbtTbmKpi.iterationNo " % bbtTbm[1]
                sSql += " FROM bbtTbmKpi JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName WHERE "
                sSql += " bbtTbmKpi.tunnelName = '"+tun+"' AND BbtTbmKpi.kpiKey like '" +bbtKpi[0]+"%'  AND BbtTbm.type = '"+bbtTbm[0]+"'"
                sSql += " GROUP BY BbtTbmKpi.iterationNo ORDER BY BbtTbmKpi.iterationNo "
            cur.execute(sSql)
            bbtImpResults = cur.fetchall()
            tbmData = []
            for bbtImp in bbtImpResults:
                tbmData.append( bbtImp[0])
            tbmMean = np.mean(tbmData)
            tbmSigma = 0
            resNo = len(bbtImpResults)
            if bPrintHist:
                fig = plt.figure(figsize=(10, 6), dpi=75)
                ax = fig.add_subplot(111)
                if resNo>2:
                    bViolin = True
                    tbmSigma = np.std(tbmData)
                    n, bins, patches = ax.hist(tbmData,num_bins, normed=1, histtype ='stepfilled', color=tbmColors[bbtTbm[0]], alpha=0.3)
                    y = mlab.normpdf(bins, tbmMean, tbmSigma)
                    plt.plot(bins, y, '--', color=tbmColors[bbtTbm[0]])
                    plt.xlabel("%s - valore medio %f" % (bbtKpi[0], tbmMean))
                    plt.ylabel("Probabilita'")
                    plt.axvline(tbmMean, color='r', linewidth=2)

                    ax.yaxis.grid(True)
                    ax.set_title("%s TBM %s (%s)" % (tun, replaceTBMName(bbtTbm[0]),bbtKpi[0]))
                    outputFigure(sDiagramsFolderPath,"bbt_%s_%sX_%s_hist.svg" % ( tun.replace (" ", "_") , bbtKpi[0], replaceTBMName(bbtTbm[0])), format="svg")
                else:
                    x = range(resNo)
                    plt.plot(x, tbmData, 'o', color=tbmColors[bbtTbm[0]])
                    plt.xlabel("Iterazioni")
                    plt.ylabel("Totale indicatori di tipo %s=%f" % (bbtKpi[0],tbmMean))
                    ax.yaxis.grid(True)
                    ax.set_title("%s TBM %s (%s)" % (tun, replaceTBMName(bbtTbm[0]),bbtKpi[0]))
                    outputFigure(sDiagramsFolderPath,"bbt_%s_%sX_%s_iterations.svg" % ( tun.replace (" ", "_") , bbtKpi[0], replaceTBMName(bbtTbm[0])), format="svg")
                plt.close(fig)
            all_data.append(( bbtKpi[0], str(bbtTbm[0]),tbmMean,tbmSigma,tbmData, kpiDescrDict[bbtKpi[0]]))
    return all_data


def plotTotalsKPIS(cur,sDiagramsFolderPath,tun,tbmName,tbmColors,bGroupTypes, sTypeToGroup,bPrintHist=False):
    num_bins = 20
    # print "#### %s" % tun
    sSql = "SELECT  BbtTbmKpi.tbmName, count(*) FROM  bbtTbmKpi   WHERE  bbtTbmKpi.tunnelName = '%s'" % tun
    if len(tbmName) > 0:
        sSql = sSql + " AND BbtTbmKpi.tbmName = '%s'" % tbmName
    sSql = sSql + " GROUP BY BbtTbmKpi.tbmName ORDER BY BbtTbmKpi.tbmName "
    if bGroupTypes:
        sSql = """SELECT BbtTbm.type  , count(*) as cnt_tbmtype
                FROM
                BbtTbm
                WHERE
                BbtTbm.name IN (
                SELECT DISTINCT BbtTbmKpi.tbmName
                FROM bbtTbmKpi
                WHERE
                bbtTbmKpi.tunnelName = '"""+tun+"""')
                """
        if len(tbmName)>0:
            sSql = sSql + " AND BbtTbm.type = '%s'" % tbmName
        sSql = sSql + " GROUP BY BbtTbm.type ORDER BY BbtTbm.type "
    cur.execute(sSql)
    bbtTBMresults = cur.fetchall()
    tbmNo = len(bbtTBMresults)
    all_data = []
    bViolin = False
    for bbtTbm in bbtTBMresults:
        sSql = """SELECT  sum(BbtTbmKpi.totalImpact), BbtTbmKpi.iterationNo
                FROM
                bbtTbmKpi
                WHERE
                bbtTbmKpi.tunnelName = '"""+tun+"""'
                AND BbtTbmKpi.tbmName = '"""+ bbtTbm[0]+"""'
                GROUP BY BbtTbmKpi.iterationNo
                ORDER BY BbtTbmKpi.iterationNo """
        if bGroupTypes:
            sSql = """SELECT  sum(BbtTbmKpi.totalImpact)/"""+str(bbtTbm[1])+""", BbtTbmKpi.iterationNo
                    FROM
                    bbtTbmKpi
                    JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""'
                    AND BbtTbm.type = '"""+ bbtTbm[0]+"""'
                    GROUP BY BbtTbmKpi.iterationNo
                    ORDER BY BbtTbmKpi.iterationNo """
        cur.execute(sSql)
        bbtImpResults = cur.fetchall()
        tbmData = []
        for bbtImp in bbtImpResults:
            tbmData.append( bbtImp[0])
        tbmMean = np.mean(tbmData)
        tbmSigma = 0
        resNo = len(bbtImpResults)
        if bPrintHist:
            fig = plt.figure(figsize=(10, 6), dpi=75)
            ax = fig.add_subplot(111)
            if resNo>2:
                bViolin = True
                tbmSigma = np.std(tbmData)
                n, bins, patches = ax.hist(tbmData,num_bins, normed=1, histtype ='stepfilled', color=tbmColors[bbtTbm[0]], alpha=0.3)
                y = mlab.normpdf(bins, tbmMean, tbmSigma)
                plt.plot(bins, y, '--', color=tbmColors[bbtTbm[0]])
                plt.xlabel("Valore medio %f" %  tbmMean)
                plt.ylabel("Probabilita'")
                plt.axvline(tbmMean, color='r', linewidth=2)
                ax.yaxis.grid(True)
                ax.set_title("%s TBM %s" % (tun, replaceTBMName(bbtTbm[0])))
                outputFigure(sDiagramsFolderPath,"bbt_%s_%s_hist.svg" % (tun.replace(" ", "_") ,  replaceTBMName( bbtTbm[0])), format="svg")
            else:
                x = range(resNo)
                plt.plot(x, tbmData, 'o', color=tbmColors[bbtTbm[0]])
                plt.xlabel("Iterazioni")
                plt.ylabel("Valore KPI Totale=%f" % tbmMean)
                ax.yaxis.grid(True)
                ax.set_title("%s TBM %s" % (tun, replaceTBMName(bbtTbm[0])))
                outputFigure(sDiagramsFolderPath,"bbt_%s_%s_iterations.svg" % (tun.replace(" ", "_") ,  replaceTBMName(bbtTbm[0])), format="svg")
            plt.close(fig)
        all_data.append(('KPI', str(bbtTbm[0]),tbmMean,tbmSigma,tbmData, 'Totale KPI'))
    return all_data

def plotDetailKPIS(cur,sDiagramsFolderPath,tun,tbmName,tbmColors,bGroupTypes, sTypeToGroup,bPrintHist=False):
    num_bins = 20
    # print "#### %s" % tun
    # Legget tutte le TBM di quel tunnel
    sSql = """SELECT  BbtTbmKpi.kpiKey,BbtTbmKpi.kpiDescr, count(*)
            FROM
            bbtTbmKpi
            WHERE
            bbtTbmKpi.tunnelName = '"""+tun+"""' AND BbtTbmKpi.totalImpact > 0.0
			GROUP BY BbtTbmKpi.kpiKey
            ORDER BY BbtTbmKpi.kpiKey"""
    cur.execute(sSql)
    bbtKpiresults = cur.fetchall()
    kpiNo = len(bbtKpiresults)
    kpiKeyList = defaultdict(list)
    currentKpi = ""
    currentTbm = ""
    all_data = []
    for bbtKpi in bbtKpiresults:
        sSql = "SELECT  BbtTbmKpi.tbmName, count(*) as cnt_tbmtype FROM bbtTbmKpi WHERE bbtTbmKpi.tunnelName = '%s' AND BbtTbmKpi.kpiKey = '%s'" % (tun, bbtKpi[0])
        if len(tbmName) > 0:
            sSql = sSql + " AND BbtTbmKpi.tbmName = '%s'" % tbmName
        sSql = sSql + " GROUP BY BbtTbmKpi.tbmName ORDER BY BbtTbmKpi.tbmName "
        if bGroupTypes:
            sSql = """SELECT BbtTbm.type  , count(*) as cnt_tbmtype
                    FROM
                    BbtTbm
                    WHERE
                    BbtTbm.name IN (
                    SELECT DISTINCT BbtTbmKpi.tbmName
                    FROM bbtTbmKpi
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""'
                    AND BbtTbmKpi.kpiKey = '"""+ bbtKpi[0]+"""')
                    """
            if len(tbmName)>0:
                sSql = sSql + " AND BbtTbm.type = '%s'" % tbmName
            sSql = sSql + " GROUP BY BbtTbm.type ORDER BY BbtTbm.type "
        cur.execute(sSql)
        bbtTBMresults = cur.fetchall()
        tbmNo = len(bbtTBMresults)
        bViolin = False
        for bbtTbm in bbtTBMresults:
            sSql = """SELECT  BbtTbmKpi.totalImpact, BbtTbmKpi.avgImpact, BbtTbmKpi.probabilityScore
                    FROM
                    bbtTbmKpi
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""'
                    AND BbtTbmKpi.kpiKey = '"""+ bbtKpi[0]+"""'
                    AND BbtTbmKpi.tbmName = '"""+ bbtTbm[0]+"""'
                    ORDER BY BbtTbmKpi.iterationNo """
            if bGroupTypes:
                sSql = """SELECT  avg(BbtTbmKpi.totalImpact), avg(BbtTbmKpi.avgImpact), avg(BbtTbmKpi.probabilityScore), BbtTbm.type
                        FROM
                        bbtTbmKpi
                        JOIN BbtTbm on BbtTbm.name = bbtTbmKpi.tbmName
                        WHERE
                        bbtTbmKpi.tunnelName = '"""+tun+"""'
                        AND BbtTbmKpi.kpiKey = '"""+ bbtKpi[0]+"""'
                        AND BbtTbm.type = '"""+ bbtTbm[0]+"""'
                        GROUP BY BbtTbm.type
                        ORDER BY BbtTbmKpi.iterationNo """
            cur.execute(sSql)
            bbtImpResults = cur.fetchall()
            tbmData = []
            avgImpacts = []
            probabilityScores = []
            for bbtImp in bbtImpResults:
                tbmData.append( bbtImp[0])
                avgImpacts.append( bbtImp[1])
                probabilityScores.append( bbtImp[2])
            resNo = len(bbtImpResults)
            tbmMean = np.mean(tbmData)
            tbmSigma = 0
            if bPrintHist:
                fig = plt.figure(figsize=(10, 6), dpi=75)
                ax = fig.add_subplot(111)
                if resNo>2:
                    bViolin = True
                    tbmSigma = np.std(tbmData)
                    n, bins, patches = ax.hist(tbmData,num_bins, normed=1, histtype ='stepfilled', color=tbmColors[bbtTbm[0]], alpha=0.3)
                    y = mlab.normpdf(bins, tbmMean, tbmSigma)
                    plt.plot(bins, y, '--', color=tbmColors[bbtTbm[0]])
                    plt.xlabel("%s - valore medio %f" % (bbtKpi[1], tbmMean))
                    plt.ylabel("Probabilita'")
                    plt.axvline(tbmMean, color='r', linewidth=2)
                    ax.set_title("%s TBM %s (%s)" % (tun, replaceTBMName(bbtTbm[0]),bbtKpi[0]))
                    ax.yaxis.grid(True)
                    outputFigure(sDiagramsFolderPath,"bbt_%s_%s_%s_hist.svg" % (tun.replace (" ", "_") , bbtKpi[0], replaceTBMName(bbtTbm[0]) ), format="svg")
                else:
                    x = range(resNo)
                    plt.plot(x, tbmData, 'o', color=tbmColors[bbtTbm[0]])
                    plt.xlabel("Iterazioni")
                    plt.ylabel("Valore KPI %s = %f" % (bbtKpi[1],tbmMean))
                    ax.yaxis.grid(True)
                    ax.set_title("%s TBM %s (%s)" % (tun, replaceTBMName(bbtTbm[0]), bbtKpi[0]))
                    outputFigure(sDiagramsFolderPath,"bbt_%s_%s_%s_iterations.svg" %  (tun.replace (" ", "_") , bbtKpi[0], replaceTBMName(bbtTbm[0]) ), format="svg")
                plt.close(fig)
            all_data.append((bbtKpi[0], str(bbtTbm[0]),tbmMean,tbmSigma,tbmData, bbtKpi[1]))
    return all_data
