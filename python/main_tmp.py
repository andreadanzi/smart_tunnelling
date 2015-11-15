from TunnelSegment import *
from tbmconfig import *
from pylab import *
import matplotlib.pyplot as plt
import sqlite3, os,  csv #, pickle
from bbtutils import *
from bbtnamedtuples import *
from collections import namedtuple

# leggo il db
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

# definisco il tipo di riga che vado a leggere, la funzione bbtmyparameter_factory serve per spiegare al modulo del db dove metterte i valori delle colonne
BbtMyParameter =  namedtuple('BbtMyParameter',['descr','inizio','fine','length','he','hp','co','gamma','sci','mi','ei','gsi','rmr', 'sti', 'k0_min', 'k0_max'])
def bbtmyparameter_factory(cursor, row):
    return BbtMyParameter(*row)
# spiego al modulo del db dove metterte i valori delle colonne
conn.row_factory = bbtmyparameter_factory
cur = conn.cursor()
print "start querying database  "
# eseguo la query, che deve avere le colonne nello stesso ordine di quelle che vuoi che vadano a finire in BbtMyParameter definito prima
bbtresults = cur.execute("SELECT title,inizio,fine,abs(fine-inizio) as length,he,hp,co,g_med,sigma_ci_avg,mi_med,ei_med,gsi_med,rmr_med, (sigma_ti_min + sigma_ti_max) / 2 as sigma_ti, k0_min, k0_max FROM bbtparameter ORDER BY fine")
res=bbtresults.fetchall()
# recupero tutti i parametri e li metto in una lista
##bbt_parameterseval = []  # servono????

# gabriele@20151114 friction parametrica
fiRi = .5
frictionCoeff = .15

#inizializzo le info sul tracciato
alnCE=InfoAlignment('Cunicolo esplorativo direzione Nord', 'CE', 13290., 27217., fiRi, frictionCoeff) # gabriele@20151114 friction parametrica
alnGLNORD=InfoAlignment('Galleria di linea direzione Nord', 'GLNORD', 44191.75, 32088., fiRi, frictionCoeff) # gabriele@20151114 friction parametrica
alnGLSUD=InfoAlignment('Galleria di linea direzione Sud', 'GLSUD', 49082.867, 53000., fiRi, frictionCoeff) # gabriele@20151114 friction parametrica

#loop sui tracciati (ora prendo solo il CE
alnCurr = alnCE
pkMinCurr = min(alnCurr.pkStart, alnCurr.pkEnd)
pkMaxCurr = max(alnCurr.pkStart, alnCurr.pkEnd)

# leggo le tbm
# ora la prendo secca ma andrebbero prese tutte quelle che in cui (vedi riga commentata sotto
for tbmName in tbms:
    tbmData = tbms[tbmName]
    if alnCurr.tbmKey in tbmData.alignmentCode:
        
        # inizializzo i performance index
        #indicatori di produzione (restituiscono un tempo in ore)
        # vanno sommati segmento a segmento
        #P0 = PerformanceIndex('Produzione effettiva') #
        P1 = PerformanceIndex('Produzione in condizioni standard') #
        P2 = PerformanceIndex('Montaggio e smontaggio TBM') #
        P3 = PerformanceIndex('Avanzamento in rocce dure') #
        P4 = PerformanceIndex('Preparazione prospezioni')
        P5 = PerformanceIndex('Preparazione consolidamenti')
        P6 = PerformanceIndex('Posa rivestimento')

        #indicatori geotecnici (restituiscono un parametro adimensionale che considera tempi, costi e impatti
        # vanno sommati segmento a segmento

        G1 = PerformanceIndex('Instabilita\' del fronte')
        G2 = PerformanceIndex('Instabilita\' del cavo')
        G5 = PerformanceIndex('Splaccaggio calotta')
        G6 = PerformanceIndex('Cavita\' o faglie')
        G7 = PerformanceIndex('Venute acqua')
        G8 = PerformanceIndex('Presenza gas')
        G11 = PerformanceIndex('Rigonfiamento')
        G12 = PerformanceIndex('Distacco blocchi al fronte')
        G13 = PerformanceIndex('Rockburst')

        #indicatori vari
        V1 = PerformanceIndex('Ambiente di lavoro')
        V2 = PerformanceIndex('Costo TBM')
        V3 = PerformanceIndex('Attrezzaggio per prospezioni')
        V4 = PerformanceIndex('Deviazione traiettoria')
        V5 = PerformanceIndex('Integrita\' conci')
        V6 = PerformanceIndex('Complessita\' TBM')
        
        
        tbm = TBM(tbmData, 'V')

        #definisco impatto montaggio e smontaggio
        tProductionMin =alnCurr.length/tbm.maxProduction # tempo minimo di produzione dato applicando la produzione massima a tutta la tratta
        tbm.P2.defineImpact(tProductionMin)
        tbm.P6.defineImpact(tProductionMin, tbm.type,  alnCurr.tbmKey)

        #posso subito definire gli indicatori vari 
        pCur=1.

        iCur=tbm.P2.impact
        P2.updateIndex(0.005, iCur, alnCurr.length) # gabriele@20151115
        P2.finalizeIndex(alnCurr.length) # gabriele@20151115

        iCur=tbm.P6.impact
        P6.updateIndex(pCur, iCur, 1.)
        P6.finalizeIndex(1.)

        iCur=tbm.V1.impact
        V1.updateIndex(0.005, iCur, alnCurr.length)
        V1.finalizeIndex(alnCurr.length)

        projectRefCost = 1400. # mln di euro
        tbm.V2.defineImpact(projectRefCost)
        iCur=tbm.V2.impact
        V2.updateIndex(0.005, iCur, alnCurr.length) # gabriele@20151115
        V2.finalizeIndex(alnCurr.length) # gabriele@20151115
