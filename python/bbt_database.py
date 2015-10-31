import sqlite3, os
from bbtnamedtuples import *

def get_bbtparameters(sDBPath):
    conn = sqlite3.connect(sDBPath)
    conn.row_factory = bbtparameter_factory
    cur = conn.cursor()
    print "start querying database  "
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


def insert_bbtparameterseval(sDBPath, bbt_evalparameters, iteration_no=0):
    conn = sqlite3.connect(sDBPath)
    c = conn.cursor()
    c.execute("delete from BbtParameterEval WHERE iteration_no = %d" % iteration_no)
    for bbtpar in bbt_evalparameters:
        c.execute("insert into BbtParameterEval (           insertdate,\
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
    conn.commit()
    conn.close()
