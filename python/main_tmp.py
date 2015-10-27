import math
from TunnelSegment import *
from pylab import *
import matplotlib.pyplot as plt
import csv

# andrea: pickle serve per serializzare e deserializzare oggetti che stanno in memoria, per poterli scivere su un file per poi riutilizzarli
import pickle, os, pprint
from collections import namedtuple
# BbtParameterEval e il tipo dato con cui ho serializzato i dati, e un contenitore di valori che puoi richiamare con il nome dl campo
BbtParameterEval =  namedtuple('BbtParameterEval',['fine','he','hp','co','gamma','sigma','mi','ei','cai','gsi', 'rmr', 'closure'])
# ricavo il percorso della directory contenente il file corrente (main.py)
path = os.path.dirname(os.path.realpath(__file__))
# mi metto nella directory corrente
os.chdir(path)
# leggo il file serializzato (bbtdata.pkl) che ti ho messo nella stessa directory sul Drive
pkl_file = open('bbtdata.pkl', 'rb')
# carico un file mettendo il contenuto nell'oggettto bbt_evalparameters che e una lista di BbtParameterEval
bbt_evalparameters = pickle.load(pkl_file)
#          (type, slen, sdiammin, sdiammax, overexcav, cno, cr, ct, cs, rpm, Ft, totalContactThrust, installedThrustForce, installedAucillaryThrustForce, nominalTorque, breakawayTorque, backupDragForce, friction, LDP_type)
tbm = TBM('DS', 300., 6.42, 6.62, .1, 38., 19.*.0254/2., .020, .1, 5.,  315., 11970., 35626., 42223., 4375., 6343., 4000., 0.15, 'P')

dimarray = len(bbt_evalparameters)
varnum = 20
vplot = zeros(shape=(varnum, dimarray), dtype=float)
vcheck = zeros(shape=(dimarray,  varnum), dtype=float)

for i in range(dimarray):
    p = bbt_evalparameters[i]
    # qui puoi instanziare i tuoi TBMSegment usando p.fine, p.he, p.hp, p.co, p.gamma, p.sigma, p.mi, p.ei, p.cai, p.gsi
    #                                            (gamma,            ni,     e,                  ucs,            sigmat, psi, mi,   ob, waterdepth, k0min, k0max, gsi, rmr, excavType, excavArea,                                                            excavWidth,        excavHeight, refLength,      pi,     lunsupported, tbm)
    tbmsect = TBMSegment(p.gamma, .2, p.ei*1000., p.sigma, 5.,0., p.mi, p.co, p.co, .5, 1., p.gsi, p.rmr, 'Mech', (tbm.SdiamMax**2)*math.pi/4., tbm.SdiamMax, tbm.SdiamMax, tbm.Slen, 0., tbm.Slen,  tbm)
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
    vcheck[i][1] = vplot[1][i]          #copertura
    vcheck[i][2] = vplot[2][i]          #tunnel closure a fine scudo in cm
    vcheck[i][3] = tbmsect.HoekBrown.Mr          #mb res
    vcheck[i][4] = tbmsect.HoekBrown.Sr          #s res   
    vcheck[i][5] = tbmsect.HoekBrown.Ar          #a res
    vcheck[i][6] = tbmsect.HoekBrown.SigmaC          #
    vcheck[i][7] = tbmsect.HoekBrown.SigmaCr          #a res
    vcheck[i][8] = tbmsect.UrPi_HB(0.)
"""
    vcheck[i][3] = vplot[3][i]          #valore coefficiente per rockburst
    vcheck[i][4] = vplot[4][i]          #valore Panet Ns    
    vcheck[i][5] = vplot[5][i]          #valore Panet lambdae
    vcheck[i][6] = vplot[6][i]          #penetration rate in mm/giro
    vcheck[i][7] = vplot[7][i]          #riduzione della penetration rate in mm/giro
    vcheck[i][8] = vplot[8][i]          #thrust sul fronte in kN    
    vcheck[i][9] = vplot[9][i]          #torque sul fronte in kNm
    vcheck[i][10] = vplot[10][i]       #forza attrito per convergenza sullo scudo in kN
    vcheck[i][11] = vplot[11][i]       #thrust totale richiesto in kN (fronte+attrito+backup)
    vcheck[i][12] = vplot[12][i]       #thrust disponibile per vincere attrito in kN
    vcheck[i][13] = vplot[13][i]       #produzione in m/gg (con 340 gg lavorativi anno)
"""

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
fig1.suptitle('Geotechnical analyses', fontsize=16)
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
ax11.plot((min(vplot[0]), max(vplot[0])), (100.*tbm.OverExcavation, 100.*tbm.OverExcavation), label='Sovrascavo', linewidth=2)
ax11.set_ylabel('Chiusura cavo [cm]')
ax11.set_ylim(0.0, tbm.OverExcavation*1000.0)
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
fig2.suptitle('Production analyses', fontsize=16)

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
fig3.suptitle('Thrust requirements', fontsize=16)
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
ax32.plot(vplot[0], vplot[12], label='Available thrust to win friction', linewidth=2)
ax32.set_ylabel('Thrust kN')
ax32.legend(loc=1)


#figura 4
fig4 = plt.figure()
fig4.suptitle('TBM utilization', fontsize=16)
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




