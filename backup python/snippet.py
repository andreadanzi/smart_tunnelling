import sys, getopt, logging, os
from tbmconfig import tbms
from bbt_database import *
from bbtutils import *


"""
DA Eseguire sul DB

ALTER TABLE BbtTbm ADD COLUMN breakawayTorque REAL

SELECT  BbtParameterEval.tunnelName, BbtParameterEval.tbmName, BbtParameterEval.fine, count(*) as cnt
FROM BbtParameterEval
JOIN BbtTbm on BbtTbm.name = BbtParameterEval.tbmName
WHERE BbtParameterEval.tbmName !='XXX'
AND (
		(BbtParameterEval.tbmName LIKE 'CE%' and BbtParameterEval.availableThrust< 3000) OR (BbtParameterEval.tbmName LIKE 'GL%' and BbtParameterEval.availableThrust< 5000)
		OR
		(BbtParameterEval.torque> BbtTbm.breakawayTorque)
		)
GROUP BY BbtParameterEval.tunnelName, BbtParameterEval.tbmName, BbtParameterEval.fine
ORDER BY BbtParameterEval.tunnelName, BbtParameterEval.tbmName ASC, cnt DESC
"""
########## Mi metto nella directory corrente
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
########## File vari: DB e file excel
sDBName = bbtConfig.get('Database','dbname')
sDBPath = os.path.join(os.path.abspath('..'), bbtConfig.get('Database','dbfolder'), sDBName)
if not os.path.isfile(sDBPath):
    print "Errore! File %s inesistente!" % sDBPath
    exit(1)

load_tbm_table(sDBPath, tbms)
