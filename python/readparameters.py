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


sSql = """select BBtParameterEval.fine, BBtParameterEval.iteration_no, BBtParameterEval.frictionForce
from BBtParameterEval where BBtParameterEval.frictionForce > 0.0 order by BBtParameterEval.iteration_no ,BBtParameterEval.fine
 """
cur.execute(sSql)
bbtresults = cur.fetchall()
# recupero tutti i parametri e li metto in una lista
N = len(bbtresults)
ff1i = []
ff2i = []
ff3i = []
i=0
for bbt_parametereval in bbtresults:
    iteration_no = bbt_parametereval[1]
    if iteration_no < 10 and iteration_no >= 0 :
        ff1i.append( float(bbt_parametereval[2]) )
    elif iteration_no < 20 and iteration_no >= 10 :
        ff2i.append( float(bbt_parametereval[2]) )
    elif iteration_no < 30 and iteration_no >= 20 :
        ff3i.append( float(bbt_parametereval[2]) )
    i += 1

print "%d-%d-%d" % (len(ff1i),len(ff2i),len(ff3i))

cur.execute("select BBtParameterEval.fine, BBtParameterEval.dailyAdvanceRate ,  BBtParameterEval.he, BBtParameterEval.hp , BBtParameterEval.iteration_no , BBtParameterEval.frictionForce from BBtParameterEval  order by BBtParameterEval.iteration_no, BBtParameterEval.fine")
bbtresults = cur.fetchall()
# recupero tutti i parametri e li metto in una lista
M = 30 # No di iterazioni
N = len(bbtresults)/M # No di segmenti
pi = zeros(shape=(N,), dtype=float)
he = zeros(shape=(N,), dtype=float)
hp = zeros(shape=(N,), dtype=float)
ti = zeros(shape=(N,), dtype=float)
m_rmr = zeros(shape=(N,M), dtype=float)
tti = zeros(shape=(N,M), dtype=float)
xti = zeros(shape=(N,M), dtype=float)
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
subplot(231)
"""
title("Avanzamento")
plot(pi,he, linewidth=1)
plot(pi,hp, linewidth=1)
plot(pi,m_rmr/1000, linewidth=1)
errorbar(pi,aa, yerr=asymmetric_error)

axis([max(pi)*1.1,min(pi)*0.9,0,max(he)+1])
"""

title("No Eventi per Friction Force con sovrascavo 0,1")

n, bins, patches = hist(ff1i,bins=20)
bi_mean = np.nanmean(ff1i)
bi_std = np.nanstd(ff1i)

axvline(bi_mean,linewidth=4, color='g',label='media')
axvline(bi_mean-bi_std, color='y')
axvline(bi_mean+bi_std, color='y')

subplot(232)

title("No Eventi per Friction Force con sovrascavo 0,2")

n, bins, patches = hist(ff2i,bins=20)
bi_mean = np.nanmean(ff2i)
bi_std = np.nanstd(ff2i)

axvline(bi_mean,linewidth=4, color='g',label='media')
axvline(bi_mean-bi_std, color='y')
axvline(bi_mean+bi_std, color='y')

subplot(233)
title("No Eventi per Friction Force con sovrascavo 0,3")
n, bins, patches = hist(ff3i,bins=20)
bi_mean = np.nanmean(ff3i)
bi_std = np.nanstd(ff3i)

axvline(bi_mean,linewidth=4, color='g',label='media')
axvline(bi_mean-bi_std, color='y')
axvline(bi_mean+bi_std, color='y')

subplot(234)
title("Totale No Eventi suddivisi per Sovrascavo ")
x = [0.1,0.2,0.3]
nev = [len(ff1i),len(ff2i),len(ff3i)]
bar(x,nev,  width=0.01)
show()

print(sum(ff1i)/len(ff1i))
print(sum(ff2i)/len(ff2i))
print(sum(ff3i)/len(ff3i))
