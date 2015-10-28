import sqlite3, os, csv
from bbtutils import *
from bbtnamedtuples import *
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db

# mi metto nella directory corrente
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

# mi connetto al database
conn = sqlite3.connect('bbt_mules_2-3.db')
# definisco il tipo di riga che vado a leggere
conn.row_factory = bbtparametereval_factory
cur = conn.cursor()
print "start querying database  "
bbtresults = cur.execute("SELECT insertdate,iteration_no,fine,he,hp,co,gamma,sigma,mi,ei,cai,gsi,rmr,pkgl,closure,rockburst,front_stability_ns,front_stability_lambda,penetrationRate,penetrationRateReduction,contactThrust,torque,frictionForce,requiredThrustForce,availableThrust,dailyAdvanceRate FROM bbtparametereval ORDER BY fine")
# recupero tutti i parametri
bbt_parameterseval = []
for bbt_parametereval in bbtresults:
    bbt_parameterseval.append(bbt_parametereval)
    print bbt_parametereval.fine
    print bbt_parametereval.closure
    print bbt_parametereval.torque
conn.close()


with open('parameters_eval.csv', 'wb') as f:
    writer = csv.writer(f,delimiter=",")
    writer.writerows(bbt_parameterseval)
