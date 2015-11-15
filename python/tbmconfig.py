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
    frictionCoefficient=0.
    openingRatio=0.
    cutterheadThickness=0.8 # in metri lo spessore della testa di scavo
    dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata

tbms={}

#TBM 1
tbm1=TBMConfig()
tbm1.name = 'GL_O_BBT '
tbm1.manifacturer='BBT'
tbm1.alignmentCode='GLSUD'
tbm1.type='O' # O = open, S = single shield, DS = double shield
tbm1.shieldLength=2. 
tbm1.frontShieldDiameter=0.
tbm1.tailShieldDiameter=0.
tbm1.excavationDiameter=9.72
tbm1.overcut=0.05
tbm1.loadPerCutter=250.
tbm1.cutterSize=17.*0.0254 #diameter
tbm1.cutterSpacing=0.1
tbm1.cutterThickness=0.02
tbm1.cutterCount=76
tbm1.totalContactThrust=tbm1.loadPerCutter*tbm1.cutterCount
tbm1.referenceRpm=5.
tbm1.nominalTorque=9000.
tbm1.breakawayTorque=9000.
tbm1.backupDragForce=6000.
tbm1.frictionCoefficient=0.15
tbm1.nominalThrustForce=tbm1.totalContactThrust+2.*tbm1.backupDragForce
tbm1.auxiliaryThrustForce=1.1*tbm1.nominalThrustForce
tbm1.openingRatio=0.1
tbms[tbm1.name] = tbm1

#TBM 2
tbm2=TBMConfig()
tbm2.name = 'GL_S_BBT'
tbm2.alignmentCode='GLSUD;GLNORD'
tbm2.manifacturer='BBT'
tbm2.type='S' # O = open, S = single shield, DS = double shield
tbm2.shieldLength=10. 
tbm2.frontShieldDiameter=10.27
tbm2.tailShieldDiameter=10.27
tbm2.excavationDiameter=10.47
tbm2.overcut=0.1
tbm2.loadPerCutter=250.
tbm2.cutterSize=17.*0.0254 #diameter
tbm2.cutterSpacing=0.1
tbm2.cutterThickness=0.02
tbm2.cutterCount=80
tbm2.referenceRpm=5.
tbm2.totalContactThrust=tbm2.loadPerCutter*tbm2.cutterCount
tbm2.nominalTorque=9500.
tbm2.breakawayTorque=9500.
tbm2.backupDragForce=8000.
tbm2.frictionCoefficient=0.15
tbm2.nominalThrustForce=tbm2.totalContactThrust+2.*tbm2.backupDragForce
tbm2.auxiliaryThrustForce=1.1*tbm2.nominalThrustForce
tbm2.openingRatio=0.1
tbms[tbm2.name] = tbm2

#TBM 3
tbm3=TBMConfig()
tbm3.name = 'CE_S_BBT'
tbm3.alignmentCode='CE'
tbm3.manifacturer='BBT'
tbm3.type='S' # O = open, S = single shield, DS = double shield
tbm3.shieldLength=10. 
tbm3.frontShieldDiameter=6.42
tbm3.tailShieldDiameter=6.42
tbm3.excavationDiameter=6.62
tbm3.overcut=0.1
tbm3.loadPerCutter=250.
tbm3.cutterSize=17.*0.0254 #diameter
tbm3.cutterSpacing=0.1
tbm3.cutterThickness=0.02
tbm3.cutterCount=48
tbm3.totalContactThrust=tbm3.loadPerCutter*tbm3.cutterCount
tbm3.referenceRpm=8.
tbm3.nominalTorque=9500.
tbm3.breakawayTorque=4000.
tbm3.backupDragForce=4000.
tbm3.frictionCoefficient=0.15
tbm3.nominalThrustForce=tbm3.totalContactThrust+2.*tbm3.backupDragForce
tbm3.auxiliaryThrustForce=1.1*tbm3.nominalThrustForce
tbm3.openingRatio=0.1
tbms[tbm3.name] = tbm3

