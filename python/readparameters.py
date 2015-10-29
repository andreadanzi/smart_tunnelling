import sqlite3, os, csv
from bbtutils import *
from bbtnamedtuples import *
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db

# mi metto nella directory corrente
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

########## File vari: DB
sDBName = 'bbt_mules_2-3.db'
sDBPath = os.path.join(os.path.abspath('..'),'db', sDBName)
if not os.path.isfile(sDBPath):
    print "Errore! File %s inesistente!" % sDBPath
    exit(1)

# mi connetto al database
conn = sqlite3.connect(sDBPath)
# definisco il tipo di riga che vado a leggere, bbtparametereval_factory viene definita in bbtnamedtuples
conn.row_factory = bbtparametereval_factory
cur = conn.cursor()
print "start querying database  "
# eseguo la query, che deve avere le colonne conformi a BbtParameterEval definito in bbtnamedtuples.py
bbtresults = cur.execute("SELECT insertdate,iteration_no,fine,he,hp,co,gamma,sigma,mi,ei,cai,gsi,rmr,pkgl,closure,rockburst,front_stability_ns,front_stability_lambda,penetrationRate,penetrationRateReduction,contactThrust,torque,frictionForce,requiredThrustForce,availableThrust,dailyAdvanceRate,profilo_id,geoitem_id FROM bbtparametereval ORDER BY fine")
# recupero tutti i parametri e li metto in una lista
bbt_parameterseval = []
for bbt_parametereval in bbtresults:
    bbt_parameterseval.append(bbt_parametereval)
    # accedo ai valori tramite le properties definite con BbtParameterEval in bbtnamedtuples.py
    print bbt_parametereval.fine
    print bbt_parametereval.closure
    print bbt_parametereval.torque
    print bbt_parametereval.geoitem_id
    print bbt_parametereval.profilo_id
conn.close()

# me li metto in un csv per controllo
with open('parameters_eval.csv', 'wb') as f:
    writer = csv.writer(f,delimiter=",")
    writer.writerows(bbt_parameterseval)
