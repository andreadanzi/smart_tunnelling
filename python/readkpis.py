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
main_colors = ['#1f77b4',  '#ff7f0e', '#2ca02c',
                  '#d62728',  '#9467bd',
                  '#8c564b',  '#e377c2', '#7f7f7f',
                  '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']

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


def radar_data(kpiArray,tunnelArray,cur):
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
        cur.execute(sSql)
        bbtresults = cur.fetchall()
        for bbtr in bbtresults:
            tbmGroups[bbtr[1]].append((float(bbtr[2]),bbtr[0]))
        data.append((tn,tbmGroups))

    return data

def outputFigure(sDiagramsFolderPath, sFilename):
    imagefname=os.path.join(sDiagramsFolderPath,sFilename)
    if os.path.exists(imagefname):
        os.remove(imagefname)
    plt.savefig(imagefname,format='png', bbox_inches='tight', pad_inches=0)

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
cur = conn.cursor()
print "start querying database  "

# Legge tutti i Tunnell
sSql = """SELECT distinct
        bbtTbmKpi.tunnelName
        FROM
        bbtTbmKpi
        ORDER BY bbtTbmKpi.tunnelName"""
cur.execute(sSql)
bbtresults = cur.fetchall()
tunnelArray = []
for bbtr in bbtresults:
    tunnelArray.append(bbtr[0])
# Legget tutte le TBM
sSql = """SELECT distinct
        bbtTbmKpi.tbmName
        FROM
        bbtTbmKpi
        ORDER BY bbtTbmKpi.tbmName"""
cur.execute(sSql)
bbtresults = cur.fetchall()
tbmColors = {}
for bbtr in bbtresults:
    tbmColors[bbtr[0]] = main_colors.pop(0)

plotArray = []
print "#### P kpis"
kpiPArray = ['P1','P2','P3','P4','P5','P6']
kpiPdata = radar_data(kpiPArray,tunnelArray,cur)
plotArray.append(kpiPdata)
print "#### G kpis"
kpiGArray = ['G1','G2','G5','G6','G7','G8','G11','G12','G13']
kpiGdata = radar_data(kpiGArray,tunnelArray,cur)
plotArray.append(kpiGdata)
print "#### V kpis"
kpiVArray = ['V1','V2','V3','V4','V5','V6']
kpiVdata = radar_data(kpiVArray,tunnelArray,cur)
plotArray.append(kpiVdata)
conn.close()
print "##################### RADAR"
fig = plt.figure(figsize=(20, 12), dpi=200)
fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
pltIndex = 1
inx = 0
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

outputFigure(sDiagramsFolderPath,"radar_bbt_2015.png")
plt.close(fig)


print "##################### Sintesi G,P,V"

