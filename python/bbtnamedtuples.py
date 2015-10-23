from collections import namedtuple
# id	inizio	fine	L	perc	type	g_med	g_stddev	sigma_ci_avg	sigma_ci_stdev	mi_med	mi_stdev	ei_med	ei_stdev	cai_med	cai_stdev	gsi_med	gsi_stdev
BbtGeoitem = namedtuple('BbtGeoitem', ['id','inizio','fine','l','perc','type','g_med','g_stddev','sigma_ci_avg','sigma_ci_stdev','mi_med','mi_stdev','ei_med','ei_stdev','cai_med','cai_stdev','gsi_med','gsi_stdev'])
#id=Vertice altimetrico inizio(calcolato)	fine=Progressiva	Est	Nord	he=Quota altimetrica esistente	hp=Progetto quota altimetrica	co=Differenza quota altimetrica	tipo=Tipo di punto
BbtProfilo = namedtuple('BbtProfilo',['id','inizio','fine','est','nord','he','hp','co','tipo'])
BbtParameter =  namedtuple('BbtParameter',['inizio','fine','est','nord','he','hp','co','tipo','g_med','g_stddev','sigma_ci_avg','sigma_ci_stdev','mi_med','mi_stdev','ei_med','ei_stdev','cai_med','cai_stdev','gsi_med','gsi_stdev','profilo_id','geoitem_id'])
#BbtParameterEval =  namedtuple('BbtParameterEval',['fine','he','hp','co','gamma','sigma','mi','ei','cai','gsi'])

def bbtparameter_factory(cursor, row):
    return BbtParameter(*row)

def bbtprofilo_factory(cursor, row):
    return BbtProfilo(*row)

def bbtgeoitem_factory(cursor, row):
    return BbtGeoitem(*row)