#TBM 4
tbm4=TBMConfig()
tbm4.name = 'GL_O_HRK'
tbm4.alignmentCode='GLSUD'
tbm4.manifacturer='Herrenknecht'
tbm4.type='O' # O = open, S = single shield, DS = double shield
tbm4.shieldLength=3.88 
tbm4.frontShieldDiameter=7.
tbm4.tailShieldDiameter=7.
tbm4.excavationDiameter=9.72
tbm4.overcut=0.05
tbm4.loadPerCutter=315.
tbm4.cutterCount=56
tbm4.cutterSize=19.*0.0254 #diameter
tbm4.cutterSpacing=0.1
tbm4.cutterThickness=0.02
tbm4.totalContactThrust=tbm4.loadPerCutter*tbm4.cutterCount
tbm4.referenceRpm=5.
tbm4.nominalTorque=10238.
tbm4.breakawayTorque=16381.
tbm4.backupDragForce=6000.
tbm4.frictionCoefficient=0.15
tbm4.nominalThrustForce=27489.
tbm4.auxiliaryThrustForce=tbm4.nominalThrustForce
tbm4.openingRatio=0.1
tbms[tbm4.name] = tbm4

#TBM 5
tbm5=TBMConfig()
tbm5.name = 'GL_S_HRK'
tbm5.alignmentCode='GLSUD;GLNORD'
tbm5.manifacturer='Herrenknecht'
tbm5.type='S' # O = open, S = single shield, DS = double shield
tbm5.shieldLength=9.915 
tbm5.frontShieldDiameter=10.46
tbm5.tailShieldDiameter=10.42
tbm5.excavationDiameter=10.52
tbm5.overcut=0.1
tbm5.loadPerCutter=315.
tbm5.cutterSize=19.*0.0254 #diameter
tbm5.cutterSpacing=0.1
tbm5.cutterThickness=0.02
tbm5.cutterCount=62
tbm5.referenceRpm=5.
tbm5.totalContactThrust=tbm5.loadPerCutter*tbm5.cutterCount
tbm5.nominalTorque=12618.
tbm5.breakawayTorque=21451.
tbm5.backupDragForce=8000.
tbm5.frictionCoefficient=0.15
tbm5.nominalThrustForce=106965.
tbm5.auxiliaryThrustForce=tbm5.nominalThrustForce
tbm5.openingRatio=0.1
tbms[tbm5.name] = tbm5

#TBM 6
tbm6=TBMConfig()
tbm6.name = 'GL_DS_HRK'
tbm6.alignmentCode='GLSUD;GLNORD'
tbm6.manifacturer='Herrenknecht'
tbm6.type='DS' # O = open, S = single shield, DS = double shield
tbm6.shieldLength=12.25 
tbm6.frontShieldDiameter=10.62
tbm6.tailShieldDiameter=10.42
tbm6.excavationDiameter=10.68
tbm6.overcut=0.1
tbm6.loadPerCutter=315.
tbm6.cutterSize=19.*0.0254 #diameter
tbm6.cutterSpacing=0.1
tbm6.cutterThickness=0.02
tbm6.cutterCount=62
tbm6.referenceRpm=5.
tbm6.totalContactThrust=tbm6.loadPerCutter*tbm6.cutterCount
tbm6.nominalTorque=12618.
tbm6.breakawayTorque=21451.
tbm6.backupDragForce=8000.
tbm6.frictionCoefficient=0.15
tbm6.nominalThrustForce=79168.
tbm6.auxiliaryThrustForce=106965.
tbm6.openingRatio=0.1
tbms[tbm6.name] = tbm6

#TBM 7
tbm7=TBMConfig()
tbm7.name = 'CE_S_HRK'
tbm7.alignmentCode='CE'
tbm7.manifacturer='Herrenknecht'
tbm7.type='S' # O = open, S = single shield, DS = double shield
tbm7.shieldLength=11.76
tbm7.frontShieldDiameter=6.69
tbm7.tailShieldDiameter=6.65
tbm7.excavationDiameter=6.85
tbm7.overcut=0.05
tbm7.loadPerCutter=315.
tbm7.cutterSize=19.*0.0254 #diameter
tbm7.cutterSpacing=0.1
tbm7.cutterThickness=0.02
tbm7.cutterCount=38
tbm7.totalContactThrust=tbm7.loadPerCutter*tbm7.cutterCount
tbm7.referenceRpm=8.
tbm7.nominalTorque=4375.
tbm7.breakawayTorque=6343.
tbm7.backupDragForce=4000.
tbm7.frictionCoefficient=0.15
tbm7.nominalThrustForce=35626.
tbm7.auxiliaryThrustForce=35626.
tbm7.openingRatio=0.1
tbms[tbm7.name] = tbm7