num_bins = 20
# mi connetto al database
conn = sqlite3.connect(sDBPath)
# definisco il tipo di riga che vado a leggere, bbtparametereval_factory viene definita in bbtnamedtuples
cur = conn.cursor()
for tun in tunnelArray:
    print "#### %s" % tun
    # Legget tutte le TBM di quel tunnel
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
    for bbtKpi in bbtKpiresults:
        sSql = """SELECT  BbtTbmKpi.tbmName, count(*)
                FROM
                bbtTbmKpi
                WHERE
                bbtTbmKpi.tunnelName = '"""+tun+"""'
                AND BbtTbmKpi.kpiKey LIKE '"""+ bbtKpi[0]+"""%'
    			GROUP BY BbtTbmKpi.tbmName
                ORDER BY BbtTbmKpi.tbmName """
        cur.execute(sSql)
        bbtTBMresults = cur.fetchall()
        tbmNo = len(bbtTBMresults)
        all_data = []

        for bbtTbm in bbtTBMresults:
            fig = plt.figure(figsize=(10, 6), dpi=75)
            ax = fig.add_subplot(111)
            sSql = """SELECT  sum(BbtTbmKpi.totalImpact), BbtTbmKpi.iterationNo
                    FROM
                    bbtTbmKpi
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""'
                    AND BbtTbmKpi.kpiKey like '"""+ bbtKpi[0]+"""%'
                    AND BbtTbmKpi.tbmName = '"""+ bbtTbm[0]+"""'
                    GROUP BY BbtTbmKpi.iterationNo
                    ORDER BY BbtTbmKpi.iterationNo """
            cur.execute(sSql)
            bbtImpResults = cur.fetchall()
            resNo = len(bbtImpResults)
            tbmData = []
            for bbtImp in bbtImpResults:
                tbmData.append( bbtImp[0])
            tbmMean = np.mean(tbmData)
            tbmSigma = np.std(tbmData)
            if tbmSigma > 0:
                all_data.append((str(bbtTbm[0]),tbmMean,tbmSigma,tbmData))
            n, bins, patches = ax.hist(tbmData,num_bins, normed=1, histtype ='stepfilled', color=tbmColors[bbtTbm[0]], alpha=0.3)
            y = mlab.normpdf(bins, tbmMean, tbmSigma)
            plt.plot(bins, y, '--', color=tbmColors[bbtTbm[0]])
            plt.xlabel("%s - valore medio %f" % (bbtKpi[0], tbmMean))
            plt.ylabel("Probabilita'")
            plt.axvline(tbmMean, color='r', linewidth=2)
            ax.yaxis.grid(True)
            ax.set_title("%s TBM %s (%s)" % (tun,bbtTbm[0],bbtKpi[0]))
            outputFigure(sDiagramsFolderPath,"bbt_%s_%sX_%s_hist.png" % ( tun.replace (" ", "_") , bbtKpi[0],bbtTbm[0]))
            plt.close(fig)
        fig = plt.figure(figsize=(10, 6), dpi=75)
        ax = fig.add_subplot(111)
        ax.yaxis.grid(True)
        tbmNames = map(lambda y:y[0],all_data)
        tbmMeans = map(lambda y:y[1],all_data)
        tbmSigmas = map(lambda y:y[2],all_data)
        tbmDatas = map(lambda y:y[3],all_data)
        ax.set_xticks([y+1 for y in range(len(tbmDatas)) ])
        ax.set_xlabel('TBMs')
        ax.set_ylabel(bbtKpi[0])
        # scatter([y+1 for y in range(len(tbmDatas)) ], tbmDatas[0])
        try:
            violin_parts = violinplot(tbmDatas,showmeans = True, points=50)
            idx = 0
            indMax = np.argmax(tbmMeans)
            for vp in violin_parts['bodies']:
                vp.set_facecolor(tbmColors[tbmNames[idx]])
                vp.set_edgecolor(tbmColors[tbmNames[idx]])
                vp.set_alpha(0.4)
                if idx==indMax:
                    vp.set_edgecolor('red')
                    vp.set_linewidth(2)
                idx +=1
            ax.set_title("%s, comparazione %s " % (tun,bbtKpi[0]))
            plt.setp(ax, xticks=[y+1 for y in range(len(tbmDatas))],xticklabels=tbmNames)
            outputFigure(sDiagramsFolderPath,"bbt_%s_%sX_violin.png" % (tun.replace (" ", "_") , bbtKpi[0]))
        except Exception as e:
            print e
            print "violin plot failed for  %s %s " % (bbtKpi[0], tun)
        plt.close(fig)
conn.close()


print "##################### Totali G+P+V"

