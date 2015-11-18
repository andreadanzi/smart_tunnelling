import sqlite3, os
from bbtnamedtuples import *


def get_bbtparameterseval(sDBPath):
    conn = sqlite3.connect(sDBPath)
    conn.row_factory = bbtparametereval_factory
    cur = conn.cursor()
    bbtresults = cur.execute("SELECT insertdate,iteration_no,fine,he,hp,co,gamma,sigma,mi,ei,cai,gsi,rmr,pkgl,closure,rockburst,front_stability_ns,front_stability_lambda,penetrationRate,penetrationRateReduction,contactThrust,torque,frictionForce,requiredThrustForce,availableThrust,dailyAdvanceRate,profilo_id,geoitem_id,title,sigma_ti,k0 FROM BbtParameterEval ORDER BY iteration_no, profilo_id")
    bbt_bbtparameterseval = []
    for bbt_parametereval in bbtresults:
        bbt_bbtparameterseval.append(bbt_parametereval)
    conn.close()
    return bbt_bbtparameterseval


def get_bbtparameters(sDBPath):
    conn = sqlite3.connect(sDBPath)
    conn.row_factory = bbtparameter_factory
    cur = conn.cursor()
    bbtresults = cur.execute("SELECT inizio,fine,est,nord,he,hp,co,tipo,g_med,g_stddev,sigma_ci_avg,sigma_ci_stdev,mi_med,mi_stdev,ei_med,ei_stdev,cai_med,cai_stdev,gsi_med,gsi_stdev,rmr_med,rmr_stdev,profilo_id,geoitem_id,title,sigma_ti_min,sigma_ti_max,k0_min,k0_max FROM bbtparameter ORDER BY profilo_id")
    bbt_parameters = []
    for bbt_parameter in bbtresults:
        bbt_parameters.append(bbt_parameter)
    conn.close()
    return bbt_parameters

def insert_parameters(sDBPath,bbtpar_items):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute('delete from BbtParameter')
    for bbtpar in bbtpar_items:
        c.execute('insert into BbtParameter (inizio,fine,est,nord,he,hp,co,tipo,g_med,g_stddev,sigma_ci_avg,sigma_ci_stdev,mi_med,mi_stdev,ei_med,ei_stdev,cai_med,cai_stdev,gsi_med,gsi_stdev,rmr_med,rmr_stdev,profilo_id,geoitem_id,title,sigma_ti_min,sigma_ti_max,k0_min,k0_max) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', bbtpar)
    conn.commit()
    conn.close()

def insert_profilo(sDBPath,profilo_list):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute('delete from BbtProfilo')
    for bbtpro in profilo_list:
        c.execute('insert into BbtProfilo (id,inizio,fine,est,nord,he,hp,co,tipo) values (?,?,?,?,?,?,?,?,?)', bbtpro)
    conn.commit()
    conn.close()

def insert_geoitems(sDBPath,geoseg_list):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute('delete from BbtGeoitem')
    for geoseg in geoseg_list:
        c.execute('insert into BbtGeoitem (id,inizio,fine,l,perc,type,g_med,g_stddev,sigma_ci_avg,sigma_ci_stdev,mi_med,mi_stdev,ei_med,ei_stdev,cai_med,cai_stdev,gsi_med,gsi_stdev,rmr_med,rmr_stdev,title,sigma_ti_min,sigma_ti_max,k0_min,k0_max ) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', geoseg)
    conn.commit()
    conn.close()

def insert_bbtreliability(sDBPath, reliability_list):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute('delete from BbtReliability')
    for rel in reliability_list:
        c.execute('insert into BbtReliability (id ,inizio, fine , gmr_class, gmr_val, reliability, eval_var) values (?,?,?,?,?,?,?)', rel)
    conn.commit()
    conn.close()

def compact_database(sDBPath):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute("VACUUM")
    conn.commit()
    conn.close()

def insert_BbtTbm(sDBPath, tbm_list):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute('delete from BbtTbm')
    for rel in reliability_list:
        c.execute('insert into BbtTbm (id ,inizio, fine , gmr_class, gmr_val, reliability, eval_var) values (?,?,?,?,?,?,?)', rel)
    conn.commit()
    conn.close()