#TBM 8
tbm8=TBMConfig()
tbm8.name = 'CE_DS_HRK'
tbm8.alignmentCode='CE'
tbm8.manifacturer='Herrenknecht'
tbm8.type='DS' # O = open, S = single shield, DS = double shield
tbm8.shieldLength=11.76 + .8
tbm8.frontShieldDiameter=6.85
tbm8.tailShieldDiameter=6.65
tbm8.excavationDiameter=6.85
tbm8.overcut=0.1
tbm8.loadPerCutter=315.
tbm8.cutterSize=19.*0.0254 #diameter
tbm8.cutterSpacing=0.1
tbm8.cutterThickness=0.02
tbm8.cutterCount=39
tbm8.totalContactThrust=tbm8.loadPerCutter*tbm8.cutterCount
tbm8.referenceRpm=8.
tbm8.nominalTorque=4375.
tbm8.breakawayTorque=6343.
tbm8.backupDragForce=4000.
tbm8.frictionCoefficient=0.15
tbm8.nominalThrustForce=35626.
tbm8.auxiliaryThrustForce=42223.
tbm8.openingRatio=0.1
tbms[tbm8.name] = tbm8

#TBM 9
tbm9=TBMConfig()
tbm9.name = 'GL_O_RBS'
tbm9.alignmentCode='GLSUD'
tbm9.manifacturer='Robbins'
tbm9.type='O' # O = open, S = single shield, DS = double shield
tbm9.shieldLength=3.88 
tbm9.frontShieldDiameter=7.
tbm9.tailShieldDiameter=7.
tbm9.excavationDiameter=9.72
tbm9.overcut=0.05
tbm9.loadPerCutter=311.
tbm9.cutterCount=61
tbm9.cutterSize=19.*0.0254 #diameter
tbm9.cutterSpacing=0.1
tbm9.cutterThickness=0.02
tbm9.totalContactThrust=20600.
tbm9.referenceRpm=5.
tbm9.nominalTorque=10220.
tbm9.breakawayTorque=15330.
tbm9.backupDragForce=6000.
tbm9.frictionCoefficient=0.15
tbm9.nominalThrustForce=22640.
tbm9.auxiliaryThrustForce=tbm9.nominalThrustForce
tbm9.openingRatio=0.1
tbms[tbm9.name] = tbm9

#TBM 10
tbm10=TBMConfig()
tbm10.name = 'GL_DS_RBS'
tbm10.alignmentCode='GLSUD;GLNORD'
tbm10.manifacturer='Robbins'
tbm10.type='DS' # O = open, S = single shield, DS = double shield
tbm10.shieldLength=12.25 
tbm10.frontShieldDiameter=7.
tbm10.tailShieldDiameter=7.
tbm10.excavationDiameter=10.47
tbm10.overcut=0.1
tbm10.loadPerCutter=311.4
tbm10.cutterCount=74
tbm10.cutterSize=19.*0.0254 #diameter
tbm10.cutterSpacing=0.0723
tbm10.cutterThickness=0.02
tbm10.totalContactThrust=22419.
tbm10.referenceRpm=5.
tbm10.nominalTorque=8560.
tbm10.breakawayTorque=18696.
tbm10.backupDragForce=8000.
tbm10.frictionCoefficient=0.15
tbm10.nominalThrustForce=69305.
tbm10.auxiliaryThrustForce=116952.
tbm10.openingRatio=0.1
tbms[tbm10.name] = tbm10