num_bins = 20
# mi connetto al database
conn = sqlite3.connect(sDBPath)
# definisco il tipo di riga che vado a leggere, bbtparametereval_factory viene definita in bbtnamedtuples
cur = conn.cursor()
for tun in tunnelArray:
    print "#### %s" % tun
    sSql = """SELECT  BbtTbmKpi.tbmName, count(*)
            FROM
            bbtTbmKpi
            WHERE
            bbtTbmKpi.tunnelName = '"""+tun+"""'
			GROUP BY BbtTbmKpi.tbmName
            ORDER BY BbtTbmKpi.tbmName """
    cur.execute(sSql)
    bbtTBMresults = cur.fetchall()
    tbmNo = len(bbtTBMresults)
    all_data = []

    for bbtTbm in bbtTBMresults:
        fig = plt.figure(figsize=(10, 6), dpi=75)
        ax = fig.add_subplot(111)
        sSql = """SELECT  sum(BbtTbmKpi.totalImpact), BbtTbmKpi.iterationNo
                FROM
                bbtTbmKpi
                WHERE
                bbtTbmKpi.tunnelName = '"""+tun+"""'
                AND BbtTbmKpi.tbmName = '"""+ bbtTbm[0]+"""'
                GROUP BY BbtTbmKpi.iterationNo
                ORDER BY BbtTbmKpi.iterationNo """
        cur.execute(sSql)
        bbtImpResults = cur.fetchall()
        resNo = len(bbtImpResults)
        tbmData = []
        for bbtImp in bbtImpResults:
            tbmData.append( bbtImp[0])
        tbmMean = np.mean(tbmData)
        tbmSigma = np.std(tbmData)
        if tbmSigma > 0:
            all_data.append((str(bbtTbm[0]),tbmMean,tbmSigma,tbmData))
        n, bins, patches = ax.hist(tbmData,num_bins, normed=1, histtype ='stepfilled', color=tbmColors[bbtTbm[0]], alpha=0.3)
        y = mlab.normpdf(bins, tbmMean, tbmSigma)
        plt.plot(bins, y, '--', color=tbmColors[bbtTbm[0]])
        plt.xlabel("Valore medio %f" %  tbmMean)
        plt.ylabel("Probabilita'")
        plt.axvline(tbmMean, color='r', linewidth=2)
        ax.set_title("%s TBM %s" % (tun,bbtTbm[0]))
        outputFigure(sDiagramsFolderPath,"bbt_%s_%s_hist.png" % (tun.replace(" ", "_") , bbtTbm[0]))
        plt.close(fig)
    fig = plt.figure(figsize=(10, 6), dpi=75)
    ax = fig.add_subplot(111)
    ax.yaxis.grid(True)
    tbmNames = map(lambda y:y[0],all_data)
    tbmMeans = map(lambda y:y[1],all_data)
    tbmSigmas = map(lambda y:y[2],all_data)
    tbmDatas = map(lambda y:y[3],all_data)
    ax.set_xticks([y+1 for y in range(len(tbmDatas)) ])
    ax.set_xlabel('TBMs')
    ax.set_ylabel('Indicatore')
    # scatter([y+1 for y in range(len(tbmDatas)) ], tbmDatas[0])
    try:
        violin_parts = violinplot(tbmDatas,showmeans = True, points=50)
        idx = 0
        indMax = np.argmax(tbmMeans)
        for vp in violin_parts['bodies']:
            vp.set_facecolor(tbmColors[tbmNames[idx]])
            vp.set_edgecolor(tbmColors[tbmNames[idx]])
            vp.set_alpha(0.4)
            if idx==indMax:
                vp.set_edgecolor('red')
                vp.set_linewidth(2)
            idx +=1
        ax.set_title("%s, comparazione TBM" % tun)
        plt.setp(ax, xticks=[y+1 for y in range(len(tbmDatas))],xticklabels=tbmNames)
        outputFigure(sDiagramsFolderPath,"bbt_%s_violin.png" % tun.replace (" ", "_") )
    except Exception as e:
        print e
        print "violin plot failed for %s " %  tun
    plt.close(fig)
conn.close()