# gabriele@20151115
# assegno la stessa percentuale della preparazione prospezioni che ee' su tutto il tracciato
        iCur=tbm.V3.impact
        V3.updateIndex(1., iCur, alnCurr.length)
        V3.finalizeIndex(alnCurr.length)

        iCur=tbm.V4.impact
        V4.updateIndex(0.005, iCur, alnCurr.length)
        V4.finalizeIndex(alnCurr.length)

        iCur=tbm.V5.impact
        V5.updateIndex(0.005, iCur, alnCurr.length)
        V5.finalizeIndex(alnCurr.length)

        iCur=tbm.V6.impact
        V6.updateIndex(0.005, iCur, alnCurr.length)
        V6.finalizeIndex(alnCurr.length)


        dimarray = len(res)
        varnum = 21
        vplot = zeros(shape=(varnum, dimarray), dtype=float)
        vcheck = zeros(shape=(dimarray,  varnum), dtype=float)

        i=0
        for p in res:
            
            #verifico che il segmento ricada entro le progressive del tracciato corrente alnCurr
            #pkMinSegm=min(p.inizio, p.fine)
            #pkMaxSegm=max(p.inizio, p.fine)
            
            segmToAnalize = True #pkMinSegm<=pkMaxCurr and pkMaxSegm>=pkMinCurr
            
            if segmToAnalize:
                tbmsect = TBMSegment(p, tbm, alnCurr.fiRi, alnCurr.frictionCoeff) # gabriele@20151114 friction parametrica
                
                # aggiorno indici produzione. l'impatto medio dovra' poi essere diviso per la lunghezza del tracciato
        #        pCur=tbmsect.P0.probability
        #        iCur=tbmsect.P0.impact
        #        P0.updateIndex(pCur, iCur, p.length)

                pCur=tbmsect.P1.probability
                iCur=tbmsect.P1.impact
                P1.updateIndex(pCur, iCur, p.length)

                pCur=tbmsect.P3.probability
                iCur=tbmsect.P3.impact
                P3.updateIndex(pCur, iCur, p.length)

                pCur=tbmsect.P4.probability
                iCur=tbmsect.P4.impact
                P4.updateIndex(pCur, iCur, p.length)

                pCur=tbmsect.P5.probability
                iCur=tbmsect.P5.impact
                P5.updateIndex(pCur, iCur, p.length)
                
                # aggiorno indici geotecnici
                pCur=tbmsect.G1.probability
                iCur=tbmsect.G1.impact
                G1.updateIndex(pCur, iCur, p.length)
                
                pCur=tbmsect.G2.probability
                iCur=tbmsect.G2.impact
                G2.updateIndex(pCur, iCur, p.length)
                
                pCur=tbmsect.G5.probability
                iCur=tbmsect.G5.impact
                G5.updateIndex(pCur, iCur, p.length)

                pCur=tbmsect.G6.probability
                iCur=tbmsect.G6.impact
                #scalo probabilita' in base al tracciato
                prob=0.
                if alnCurr.tbmKey =='CE':
                    prob=.2 # classe 4 aftes
                elif alnCurr.tbmKey =='GLNORD':
                    prob=.005 #classe 1 aftes perche' noto da cunicolo
                elif alnCurr.tbmKey =='GLSUD':
                    prob=.005 #classe 1 aftes perche' noto da cunicolo
                G6.updateIndex(pCur, iCur, prob*p.length)

                pCur=tbmsect.G7.probability
                iCur=tbmsect.G7.impact
                #scalo probabilita' in base al tracciato
                prob=0.
                if alnCurr.tbmKey =='CE':
                    prob=.05 # classe 3 aftes
                elif alnCurr.tbmKey =='GLNORD':
                    prob=.005 # drenato dal cunicolo
                elif alnCurr.tbmKey =='GLSUD':
                    prob=.005 # drenato dal cunicolo
                G7.updateIndex(pCur, iCur, prob*p.length)

                pCur=tbmsect.G8.probability
                iCur=tbmsect.G8.impact
                #scalo probabilita' in base al tracciato
                prob=0.
                if alnCurr.tbmKey =='CE':
                    prob=.02
                elif alnCurr.tbmKey =='GLNORD':
                    prob=.005
                elif alnCurr.tbmKey =='GLSUD':
                    prob=0.
                G8.updateIndex(pCur, iCur, prob*p.length)

                pCur=tbmsect.G11.probability
                iCur=tbmsect.G11.impact
                G11.updateIndex(pCur, iCur, p.length)

                pCur=tbmsect.G12.probability
                iCur=tbmsect.G12.impact
                G12.updateIndex(pCur, iCur, p.length)

                pCur=tbmsect.G13.probability
                iCur=tbmsect.G13.impact
                G13.updateIndex(pCur, iCur, p.length)

                vplot[0][i] = tbmsect.pkCe2Gl(p.fine)
                vplot[1][i] = p.co
                vplot[2][i] = tbmsect.TunnelClosureAtShieldEnd*100. #in cm
                vplot[3][i] = tbmsect.rockBurst.Val
                vplot[4][i] = tbmsect.frontStability.Ns
                vplot[5][i] = tbmsect.frontStability.lambdae
                vplot[6][i] = tbmsect.penetrationRate*1000. #in mm/giro
                vplot[7][i] = tbmsect.penetrationRateReduction*1000. #in mm/giro
                vplot[8][i] = tbmsect.contactThrust
                vplot[9][i] = tbmsect.torque
                vplot[10][i] = tbmsect.frictionForce
                vplot[11][i] = tbmsect.requiredThrustForce
                vplot[12][i] = tbmsect.availableThrust
                vplot[13][i] = tbmsect.dailyAdvanceRate
                
                vcheck[i][0] = vplot[0][i]          #progressive GL
                vcheck[i][1] = tbmsect.Excavation.Radius          #tunnel radius in m
                vcheck[i][2] = tbmsect.InSituCondition.SigmaV          #in-situ stress in MPa
                vcheck[i][3] = tbmsect.Rock.E   #young modulus in MPa
                vcheck[i][4] = tbmsect.MohrCoulomb.psi #dilatation angle
                vcheck[i][5] = tbmsect.Rock.Ucs #UCS in MPa
                vcheck[i][6] = tbmsect.InSituCondition.Gsi #GSI
                vcheck[i][7] = tbmsect.HoekBrown.Mi
                vcheck[i][8] = tbmsect.HoekBrown.D
                vcheck[i][9] = tbmsect.HoekBrown.Mb
                vcheck[i][10] = tbmsect.HoekBrown.S
                vcheck[i][11] = tbmsect.HoekBrown.A
                vcheck[i][12] = tbmsect.HoekBrown.Mr
                vcheck[i][13] = tbmsect.HoekBrown.Sr
                vcheck[i][14] = tbmsect.HoekBrown.Ar
                vcheck[i][16] = tbmsect.UrPi_HB(0.) #convergenza infinita
                vcheck[i][15] = tbmsect.Rpl # raggio plastico
                vcheck[i][17] = tbmsect.Picr #Pcr in MPa
                vcheck[i][18] = tbmsect.LDP_Vlachopoulos_2009(0.) #convergenza al fronte
                vcheck[i][19] = tbmsect.LDP_Vlachopoulos_2009(tbm.Slen) #Convergenza fine scudo
                vcheck[i][20] = tbmsect.TunnelClosureAtShieldEnd #Chiusura a fine scudo
                
