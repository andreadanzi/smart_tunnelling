import sqlite3
import csv, pprint, os
import sys
from collections import defaultdict
from collections import namedtuple
from bbtnamedtuples import BbtGeoitem, BbtParameter, BbtProfilo, BbtReliability
from collections import OrderedDict
import numpy as np
from pylab import *
from scipy.stats import *
import xlrd
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
geosec_index = defaultdict(list)
class Geoitem(object):
    pkend = 0
    profile_list = []
    geo_list = []
    pk_index = defaultdict(list)

    def __init__(self, pkend):
        self.pkend = float(pkend)
        Geoitem.pk_index[pkend].append(self)

    def getPkend():
        return pkend

    def appendProfile(self, profile):
        self.profile_list.append(profile)

    def appendGeoitem(self, geoitem):
        self.profile_list.append(geoitem)


    @classmethod
    def find_or_new_by_pkend(cls,pkend):
        gseg = cls.find_by_pkend(pkend)
        if gseg is None:
            gseg = Geoitem(pkend)
        return gseg

    @classmethod
    def find_by_pkend(cls, pkend):
        gfound=None
        for idx_pkend, geosegment in Geoitem.pk_index.iteritems():
            # print  "%f-%f <= %f" % (idx_pkend,geosegment.pkend, pkend)
            if idx_pkend <= pkend:
                gfound = geosegment
        return gfound