print "##################### Dettagli"
num_bins = 20
# mi connetto al database
conn = sqlite3.connect(sDBPath)
# definisco il tipo di riga che vado a leggere, bbtparametereval_factory viene definita in bbtnamedtuples
cur = conn.cursor()
for tun in tunnelArray:
    print "#### %s" % tun
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
    for bbtKpi in bbtKpiresults:
        sSql = """SELECT  BbtTbmKpi.tbmName, count(*)
                FROM
                bbtTbmKpi
                WHERE
                bbtTbmKpi.tunnelName = '"""+tun+"""'
                AND BbtTbmKpi.kpiKey = '"""+ bbtKpi[0]+"""'
    			GROUP BY BbtTbmKpi.tbmName
                ORDER BY BbtTbmKpi.tbmName """
        cur.execute(sSql)
        bbtTBMresults = cur.fetchall()
        tbmNo = len(bbtTBMresults)
        all_data = []

        for bbtTbm in bbtTBMresults:
            fig = plt.figure(figsize=(10, 6), dpi=75)
            ax = fig.add_subplot(111)
            sSql = """SELECT  BbtTbmKpi.totalImpact, BbtTbmKpi.avgImpact, BbtTbmKpi.probabilityScore
                    FROM
                    bbtTbmKpi
                    WHERE
                    bbtTbmKpi.tunnelName = '"""+tun+"""'
                    AND BbtTbmKpi.kpiKey = '"""+ bbtKpi[0]+"""'
                    AND BbtTbmKpi.tbmName = '"""+ bbtTbm[0]+"""'
                    ORDER BY BbtTbmKpi.iterationNo """
            cur.execute(sSql)
            bbtImpResults = cur.fetchall()
            resNo = len(bbtImpResults)
            tbmData = []
            avgImpacts = []
            probabilityScores = []
            for bbtImp in bbtImpResults:
                tbmData.append( bbtImp[0])
                avgImpacts.append( bbtImp[1])
                probabilityScores.append( bbtImp[2])
            tbmMean = np.mean(tbmData)
            tbmSigma = np.std(tbmData)
            if tbmSigma > 0:
                all_data.append((str(bbtTbm[0]),tbmMean,tbmSigma,tbmData))
            n, bins, patches = ax.hist(tbmData,num_bins, normed=1, histtype ='stepfilled', color=tbmColors[bbtTbm[0]], alpha=0.3)
            y = mlab.normpdf(bins, tbmMean, tbmSigma)
            plt.plot(bins, y, '--', color=tbmColors[bbtTbm[0]])
            plt.xlabel("%s - valore medio %f" % (bbtKpi[1], tbmMean))
            plt.ylabel("Probabilita'")
            plt.axvline(tbmMean, color='r', linewidth=2)
            ax.set_title("%s TBM %s (%s)" % (tun,bbtTbm[0],bbtKpi[0]))
            outputFigure(sDiagramsFolderPath,"bbt_%s_%s_%s_hist.png" % (tun.replace (" ", "_") , bbtKpi[0],bbtTbm[0] ))
            plt.close(fig)
        fig = plt.figure(figsize=(10, 6), dpi=75)
        ax = fig.add_subplot(111)
        ax.yaxis.grid(True)
        tbmNames = map(lambda y:y[0],all_data)
        tbmMeans = map(lambda y:y[1],all_data)
        tbmSigmas = map(lambda y:y[2],all_data)
        tbmDatas = map(lambda y:y[3],all_data)
        ax.set_xticks([y+1 for y in range(len(tbmDatas)) ])
        ax.set_xlabel('TBMs')
        ax.set_ylabel(bbtKpi[1])
        # scatter([y+1 for y in range(len(tbmDatas)) ], tbmDatas[0])
        try:
            violin_parts = violinplot(tbmDatas,showmeans = True, points=50)
            idx = 0
            indMax = np.argmax(tbmMeans)
            for vp in violin_parts['bodies']:
                vp.set_facecolor(tbmColors[tbmNames[idx]])
                vp.set_edgecolor(tbmColors[tbmNames[idx]])
                vp.set_alpha(0.4)
                if idx==indMax:
                    vp.set_edgecolor('red')
                    vp.set_linewidth(2)
                idx +=1
            ax.set_title("%s, comparazione %s (%s)" % (tun,bbtKpi[1],bbtKpi[0]))
            plt.setp(ax, xticks=[y+1 for y in range(len(tbmDatas))],xticklabels=tbmNames)
            outputFigure(sDiagramsFolderPath,"bbt_%s_%s_violin.png" % (tun.replace (" ", "_") , bbtKpi[0] ))
        except Exception as e:
            print e
            print "violin plot failed for  %s %s " % (bbtKpi[0], tun)
        plt.close(fig)
conn.close()


print "#################### fineee"
