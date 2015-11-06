import sqlite3, os, csv
from bbtutils import *
from bbtnamedtuples import *
from collections import defaultdict
from sets import Set
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db

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


def radar_data(kpiArray,cur):
    sGL_Nord = 'Galleria di linea direzione Nord'
    sGL_Sud = 'Galleria di linea direzione Sud'
    sCE_Nord = 'Cunicolo esplorativo direzione Nord'
    tunnelArray = [sGL_Nord,sGL_Sud,sCE_Nord]
    tunnelGroups = defaultdict(list)
    sKpis = "','".join(kpiArray)
    for tn in tunnelArray:
        tbmGroups = defaultdict(list)
        sSql = """select
            bbtTbmKpi.kpiKey,
            bbtTbmKpi.tbmName,
            avg(bbtTbmKpi.totalImpact) +2 as val
            from

            bbtTbmKpi
            WHERE
            bbtTbmKpi.tunnelName = '"""+tn+"""'
            AND bbtTbmKpi.kpiKey in ('"""+sKpis+"""')
            group by
            bbtTbmKpi.kpiKey,
            bbtTbmKpi.tbmName
            order by bbtTbmKpi.tbmName, bbtTbmKpi.kpiKey"""
        cur.execute(sSql)
        bbtresults = cur.fetchall()
        for bbtr in bbtresults:
            tbmGroups[bbtr[1]].append(float(bbtr[2]))
        tunnelGroups[tn].append(tbmGroups)
    ceNord=[]
    glNord=[]
    glSud=[]
    data = [
            kpiArray,
        (sCE_Nord, tunnelGroups[sCE_Nord]),
        (sGL_Nord, tunnelGroups[sGL_Nord]),
        (sGL_Sud, tunnelGroups[sGL_Sud])
    ]
    return data


# mi metto nella directory corrente
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

########## File vari: DB
sDBName = bbtConfig.get('Database','dbname')
sDBPath = os.path.join(os.path.abspath('..'), bbtConfig.get('Database','dbfolder'), sDBName)
if not os.path.isfile(sDBPath):
    print "Errore! File %s inesistente!" % sDBPath
    exit(1)

# mi connetto al database
conn = sqlite3.connect(sDBPath)
# definisco il tipo di riga che vado a leggere, bbtparametereval_factory viene definita in bbtnamedtuples
cur = conn.cursor()
print "start querying database  "
plotArray = []
print "#### P kpis"
kpiPArray = ['P1','P2','P3','P4','P5','P6']
kpiPdata = radar_data(kpiPArray,cur)
plotArray.append(kpiPdata)
print "#### G kpis"
kpiGArray = ['G1','G2','G5','G6','G7','G8','G11','G12','G13']
kpiGdata = radar_data(kpiGArray,cur)
plotArray.append(kpiGdata)
print "#### V kpis"
kpiVArray = ['V1','V2','V3','V4','V5','V6']
kpiVdata = radar_data(kpiVArray,cur)
plotArray.append(kpiVdata)
conn.close()

# These are the colors that will be used in the plot
colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']


fig = plt.figure(figsize=(9, 9))
fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
pltIndex = 1
inx = 0
labelsList = []
for pltItem in plotArray:
    spoke_labels = pltItem.pop(0)
    theta = radar_factory(len(spoke_labels), frame='polygon')
    for n, (title, case_data) in enumerate(pltItem):
        plot_data = []
        dataLen = 0
        for key_list in case_data:
            for tmb in key_list:
                labelsList.append(tmb)
                dataLen = len(key_list[tmb])
                plot_data.append(key_list[tmb])
        ax = fig.add_subplot(3, 3, pltIndex, projection='radar')
        plt.xticks(theta,spoke_labels)
        #plt.rgrids([2,4, 6, 8, 10,12])
        if pltIndex in range(4):
            ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1), horizontalalignment='center', verticalalignment='center')
        for d, color in zip(plot_data, colors):
            ax.plot(theta , d, color=color)
            ax.fill(theta, d, facecolor=color, alpha=0.15)
        pltIndex += 1


    ax.set_varlabels(spoke_labels)
# add legend relative to top-left plot
plt.subplot(3, 3, 1)
labels=set(labelsList)
print labels

legend = plt.legend(labels, loc=(0.9, .95), labelspacing=0.1)
plt.setp(legend.get_texts(), fontsize='small')
plt.figtext(0.5, 0.965, '5-Factor Solution Profiles Across Four Scenarios',
            ha='center', color='black', weight='bold', size='large')

plt.show()