dPk = defaultdict(list)
geoList = []
with open('gl_nord.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    for row in spamreader:
        splitted = row[0].split('+')
        strVal = ''.join(splitted)
        pkend = float(strVal)
        geoseg = Geoitem(pkend)
        geoList.append(geoseg)
        dPk[strVal].append(row[1:])
        print "%f - %s " % (pkend, ', '.join(row[1:]))

#Affidabilita modello GEO
fname = 'valutazione_modello_geo.xls'
book = xlrd.open_workbook(fname)
xl_sheet = book.sheet_by_name(u'ce')
headrow = xl_sheet.row(3)  # header
row = xl_sheet.row(4)  # first row
num_cols = xl_sheet.ncols
reliability_list = []
for row_idx in range(4, xl_sheet.nrows):
    rowvalues=[]
    for col_idx in range(0, num_cols):  # Iterate through columns
        cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
        rowvalues.append(cell_obj.value)
    reliability_item = BbtReliability(*rowvalues)
    reliability_list.append(reliability_item)
# salvo in db BbtReliability
conn = sqlite3.connect('bbt_mules_2-3.db')
c = conn.cursor()
c.execute('delete from BbtReliability')
for rel in reliability_list:
    c.execute('insert into BbtReliability (id ,inizio, fine , gmr_class, gmr_val, reliability, eval_var) values (?,?,?,?,?,?,?)', rel)
conn.commit()
conn.close()

# caratteristiche GEO da tavola
fname = 'bbt_ce.xls'
book = xlrd.open_workbook(fname)
xl_sheet = book.sheet_by_name(u'geoce')
headrow = xl_sheet.row(2)  # header
row = xl_sheet.row(3)  # first row
num_cols = xl_sheet.ncols
geoseg_list = []
for row_idx in range(3, xl_sheet.nrows):
    rowvalues=[]
    for col_idx in range(0, num_cols):  # Iterate through columns
        cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
        rowvalues.append(cell_obj.value)
    geoseg = BbtGeoitem(*rowvalues)
    geoseg_list.append(geoseg)
    reliab_match = [rel for rel in reliability_list if rel.inizio < geoseg.fine <= rel.fine]
    for reli in reliab_match:
        print "reliab %d-%s finisce in %f vicino a Geoseg %f" % (reli.id,reli.gmr_class, reli.fine,geoseg.fine)
    geosec_index[geoseg.fine].append(geoseg)
# salvo in db BbtGeoitem e BbtReliability
conn = sqlite3.connect('bbt_mules_2-3.db')
c = conn.cursor()
c.execute('delete from BbtGeoitem')
for geoseg in geoseg_list:
    c.execute('insert into BbtGeoitem (id,inizio,fine,l,perc,type,g_med,g_stddev,sigma_ci_avg,sigma_ci_stdev,mi_med,mi_stdev,ei_med,ei_stdev,cai_med,cai_stdev,gsi_med,gsi_stdev,rmr_med,rmr_stdev ) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', geoseg)
conn.commit()
conn.close()

# Profilo
profilo='Report_CE-10metri.xls'
bprofilo = xlrd.open_workbook(profilo)
civilReport_sheet = bprofilo.sheet_by_name(u'CivilReport')
headrow = civilReport_sheet.row(16)  # header
row = civilReport_sheet.row(17)  # first row

from xlrd.sheet import ctype_text

print('(Column #) type:value')
for idx, cell_obj in enumerate(row):
    cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
    print('(%s) %s %s' % (idx, cell_type_str, cell_obj.value))
num_cols = civilReport_sheet.ncols
profilo_list = []
prev_prog = 0
for row_idx in range(17, civilReport_sheet.nrows):
    keepRow = False
    rowvalues=[]
    for col_idx in range(1, num_cols):  # Iterate through columns
        cell_obj = civilReport_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
        if col_idx == 1:
            s1 = cell_obj.value.split(',')
            dec = int(s1[1])
            s2 = s1[0].split('+')
            strVal = ''.join(s2)
            pkend = float(strVal)
            if dec == 0 and int(pkend) % 10 == 0:
                rowvalues.append(prev_prog)
                keepRow = True
                rowvalues.append(pkend-10)
                rowvalues.append(pkend)
                prev_prog += 1
        else:
            if keepRow and col_idx == 2:
                rowvalues.append(cell_obj.value)
            if keepRow and col_idx == 3:
                rowvalues.append(cell_obj.value)
            if keepRow and col_idx == 4: #quota altimetrica 1.871,894m
                s1 = cell_obj.value.split(",")
                if len(s1) > 1:
                    s2 = s1[0].split('.')
                    strVal = ''.join(s2)
                    he = float(strVal)
                    rowvalues.append(he)
                else:
                    rowvalues.append(0)
            if keepRow and col_idx == 5: #quota progetto 704,988m
                s1 = cell_obj.value.split(",")
                if len(s1) > 1:
                    s2 = s1[0].split('.')
                    strVal = ''.join(s2)
                    hp = float(strVal)
                    rowvalues.append(hp)
                else:
                    rowvalues.append(0)
            if keepRow and col_idx == 6: #copertura 1.166,906m
                s1 = cell_obj.value.split(",")
                if len(s1) > 1:
                    s2 = s1[0].split('.')
                    strVal = ''.join(s2)
                    co = float(strVal)
                    rowvalues.append(co)
                else:
                    rowvalues.append(0)
            if keepRow and col_idx == 7:
                rowvalues.append(cell_obj.value)
    if rowvalues:
        bbtpro = BbtProfilo(*rowvalues)
        profilo_list.append(bbtpro)

# salvo profilo
conn = sqlite3.connect('bbt_mules_2-3.db')
c = conn.cursor()
c.execute('delete from BbtProfilo')
for bbtpro in profilo_list:
    c.execute('insert into BbtProfilo (id,inizio,fine,est,nord,he,hp,co,tipo) values (?,?,?,?,?,?,?,?,?)', bbtpro)
conn.commit()
conn.close()

# BbtParameter rappresenta il segmento unitario con i parametri geologici base valorizzati secondo i dati provenienti dalle tavole geologiche
geoitems=defaultdict(list)
for bbtpro in profilo_list:
    #print "profilo %f-%f" % (bbtpro.inizio, bbtpro.fine)
    matches = [geoseg for geoseg in geoseg_list if geoseg.inizio <  bbtpro.fine <= geoseg.fine  ]
    for geoseg in matches:
        # print "\tgeosec %f-%f" % ( geoseg.inizio, geoseg.fine )
        bbtprofound = [pro for pro in geoitems[geoseg.fine] if pro.fine == bbtpro.fine]
        if len(bbtprofound) == 0:
            geoitems[geoseg.fine].append(bbtpro)

bbtpar_items = []
for k in geoitems:
    print "geoseg %d-%d" % (geosec_index[k][0].inizio,geosec_index[k][0].fine)
    totItem = 0
    px = []
    gx = []
    for geosec in geosec_index[k]:
        itemNo = int(geosec.perc*len( geoitems[k]))
        if itemNo == 0:
            itemNo = 1
        px.append(itemNo)
        gx.append(geosec)
        totItem = sum(px)
        print "%s - %f - %d" % (geosec.type, geosec.perc,itemNo)
    missing = len( geoitems[k])-totItem
    print "%d vs %d, missing %d" % (totItem,len( geoitems[k]), missing )
    for i in range(missing):
        px[i] = px[i] + 1
    print px
    prev = 0
    for i in range(len(px)):
        geosec = gx[i]
        for j in range(prev,prev+px[i]):
            pk = geoitems[k][j]
            tmparr = [pk.inizio , pk.fine, pk.est, pk.nord, pk.he, pk.hp, pk.co, pk.tipo, geosec.g_med,geosec.g_stddev,geosec.sigma_ci_avg,geosec.sigma_ci_stdev,geosec.mi_med,geosec.mi_stdev,geosec.ei_med,geosec.ei_stdev,geosec.cai_med,geosec.cai_stdev,geosec.gsi_med,geosec.gsi_stdev,geosec.rmr_med,geosec.rmr_stdev,pk.id,geosec.id]
            #print "\t profile %f-%f has geoclass ending in %f with perc %f" % (pk.inizio,pk.fine,geosec.fine,geosec.perc)
            bbtpar = BbtParameter(*tmparr)
            bbtpar_items.append(bbtpar)
        prev += px[i]
# salvo parametri
conn = sqlite3.connect('bbt_mules_2-3.db')
c = conn.cursor()
c.execute('delete from BbtParameter')
for bbtpar in bbtpar_items:
    c.execute('insert into BbtParameter (inizio,fine,est,nord,he,hp,co,tipo,g_med,g_stddev,sigma_ci_avg,sigma_ci_stdev,mi_med,mi_stdev,ei_med,ei_stdev,cai_med,cai_stdev,gsi_med,gsi_stdev,rmr_med,rmr_stdev,profilo_id,geoitem_id) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', bbtpar)
conn.commit()
conn.close()
