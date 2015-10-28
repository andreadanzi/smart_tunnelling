from collections import namedtuple
# id	inizio	fine	L	perc	type	g_med	g_stddev	sigma_ci_avg	sigma_ci_stdev	mi_med	mi_stdev	ei_med	ei_stdev	cai_med	cai_stdev	gsi_med	gsi_stdev
BbtGeoitem = namedtuple('BbtGeoitem', ['id','inizio','fine','l','perc','type','g_med','g_stddev','sigma_ci_avg','sigma_ci_stdev','mi_med','mi_stdev','ei_med','ei_stdev','cai_med','cai_stdev','gsi_med','gsi_stdev','rmr_med','rmr_stdev'])
#id=Vertice altimetrico inizio(calcolato)	fine=Progressiva	Est	Nord	he=Quota altimetrica esistente	hp=Progetto quota altimetrica	co=Differenza quota altimetrica	tipo=Tipo di punto
BbtProfilo = namedtuple('BbtProfilo',['id','inizio','fine','est','nord','he','hp','co','tipo'])
BbtParameter =  namedtuple('BbtParameter',['inizio','fine','est','nord','he','hp','co','tipo','g_med','g_stddev','sigma_ci_avg','sigma_ci_stdev','mi_med','mi_stdev','ei_med','ei_stdev','cai_med','cai_stdev','gsi_med','gsi_stdev','rmr_med','rmr_stdev','profilo_id','geoitem_id'])
BbtReliability = namedtuple('BbtReliability',['id','inizio','fine','gmr_class','gmr_val','reliability','eval_var'])
BbtParameterEval =  namedtuple('BbtParameterEval',[ 'insertdate',
                                                    'iteration_no',
                                                    'fine',\
                                                    'he',\
                                                    'hp',\
                                                    'co',\
                                                    'gamma',\
                                                    'sigma',\
                                                    'mi',\
                                                    'ei',\
                                                    'cai',\
                                                    'gsi',\
                                                    'rmr',\
                                                    'pkgl',\
                                                    'closure',\
                                                    'rockburst',\
                                                    'front_stability_ns',\
                                                    'front_stability_lambda',\
                                                    'penetrationRate',\
                                                    'penetrationRateReduction',\
                                                    'contactThrust',\
                                                    'torque',\
                                                    'frictionForce',\
                                                    'requiredThrustForce',\
                                                    'availableThrust',\
                                                    'dailyAdvanceRate'])


def bbtparameter_factory(cursor, row):
    return BbtParameter(*row)

def bbtprofilo_factory(cursor, row):
    return BbtProfilo(*row)

def bbtgeoitem_factory(cursor, row):
    return BbtGeoitem(*row)

def bbtparametereval_factory(cursor, row):
    return BbtParameterEval(*row)

bbtClassReliabilityList = []
BbtClassReliability = namedtuple('BbtClassReliability',['code','reliability','gmr_min','gmr_max','min_val','max_val'])
bbtcls = BbtClassReliability('A','Buona',7.5,10,50,0)
bbtClassReliabilityList.append(bbtcls)
bbtcls = BbtClassReliability('B','Discreta',5,7.5,100,50)
bbtClassReliabilityList.append(bbtcls)
bbtcls = BbtClassReliability('C','Scarsa',2.5,5,200,100)
bbtClassReliabilityList.append(bbtcls)
bbtcls = BbtClassReliability('D','Non affidabile',0,2.5,400,200)
bbtClassReliabilityList.append(bbtcls)
