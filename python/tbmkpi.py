from TunnelSegment import PerformanceIndex
from bbtutils import *
from bbtnamedtuples import *
import sqlite3, os

class KpiTbm4Tunnel:
    kpis = {}
    tbmName = ""
    tunnelName = ""
    bbttbmkpis = []
    iterationNo = 0

    def __init__(self,sTunnelName, iIterationNo):
        self.tunnelName = sTunnelName
        self.iterationNo = iIterationNo
        # inizializzo i performance index
        #indicatori di produzione (restituiscono un tempo in ore)
        # vanno sommati segmento a segmento
        self.kpis['P0'] = PerformanceIndex('Produzione effettiva') #
        self.kpis['P1'] = PerformanceIndex('Produzione in condizioni standard') #
        self.kpis['P2'] = PerformanceIndex('Montaggio e smontaggio TBM') #
        self.kpis['P3'] = PerformanceIndex('Avanzamento in rocce dure') #
        self.kpis['P4'] = PerformanceIndex('Preparazione prospezioni')
        self.kpis['P5'] = PerformanceIndex('Preparazione consolidamenti')

        #indicatori geotecnici (restituiscono un parametro adimensionale che considera tempi, costi e impatti
        # vanno sommati segmento a segmento

        self.kpis['G1'] = PerformanceIndex('Instabilita\' del fronte')
        self.kpis['G2'] = PerformanceIndex('Instabilita\' del cavo')
        self.kpis['G5'] = PerformanceIndex('Splaccaggio calotta')
        self.kpis['G6'] = PerformanceIndex('Cavita\' o faglie')
        self.kpis['G7'] = PerformanceIndex('Venute acqua')
        self.kpis['G8'] = PerformanceIndex('Presenza gas')
        self.kpis['G11'] = PerformanceIndex('Rigonfiamento')
        self.kpis['G12'] = PerformanceIndex('Distacco blocchi al fronte')
        self.kpis['G13'] = PerformanceIndex('Rockburst')

        #indicatori vari
        self.kpis['V1'] = PerformanceIndex('Ambiente di lavoro')
        self.kpis['V2'] = PerformanceIndex('Costo TBM')
        self.kpis['V3'] = PerformanceIndex('Attrezzaggio per prospezioni')
        self.kpis['V4'] = PerformanceIndex('Deviazione traiettoria')
        self.kpis['V5'] = PerformanceIndex('Integrita\' conci')
        self.kpis['V6'] = PerformanceIndex('Complessita\' TBM')

    def setKPI4TBM(self,tbmName, tbm):
        self.tbmName = tbmName
        pCur=1.

        iCur=tbm.P2.impact
        self.kpis['P2'].updateIndex(pCur, iCur, 1.)
        self.kpis['P2'].convertDaysToImpactAndFinalizeIndex(1.)

        iCur=tbm.P4.impact
        self.kpis['P4'].updateIndex(pCur, iCur, 1.)
        self.kpis['P4'].convertDaysToImpactAndFinalizeIndex(1.)

        iCur=tbm.V1.impact
        self.kpis['V1'].updateIndex(pCur, iCur, 1.)
        self.kpis['V1'].finalizeIndex(1.)

        iCur=tbm.V2.impact
        self.kpis['V2'].updateIndex(pCur, iCur, 1.)
        self.kpis['V2'].finalizeIndex(1.)

        iCur=tbm.V3.impact
        self.kpis['V3'].updateIndex(pCur, iCur, 1.)
        self.kpis['V3'].finalizeIndex(1.)

        iCur=tbm.V4.impact
        self.kpis['V4'].updateIndex(pCur, iCur, 1.)
        self.kpis['V4'].finalizeIndex(1.)

        iCur=tbm.V5.impact
        self.kpis['V5'].updateIndex(pCur, iCur, 1.)
        self.kpis['V5'].finalizeIndex(1.)

        iCur=tbm.V6.impact
        self.kpis['V6'].updateIndex(pCur, iCur, 1.)
        self.kpis['V6'].finalizeIndex(1.)

    def setKPI4SEG(self,tbmsect, p):
        # aggiorno indici produzione. l'impatto medio dovra' poi essere diviso per la lunghezza del tracciato
        pCur=tbmsect.P0.probability
        iCur=tbmsect.P0.impact
        self.kpis['P0'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.P1.probability
        iCur=tbmsect.P1.impact
        self.kpis['P1'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.P3.probability
        iCur=tbmsect.P3.impact
        self.kpis['P3'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.P5.probability
        iCur=tbmsect.P5.impact
        self.kpis['P5'].updateIndex(pCur, iCur, p.length)

        # aggiorno indici geotecnici
        pCur=tbmsect.G1.probability
        iCur=tbmsect.G1.impact
        self.kpis['G1'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G2.probability
        iCur=tbmsect.G2.impact
        self.kpis['G2'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G5.probability
        iCur=tbmsect.G5.impact
        self.kpis['G5'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G6.probability
        iCur=tbmsect.G6.impact
        self.kpis['G6'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G7.probability
        iCur=tbmsect.G7.impact
        self.kpis['G7'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G8.probability
        iCur=tbmsect.G8.impact
        self.kpis['G8'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G11.probability
        iCur=tbmsect.G11.impact
        self.kpis['G11'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G12.probability
        iCur=tbmsect.G12.impact
        self.kpis['G12'].updateIndex(pCur, iCur, p.length)

        pCur=tbmsect.G13.probability
        iCur=tbmsect.G13.impact
        self.kpis['G13'].updateIndex(pCur, iCur, p.length)

    def updateKPI(self, alnCurr):
        self.kpis['P0'].convertDaysToImpactAndFinalizeIndex(alnCurr.length)
        self.kpis['P1'].convertDaysToImpactAndFinalizeIndex(alnCurr.length)
        self.kpis['P3'].convertDaysToImpactAndFinalizeIndex(alnCurr.length)
        self.kpis['P5'].convertDaysToImpactAndFinalizeIndex(alnCurr.length)

        self.kpis['G1'].finalizeIndex(alnCurr.length)
        self.kpis['G2'].finalizeIndex(alnCurr.length)
        self.kpis['G5'].finalizeIndex(alnCurr.length)
        self.kpis['G6'].finalizeIndex(alnCurr.length)
        self.kpis['G7'].finalizeIndex(alnCurr.length)
        self.kpis['G8'].finalizeIndex(alnCurr.length)
        self.kpis['G11'].finalizeIndex(alnCurr.length)
        self.kpis['G12'].finalizeIndex(alnCurr.length)
        self.kpis['G13'].finalizeIndex(alnCurr.length)

    def getBbtTbmKpis(self):
        for key in self.kpis:
            _kpi = self.kpis[key]
            bbttbmkpi = BbtTbmKpi(self.tunnelName, self.tbmName,self.iterationNo,key, _kpi.definition, _kpi.minImpact, _kpi.maxImpact, _kpi.avgImpact, _kpi.appliedLength, _kpi.percentOfApplication, _kpi.probabilityScore, _kpi.totalImpact)
            self.bbttbmkpis.append(bbttbmkpi)
        return self.bbttbmkpis

    def saveBbtTbmKpis(self,sDBPath):
        conn = sqlite3.connect(sDBPath)
        c = conn.cursor()
        c.execute("DELETE FROM BbtTbmKpi WHERE tunnelName='%s' AND tbmName='%s' AND iterationNo=%d" % (self.tunnelName,self.tbmName, self.iterationNo))
        for key in self.kpis:
            _kpi = self.kpis[key]
            bbttbmkpi = BbtTbmKpi(self.tunnelName, self.tbmName,self.iterationNo,key, _kpi.definition, _kpi.minImpact, _kpi.maxImpact, _kpi.avgImpact, _kpi.appliedLength, _kpi.percentOfApplication, _kpi.probabilityScore, _kpi.totalImpact)
            c.execute("INSERT INTO BbtTbmKpi (tunnelName,tbmName,iterationNo,kpiKey,kpiDescr,minImpact,maxImpact,avgImpact,appliedLength,percentOfApplication,probabilityScore,totalImpact) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", bbttbmkpi)
            self.bbttbmkpis.append(bbttbmkpi)
        conn.commit()
        conn.close()
        return self.bbttbmkpis

    def printoutKPI(self):
        for key in self.kpis:
            _kpi = self.kpis[key]
            print '%s;%s;%d;%s;%s;%f;%f;%f;%f;%f;%f;%f' \
                % (self.tunnelName, self.tbmName,self.iterationNo,key, _kpi.definition, _kpi.minImpact, _kpi.maxImpact, _kpi.avgImpact, _kpi.appliedLength, _kpi.percentOfApplication, _kpi.probabilityScore, _kpi.totalImpact)

def build_normfunc_dict(bbt_parameter):
    gamma = get_my_norm(bbt_parameter.g_med,bbt_parameter.g_stddev,'gamma')
    sci = get_my_norm(bbt_parameter.sigma_ci_avg,bbt_parameter.sigma_ci_stdev,'sigma')
    mi = get_my_norm(bbt_parameter.mi_med,bbt_parameter.mi_stdev,'mi')
    ei = get_my_norm(bbt_parameter.ei_med,bbt_parameter.ei_stdev,'ei')
    cai = get_my_norm(bbt_parameter.cai_med,bbt_parameter.cai_stdev,'cai')
    gsi = get_my_norm(bbt_parameter.gsi_med,bbt_parameter.gsi_stdev,'gsi')
    rmr =  get_my_norm(bbt_parameter.rmr_med,bbt_parameter.rmr_stdev,'rmr')
    sti = get_my_norm_min_max(bbt_parameter.sigma_ti_min,bbt_parameter.sigma_ti_max,'sigma_ti')
    k0 = get_my_norm_min_max(bbt_parameter.k0_min,bbt_parameter.k0_max,'k0')
    return {'gamma':gamma,'sci':sci,'mi':mi,'ei':ei,'cai':cai,'gsi':gsi,'rmr':rmr,'sti':sti,'k0':k0}

def build_bbtparameter4seg_from_bbt_parameter(bbt_parameter, normfunc_dict):
    length = abs(bbt_parameter.fine - bbt_parameter.inizio)
    gamma = normfunc_dict['gamma'].rvs()
    sci = normfunc_dict['sci'].rvs()
    mi = normfunc_dict['mi'].rvs()
    ei = normfunc_dict['ei'].rvs()
    cai = normfunc_dict['cai'].rvs()
    gsi = normfunc_dict['gsi'].rvs()
    rmr =  normfunc_dict['rmr'].rvs()
    sti = normfunc_dict['sti'].rvs()
    k0 = normfunc_dict['k0'].rvs()
    bbtparameter4seg = BbtParameter4Seg(bbt_parameter.inizio,bbt_parameter.fine,length,bbt_parameter.he,bbt_parameter.hp,bbt_parameter.co,gamma,sci,mi,ei,cai ,gsi, rmr, bbt_parameter.profilo_id ,bbt_parameter.geoitem_id, bbt_parameter.title, sti, k0, bbt_parameter.k0_min, bbt_parameter.k0_max )
    return bbtparameter4seg