#TBM 11
tbm11=TBMConfig()
tbm11.name = 'CE_DS_RBS'
tbm11.alignmentCode='CE'
tbm11.manifacturer='Robbins'
tbm11.type='DS' # O = open, S = single shield, DS = double shield
tbm11.shieldLength=14.5 
tbm11.frontShieldDiameter=6.62
tbm11.frontShieldLength=6.5
tbm11.tailShieldDiameter=6.56
tbm11.excavationDiameter=6.82
tbm11.overcut=0.1
tbm11.loadPerCutter=267.
tbm11.cutterSize=17.*0.0254 #diameter
tbm11.cutterSpacing=0.1
tbm11.cutterThickness=0.02
tbm11.cutterCount=43
tbm11.totalContactThrust=tbm11.loadPerCutter*tbm11.cutterCount
tbm11.referenceRpm=8.
tbm11.nominalTorque=6000.
tbm11.breakawayTorque=14053.
tbm11.backupDragForce=4000.
tbm11.nominalThrustForce=40000.
tbm11.auxiliaryThrustForce=61965.
tbm11.openingRatio=0.1
tbm11.dotationForProspection=0.9
tbms[tbm11.name] = tbm11

#TBM 11_bis
tbm12=TBMConfig()
tbm12.name = 'CE_DS_RBS_OCRID'
tbm12.alignmentCode='CE'
tbm12.manifacturer='Robbins'
tbm12.type='DS' # O = open, S = single shield, DS = double shield
tbm12.shieldLength=14.5 
tbm12.frontShieldDiameter=6.62
tbm12.frontShieldLength=6.5
tbm12.tailShieldDiameter=6.56
tbm12.excavationDiameter=6.7
tbm12.overcut=0.04
tbm12.loadPerCutter=267.
tbm12.cutterSize=17.*0.0254 #diameter
tbm12.cutterSpacing=0.1
tbm12.cutterThickness=0.02
tbm12.cutterCount=43
tbm12.totalContactThrust=tbm12.loadPerCutter*tbm12.cutterCount
tbm12.referenceRpm=8.
tbm12.nominalTorque=6000.
tbm12.breakawayTorque=14053.
tbm12.backupDragForce=4000.
tbm12.nominalThrustForce=40000.
tbm12.auxiliaryThrustForce=61965.
tbm12.openingRatio=0.1
tbm12.dotationForProspection=0.9
tbms[tbm12.name] = tbm12

#TBM 11_ter
tbm13=TBMConfig()
tbm13.name = 'CE_DS_RBS_TORQUERID'
tbm13.alignmentCode='CE'
tbm13.manifacturer='Robbins'
tbm13.type='DS' # O = open, S = single shield, DS = double shield
tbm13.shieldLength=14.5 
tbm13.frontShieldDiameter=6.62
tbm13.frontShieldLength=6.5
tbm13.tailShieldDiameter=6.56
tbm13.excavationDiameter=6.82
tbm13.overcut=0.1
tbm13.loadPerCutter=267.
tbm13.cutterSize=17.*0.0254 #diameter
tbm13.cutterSpacing=0.1
tbm13.cutterThickness=0.02
tbm13.cutterCount=43
tbm13.totalContactThrust=tbm13.loadPerCutter*tbm13.cutterCount
tbm13.referenceRpm=8.
tbm13.nominalTorque=4000.
tbm13.breakawayTorque=6000.
tbm13.backupDragForce=4000.
tbm13.nominalThrustForce=40000.
tbm13.auxiliaryThrustForce=61965.
tbm13.openingRatio=0.1
tbm13.dotationForProspection=0.9
tbms[tbm13.name] = tbm13

#TBM 11_quater
tbm14=TBMConfig()
tbm14.name = 'CE_S_RBS_DEMO'
tbm14.alignmentCode='CE'
tbm14.manifacturer='Robbins'
tbm14.type='S' # O = open, S = single shield, DS = double shield
tbm14.shieldLength=13 
tbm14.frontShieldDiameter=6.62
tbm14.frontShieldLength=13
tbm14.tailShieldDiameter=6.56
tbm14.excavationDiameter=6.82
tbm14.overcut=0.1
tbm14.loadPerCutter=267.
tbm14.cutterSize=17.*0.0254 #diameter
tbm14.cutterSpacing=0.1
tbm14.cutterThickness=0.02
tbm14.cutterCount=43
tbm14.totalContactThrust=tbm14.loadPerCutter*tbm14.cutterCount
tbm14.referenceRpm=8.
tbm14.nominalTorque=6000.
tbm14.breakawayTorque=14053.
tbm14.backupDragForce=4000.
tbm14.nominalThrustForce=40000.
tbm14.auxiliaryThrustForce=61965.
tbm14.openingRatio=0.1
tbm14.dotationForProspection=0.9
tbms[tbm14.name] = tbm14