#                vcheck[i][6] = vplot[2][i]          #tunnel closure a fine scudo in cm
#                vcheck[i][7] = tbmsect.HoekBrown.Mr          #mb res
#                vcheck[i][8] = tbmsect.HoekBrown.Sr          #s res   
#                vcheck[i][9] = tbmsect.HoekBrown.Ar          #a res
#                vcheck[i][10] = tbmsect.HoekBrown.SigmaC          #
#                vcheck[i][11] = tbmsect.HoekBrown.SigmaCr          #a res
#                vcheck[i][12] = tbmsect.UrPi_HB(0.)
#                vcheck[i][3] = vplot[3][i]          #valore coefficiente per rockburst
#                vcheck[i][4] = vplot[4][i]          #valore Panet Ns    
#                vcheck[i][5] = vplot[5][i]          #valore Panet lambdae
#                vcheck[i][6] = vplot[6][i]          #penetration rate in mm/giro
#                vcheck[i][7] = vplot[7][i]          #riduzione della penetration rate in mm/giro
#                vcheck[i][8] = vplot[8][i]          #thrust sul fronte in kN    
#                vcheck[i][9] = vplot[9][i]          #torque sul fronte in kNm
#                vcheck[i][10] = vplot[10][i]       #forza attrito per convergenza sullo scudo in kN
#                vcheck[i][11] = vplot[11][i]       #thrust totale richiesto in kN (fronte+attrito+backup)
#                vcheck[i][12] = vplot[12][i]       #thrust disponibile per vincere attrito in kN
#                vcheck[i][13] = vplot[13][i]       #produzione in m/gg (con 340 gg lavorativi anno)
            
            # accedo ai valori tramite le properties definite con BbtParameterEval in bbtnamedtuples.py
            #print p.fine, p.sci, p.sti, p.k0_min, p.k0_max  
            i += 1
        conn.close()

        # aggiorno i valori medi degli indici e la loro applicazione percentuale sulla tratta in esame
        #P0.convertDaysToImpactAndFinalizeIndex(alnCurr.length)
        P1.finalizeIndex(alnCurr.length)
        P3.finalizeIndex(alnCurr.length)
        P4.finalizeIndex(alnCurr.length)
        P5.finalizeIndex(alnCurr.length)

        G1.finalizeIndex(alnCurr.length)
        G2.finalizeIndex(alnCurr.length)
        G5.finalizeIndex(alnCurr.length)
        G6.finalizeIndex(alnCurr.length)
        G7.finalizeIndex(alnCurr.length)
        G8.finalizeIndex(alnCurr.length)
        G11.finalizeIndex(alnCurr.length)
        G12.finalizeIndex(alnCurr.length)
        G13.finalizeIndex(alnCurr.length)

        #stampo a video i risultati
        G1.printOut()
        G2.printOut()
        G5.printOut()
        G6.printOut()
        G7.printOut()
        G8.printOut()
        G11.printOut()
        G12.printOut()
        G13.printOut()

        #P0.printOut()
        P1.printOut()
        P2.printOut()
        P3.printOut()
        P4.printOut()
        P5.printOut()
        P6.printOut()

        V1.printOut()
        V2.printOut()
        V3.printOut()
        V4.printOut()
        V5.printOut()
        V6.printOut()



        # interventi particolari (stabilization measure
        sm = (\
                StabilizationMeasure(24372, 27217, 'Tipo 1', 12),\
                StabilizationMeasure(22987, 23283, 'Tipo 1', 18),\
                StabilizationMeasure(21952, 22987, 'Tipo 1', 90),\
                StabilizationMeasure(21027, 21952, 'Tipo 1', 12),\
                StabilizationMeasure(20147, 21027, 'Tipo 1', 36),\
                StabilizationMeasure(17312, 18302, 'Tipo 1', 36),\
                StabilizationMeasure(16452, 17312, 'Tipo 1', 36),\
                StabilizationMeasure(15512, 16452, 'Tipo 1', 18),\
                StabilizationMeasure(14591, 15512, 'Tipo 1', 12),\
                StabilizationMeasure(14516, 14591, 'Tipo 1', 12),\
                StabilizationMeasure(14170, 14516, 'Tipo 1', 12),\
                StabilizationMeasure(13780, 14170, 'Tipo 1', 12),\
                StabilizationMeasure(24372, 27217, 'Tipo 2', 12),\
                StabilizationMeasure(22987, 23283, 'Tipo 2', 24),\
                StabilizationMeasure(21952, 22987, 'Tipo 2', 36),\
                StabilizationMeasure(21027, 21952, 'Tipo 2', 12),\
                StabilizationMeasure(18302, 20147, 'Tipo 2', 12),\
                StabilizationMeasure(16452, 17312, 'Tipo 2', 18),\
                StabilizationMeasure(14516, 14591, 'Tipo 2', 12),\
                StabilizationMeasure(21952, 22987, 'Tipo 3', 50)\
                )

        dim1 = 0
        dim2 = 0
        dim3 = 0
        for cur in sm:
            if cur.type == 'Tipo 1':
                dim1+=1
            elif cur.type == 'Tipo 2':
                dim2+=1
            elif cur.type == 'Tipo 3':
                dim3+=1
        sm1xplot = zeros(shape=(dim1, 2), dtype=float)
        sm1yplot = zeros(shape=(dim1, 2), dtype=float)
        sm2xplot = zeros(shape=(dim2, 2), dtype=float)
        sm2yplot = zeros(shape=(dim2, 2), dtype=float)
        sm3xplot = zeros(shape=(dim3, 2), dtype=float)
        sm3yplot = zeros(shape=(dim3, 2), dtype=float)

        cnt1 = 0
        cnt2 = 0
        cnt3 = 0
        yLim = max(vplot[1])
        y1 = 1.1*yLim
        y2 = 1.2*yLim
        y3 = 1.3*yLim
        xMin = 0.0
        xMax = 0.0
        for cur in sm:
            xMin = min(tbmsect.pkCe2Gl(cur.pkFrom), tbmsect.pkCe2Gl(cur.pkTo))
            xMax = max(tbmsect.pkCe2Gl(cur.pkFrom), tbmsect.pkCe2Gl(cur.pkTo))
            if cur.type == 'Tipo 1':
                sm1xplot[cnt1][0] = xMin
                sm1xplot[cnt1][1] = xMax
                sm1yplot[cnt1][0] = y1
                sm1yplot[cnt1][1] = y1
                cnt1+=1
            elif cur.type == 'Tipo 2':
                sm2xplot[cnt2][0] = xMin
                sm2xplot[cnt2][1] = xMax
                sm2yplot[cnt2][0] = y2
                sm2yplot[cnt2][1] = y2
                cnt2+=1
            elif cur.type == 'Tipo 3':
                sm3xplot[cnt3][0] = xMin
                sm3xplot[cnt3][1] = xMax
                sm3yplot[cnt3][0] = y3
                sm3yplot[cnt3][1] = y3
                cnt3+=1
        # plot risultati
        # figura 1
        fig1 = plt.figure()
        fig1.suptitle('Geotechnical analyses' + tbmName, fontsize=16)
        ax11 = fig1.add_subplot(3, 1, 1)
        ax11.set_xlim(min(vplot[0]), max(vplot[0]))
        ax11s = ax11.twinx()
        ax11s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        for i in range(dim1):
            ax11s.plot(sm1xplot[i], sm1yplot[i], label='Int. tipo 1', color='yellow', linewidth=2)
        for i in range(dim2):
            ax11s.plot(sm2xplot[i], sm2yplot[i], label='Int. tipo 2', color='red', linewidth=2)
        for i in range(dim3):
            ax11s.plot(sm3xplot[i], sm3yplot[i], label='Int. tipo 3', color='orange', linewidth=2)
        ax11s.set_ylim(0.0, max(vplot[1])*1.5)
        ax11s.set_ylabel('Copertura')

        ax11.plot(vplot[0], vplot[2], label='Panet a fine scudo')
        ax11.plot((min(vplot[0]), max(vplot[0])), (100.*tbm.gap, 100.*tbm.gap), label='Sovrascavo', linewidth=2)
        ax11.set_ylabel('Chiusura cavo [cm]')
        ax11.set_ylim(0.0, tbm.gap*300.0)
        ax11.legend(loc=1)

        ax12 = fig1.add_subplot(3, 1, 2)
        ax12.set_xlim(min(vplot[0]), max(vplot[0]))
        ax12.plot(vplot[0], vplot[3], label='Hoek')
        ax12.plot((min(vplot[0]), max(vplot[0])), (0.1, 0.1), label='Stable behaviour limit', linewidth=2)
        ax12.plot((min(vplot[0]), max(vplot[0])), (0.2, 0.2), label='Spalling limit', linewidth=2)
        ax12.plot((min(vplot[0]), max(vplot[0])), (0.3, 0.3), label='Severe spalling - slabbing limit', linewidth=2)
        ax12.plot((min(vplot[0]), max(vplot[0])), (0.4, 0.4), label='Need of important stabilization measure limit', linewidth=2)
        ax12.plot((min(vplot[0]), max(vplot[0])), (0.5, 0.5), label='Cavity collapse (rock burst)', linewidth=2)
        ax12.set_ylabel('Rock burst potential [-]')
        ax12.set_ylim(0.0, 1.0)
        ax12.legend(loc=1)
        ax12s = ax12.twinx()
        ax12s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax12s.set_ylim(0.0, max(vplot[1])*1.5)
        ax12s.set_ylabel('Copertura')

        ax13 = fig1.add_subplot(3, 1, 3)
        ax13.set_xlim(min(vplot[0]), max(vplot[0]))
        ax13.plot(vplot[0], vplot[5], label='Panet lambdae')
        ax13.plot((min(vplot[0]), max(vplot[0])), (0.6, 0.6), label='Stability lower limit', linewidth=2)
        ax13.plot((min(vplot[0]), max(vplot[0])), (0.3, 0.3), label='Short term stability lower limit', linewidth=2)
        ax13.plot((min(vplot[0]), max(vplot[0])), (0.0, 0.0), label='Instability', linewidth=2)
        ax13.set_ylabel('Stabilita\' del fronte [-]')
        ax13.set_ylim(0.0, 1.0)
        ax13.legend(loc=1)
        ax13s = ax13.twinx()
        ax13s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax13s.set_ylim(0.0, max(vplot[1])*1.5)
        ax13s.set_ylabel('Copertura')

        #figura 2
        fig2 = plt.figure()
        fig2.suptitle('Production analyses - ' + tbmName, fontsize=16)

        ax21 = fig2.add_subplot(2, 1, 1)
        ax21.set_xlim(min(vplot[0]), max(vplot[0]))
        ax21.plot(vplot[0], vplot[6], label='ROP')
        ax21.set_ylabel('[mm/revolution]')
        ax21.legend(loc=1)
        ax21s = ax21.twinx()
        ax21s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax21s.set_ylim(0.0, max(vplot[1])*1.5)

        ax22 = fig2.add_subplot(2, 1, 2)
        ax22.set_xlim(min(vplot[0]), max(vplot[0]))
        ax22.plot(vplot[0], vplot[13], label='Daily Production')
        ax22.set_ylabel('[m/workingday]')
        ax22.legend(loc=1)
        ax22s = ax22.twinx()
        ax22s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax22s.set_ylim(0.0, max(vplot[1])*1.5)

        #figura 3
        fig3 = plt.figure()
        fig3.suptitle('Thrust requirements - ' + tbmName, fontsize=16)
        ax31 = fig3.add_subplot(2, 1, 1)
        ax31.set_xlim(min(vplot[0]), max(vplot[0]))
        ax31s = ax31.twinx()
        ax31s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax31s.set_ylim(0.0, max(vplot[1])*1.5)
        ax31.plot(vplot[0], vplot[8], label='Contact thrust')
        ax31.plot((min(vplot[0]), max(vplot[0])), (tbm.totalContactThrust, tbm.totalContactThrust), label='Max contact thrust', linewidth=2)
        ax31.set_ylabel('Thrust kN')
        ax31.set_ylim(0.0, tbm.totalContactThrust*1.2)
        ax31.legend(loc=1)

        ax32 = fig3.add_subplot(2, 1, 2)
        ax32.set_xlim(min(vplot[0]), max(vplot[0]))
        ax32s = ax32.twinx()
        ax32s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax32s.set_ylim(0.0, max(vplot[1])*1.5)
        ax32.plot(vplot[0], vplot[10], label='Friction on shield')
        ax32.plot(vplot[0], vplot[12], label='Available thrust', linewidth=2)
        ax32.set_ylabel('Thrust kN')
        ax32.set_ylim(0.0, tbm.installedAuxiliaryThrustForce*1.2)
        ax32.legend(loc=1)

        #figura 4
        fig4 = plt.figure()
        fig4.suptitle('TBM utilization - ' + tbmName, fontsize=16)
        ax41 = fig4.add_subplot(2, 1, 1)
        ax41.set_xlim(min(vplot[0]), max(vplot[0]))
        ax41s = ax41.twinx()
        ax41s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax41s.set_ylim(0.0, max(vplot[1])*1.5)

        ax41.plot(vplot[0], vplot[11], label='Required thrust force')
        ax41.plot((min(vplot[0]), max(vplot[0])), (tbm.installedThrustForce, tbm.installedThrustForce), label='Installed thrust force', linewidth=2)
        ax41.plot((min(vplot[0]), max(vplot[0])), (tbm.installedAuxiliaryThrustForce, tbm.installedAuxiliaryThrustForce), label='Auxiliary thrust force', linewidth=2)
        ax41.set_ylabel('Thrust kN')
        ax41.set_ylim(0.0, tbm.installedAuxiliaryThrustForce*1.2)
        ax41.legend(loc=1)

        ax42 = fig4.add_subplot(2, 1, 2)
        ax42.set_xlabel('Progressive')
        ax42.set_xlim(min(vplot[0]), max(vplot[0]))
        ax42.plot(vplot[0], vplot[9], label='Required torque')
        ax42.plot((min(vplot[0]), max(vplot[0])), (tbm.nominalTorque, tbm.nominalTorque), label='Nominal torque', linewidth=2)
        ax42.plot((min(vplot[0]), max(vplot[0])), (tbm.breakawayTorque, tbm.breakawayTorque), label='Breakaway torque', linewidth=2)
        ax42.set_ylabel('Torque kNm')
        ax42.legend(loc=1)
        ax42s = ax42.twinx()
        ax42s.plot(vplot[0], vplot[1], label='Copertura', color='brown', linewidth=2)
        ax42s.set_ylim(0.0, max(vplot[1])*1.5)

        plt.show()
        # esposrto in csv i valori di confronto
        with open('confronto.csv', 'wb') as f:
            writer = csv.writer(f,delimiter=",")
            writer.writerows(vcheck)
"""

        plot(vplot[0], vplot[1], label='Panet_1995')
        plot(vplot[0], vplot[2], label='Vlachopoulos_2009')
        plot((min(vplot[0]), max(vplot[0])), (0.1, 0.1), label='Sovrascavo')
        xlim(min(vplot[0]), max(vplot[0]))
        ylim(0.0, tbm.OverExcavation*5.0)
        xlabel('Progressive')
        ylabel('Chiusura tunnel sullo scudo')
        title('Cunicolo Esplorativo')
        legend(loc='upper right')
"""

#    print "%d -> Fine segmento=%f , Quota=%f, Quota Progetto=%f, Copertura=%f, Gamma=%f, Sigma=%f, Mi=%f, Ei=%f, CAI=%f, GSI=%f" % (i, p.fine, p.he, p.hp, p.co, p.gamma, p.sigma, p.mi, p.ei, p.cai, p.gsi)

## Nel caso puoi buttare il contenuto in un file csv: delimiter e' il separatore, da leggere con excel o file di testo
#with open('bbtdata.csv', 'wb') as f:
#    writer = csv.writer(f,delimiter=",")
#    writer.writerows(bbt_evalparameters)
#
#exit(-2)




