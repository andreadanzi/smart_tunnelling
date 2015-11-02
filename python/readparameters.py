import sqlite3, os, csv
from bbtutils import *
from bbtnamedtuples import *
# qui vedi come leggere i parametri dal Database bbt_mules_2-3.db

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
# eseguo la query, che deve avere le colonne conformi a BbtParameterEval definito in bbtnamedtuples.py
cur.execute("select sum(10/BBtParameterEval.dailyAdvanceRate)/340 as tot_sum , BBtParameterEval.iteration_no  from BBtParameterEval group by BBtParameterEval.iteration_no")
bbtresults = cur.fetchall()
# recupero tutti i parametri e li metto in una lista
N = len(bbtresults)
bi = zeros(shape=(N,), dtype=float)
i=0
for bbt_parametereval in bbtresults:
    bi[i] = bbt_parametereval[0]
    i += 1



cur.execute("select BBtParameterEval.fine, BBtParameterEval.dailyAdvanceRate ,  BBtParameterEval.he, BBtParameterEval.hp , BBtParameterEval.iteration_no , BBtParameterEval.sigma from BBtParameterEval  order by BBtParameterEval.iteration_no, BBtParameterEval.fine")
bbtresults = cur.fetchall()
# recupero tutti i parametri e li metto in una lista
N = len(bbtresults)/10
pi = zeros(shape=(N,), dtype=float)
he = zeros(shape=(N,), dtype=float)
hp = zeros(shape=(N,), dtype=float)
ti = zeros(shape=(N,), dtype=float)
m_rmr = zeros(shape=(N,10), dtype=float)
tti = zeros(shape=(N,10), dtype=float)
xti = zeros(shape=(N,10), dtype=float)
i = 0
pj = 0
prev = 0.0
for bbt_parametereval in bbtresults:
    j = int(bbt_parametereval[4])
    if pj != j:
        pj = j
        prev = i = 0
    pi[i] = bbt_parametereval[0]
    xti[i][j] = 10.0/float(bbt_parametereval[1])
    tti[i][j] = prev + xti[i][j]
    prev = tti[i][j]
    he[i] = bbt_parametereval[2]
    hp[i] = bbt_parametereval[3]
    m_rmr[i][j] = float(bbt_parametereval[5])
    i += 1
conn.close()

if N==0:
    print "Nothing found in %s, empty tables?" % sDBPath
    exit()

aa = zeros(shape=(N,), dtype=float)
error = zeros(shape=(N,), dtype=float)
lowe = zeros(shape=(N,), dtype=float)
highe = zeros(shape=(N,), dtype=float)
for i in range(N):
    avg = np.average(tti[i])
    lowe[i] = avg - min(tti[i])
    highe[i] =max(tti[i]) - avg
    aa[i] = avg

asymmetric_error = [lowe, highe]
subplot(211)
title("Avanzamento")
plot(pi,he, linewidth=1)
plot(pi,hp, linewidth=1)
errorbar(pi,aa, yerr=asymmetric_error)


axis([max(pi)*1.1,min(pi)*0.9,0,max(he)+1])

subplot(212)
title("Tempo di completamento")
hist(bi,bins=50)
bi_mean = np.nanmean(bi)
bi_std = np.nanstd(bi)

axvline(bi_mean,linewidth=4, color='g',label='media')
bi_min = min(bi)
bi_max = max(bi)
show()