#danzi.tn@20151114 inseriti nuovi parametri calcolati su TunnelSegment
def insert_bbtparameterseval(sDBPath, bbt_evalparameters, iteration_no=0):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    isFirst=True
    for bbtpar in bbt_evalparameters:
        if isFirst:
            c.execute("delete from BbtParameterEval WHERE iteration_no = %d AND tunnelName ='%s' AND tbmName='%s'" % (bbtpar[1],bbtpar[2],bbtpar[3]))
            isFirst=False
        c.execute("insert into BbtParameterEval (           insertdate,\
                                                            iteration_no, \
                                                            tunnelName,\
                                                            tbmName,\
                                                            fine,\
                                                            he,\
                                                            hp,\
                                                            co,\
                                                            gamma,\
                                                            sigma,\
                                                            mi,\
                                                            ei,\
                                                            cai,\
                                                            gsi,\
                                                            rmr,\
                                                            pkgl,\
                                                            closure,\
                                                            rockburst,\
                                                            front_stability_ns,\
                                                            front_stability_lambda,\
                                                            penetrationRate,\
                                                            penetrationRateReduction,\
                                                            contactThrust,\
                                                            torque,\
                                                            frictionForce,\
                                                            requiredThrustForce,\
                                                            availableThrust,\
                                                            dailyAdvanceRate,profilo_id, geoitem_id ,title,sigma_ti,k0,t0,t1,t3,t4,t5, \
                                                            inSituConditionSigmaV,\
                                                            tunnelRadius,\
                                                            rockE,\
                                                            mohrCoulombPsi,\
                                                            rockUcs,\
                                                            inSituConditionGsi,\
                                                            hoekBrownMi,\
                                                            hoekBrownD,\
                                                            hoekBrownMb,\
                                                            hoekBrownS,\
                                                            hoekBrownA,\
                                                            hoekBrownMr,\
                                                            hoekBrownSr,\
                                                            hoekBrownAr,\
                                                            urPiHB,\
                                                            rpl,\
                                                            picr,\
                                                            ldpVlachBegin,\
                                                            ldpVlachEnd\
        ) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", bbtpar)
    conn.commit()
    conn.close()



def insert_one_bbtparameterseval(cur, bbtpar):
    cur.execute("insert into BbtParameterEval (           insertdate,\
                                                        iteration_no, \
                                                        fine,\
                                                        he,\
                                                        hp,\
                                                        co,\
                                                        gamma,\
                                                        sigma,\
                                                        mi,\
                                                        ei,\
                                                        cai,\
                                                        gsi,\
                                                        rmr,\
                                                        pkgl,\
                                                        closure,\
                                                        rockburst,\
                                                        front_stability_ns,\
                                                        front_stability_lambda,\
                                                        penetrationRate,\
                                                        penetrationRateReduction,\
                                                        contactThrust,\
                                                        torque,\
                                                        frictionForce,\
                                                        requiredThrustForce,\
                                                        availableThrust,\
                                                        dailyAdvanceRate,profilo_id, geoitem_id ,title,sigma_ti,k0 \
    ) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", bbtpar)


# danzi.tn@20151116 pulizia delle valutazioni
def clean_all_eval_ad_kpi(sDBPath):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute("delete from BbtParameterEval")
    c.execute("delete from BbtTbmKpi")
    conn.commit()
    conn.close()


def load_tbm_table(sDBPath, tbmsDict):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute("delete from BbtTbm")
    for tbmKey in tbmsDict:
        tbmData = tbmsDict[tbmKey]
        inputVal = (tbmData.name,tbmData.alignmentCode,tbmData.manifacturer,tbmData.type,tbmData.shieldLength,tbmData.overcut)
        c.execute("INSERT INTO BbtTbm (name,alignmentCode,manufacturer,type,shieldLength,overcut) VALUES (?,?,?,?,?,?)", inputVal)
    conn.commit()
    conn.close()
