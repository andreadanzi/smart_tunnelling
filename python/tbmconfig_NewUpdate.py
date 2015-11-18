class TBMConfig:
    # nominalTorque, breakawayTorque, backupDragForce, friction, LDP_type
    # length in m
    # forces in kN
    name=''
    manifacturer=''
    type='' # O = open, S = single shield, DS = double shield
    alignmentCode=''
    shieldLength=0.
    frontShieldLength=0.
    frontShieldDiameter=0.
    tailShieldDiameter=0.
    nominalThrustForce=0.
    auxiliaryThrustForce=0.
    excavationDiameter=0.
    overcut=0.
    loadPerCutter=0.
    totalContactThrust=0.
    cutterSize=0. #diameter
    cutterSpacing=0.
    cutterThickness=0.
    cutterCount=0
    referenceRpm=0.
    nominalTorque=0.
    breakawayTorque=0.
    backupDragForce=0.
    openingRatio=0.
    cutterheadThickness=0.8 # in metri lo spessore della testa di scavo
    dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata

tbms={}

#TBM 6
tbm6=TBMConfig()
tbm6.name = 'GL_DS_HRK_10.64'
tbm6.alignmentCode='GLSUD;GLNORD'
tbm6.manifacturer='Herrenknecht'
tbm6.type='DS' # O = open, S = single shield, DS = double shield
tbm6.shieldLength=11.+1.1 
tbm6.frontShieldLength=4.82+1.1
tbm6.frontShieldDiameter=10.58
tbm6.tailShieldDiameter=10.44
tbm6.excavationDiameter=10.64
tbm6.overcut=0.1
tbm6.loadPerCutter=315.
tbm6.cutterSize=19.*0.0254 #diameter
tbm6.cutterSpacing=0.085
tbm6.cutterThickness=0.02
tbm6.cutterCount=64
tbm6.referenceRpm=3.
tbm6.totalContactThrust=tbm6.loadPerCutter*tbm6.cutterCount
tbm6.nominalTorque=13500.
tbm6.breakawayTorque=30300.
tbm6.backupDragForce=8000.
tbm6.nominalThrustForce=79168.
tbm6.auxiliaryThrustForce=152800.
tbm6.openingRatio=0.05
tbm6.cutterheadThickness=1.1 # in metri lo spessore della testa di scavo
tbm6.dotationForProspection=1. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm6.name] = tbm6

#TBM 23
tbm23=TBMConfig()
tbm23.name = 'CE_DS_RBS_6.73'
tbm23.alignmentCode='CE'
tbm23.manifacturer='Robbins'
tbm23.type='DS' # O = open, S = single shield, DS = double shield
tbm23.shieldLength=11.+.9 
tbm23.frontShieldDiameter=6.67
tbm23.frontShieldLength=4.3+.9
tbm23.tailShieldDiameter=6.56
tbm23.excavationDiameter=6.73
tbm23.overcut=0.1
tbm23.loadPerCutter=267.
tbm23.cutterSize=17.*0.0254 #diameter
tbm23.cutterSpacing=0.087
tbm23.cutterThickness=0.02
tbm23.cutterCount=45
tbm23.totalContactThrust=tbm23.loadPerCutter*tbm23.cutterCount
tbm23.referenceRpm=5.4
tbm23.nominalTorque=4053.
tbm23.breakawayTorque=14034.
tbm23.backupDragForce=4000.
tbm23.nominalThrustForce=27630.
tbm23.auxiliaryThrustForce=97205.
tbm23.openingRatio=0.1
tbm23.dotationForProspection=1.
tbm23.cutterheadThickness=.9 
tbms[tbm23.name] = tbm23

