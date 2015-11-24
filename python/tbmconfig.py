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

#TBM 4
tbm4=TBMConfig()
tbm4.name = 'GL_O_HRK_9.72'
tbm4.alignmentCode='GLSUD'
tbm4.manifacturer='Herrenknecht'
tbm4.type='O' # O = open, S = single shield, DS = double shield
tbm4.shieldLength=1.1 
tbm4.frontShieldDiameter=9.62
tbm4.tailShieldDiameter=9.62
tbm4.excavationDiameter=9.72
tbm4.overcut=0.05
tbm4.loadPerCutter=315.
tbm4.cutterCount=56
tbm4.cutterSize=19.*0.0254 #diameter
tbm4.cutterSpacing=0.085
tbm4.cutterThickness=0.02
tbm4.totalContactThrust=tbm4.loadPerCutter*tbm4.cutterCount
tbm4.referenceRpm=3.
tbm4.nominalTorque=10238.
tbm4.breakawayTorque=16381.
tbm4.backupDragForce=6000.
tbm4.nominalThrustForce=27489.
tbm4.auxiliaryThrustForce=tbm4.nominalThrustForce
tbm4.openingRatio=0.05
tbm4.cutterheadThickness=1.1 # in metri lo spessore della testa di scavo
tbm4.dotationForProspection=0.75 # da 0 a 1 se e' per niente o molto dotata
tbms[tbm4.name] = tbm4

#TBM 5
tbm5=TBMConfig()
tbm5.name = 'GL_S_HRK_10.54'
tbm5.alignmentCode='GLSUD;GLNORD'
tbm5.manifacturer='Herrenknecht'
tbm5.type='S' # O = open, S = single shield, DS = double shield
tbm5.shieldLength=9.845+1.1 
tbm5.frontShieldDiameter=10.48
tbm5.tailShieldDiameter=10.45
tbm5.excavationDiameter=10.54
tbm5.overcut=0.12
tbm5.loadPerCutter=315.
tbm5.cutterSize=19.*0.0254 #diameter
tbm5.cutterSpacing=0.085
tbm5.cutterThickness=0.02
tbm5.cutterCount=64
tbm5.referenceRpm=3.
tbm5.totalContactThrust=tbm5.loadPerCutter*tbm5.cutterCount
tbm5.nominalTorque=13500.
tbm5.breakawayTorque=30300.
tbm5.backupDragForce=8000.
tbm5.nominalThrustForce=106965.
tbm5.auxiliaryThrustForce=152800
tbm5.openingRatio=0.05
tbm5.cutterheadThickness=1.1 # in metri lo spessore della testa di scavo
tbm5.dotationForProspection=1. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm5.name] = tbm5

#TBM 6
tbm6=TBMConfig()
tbm6.name = 'GL_DS_HRK_10.64'
tbm6.alignmentCode='GLSUD;GLNORD'
tbm6.manifacturer='Herrenknecht'
tbm6.type='DS' # O = open, S = single shield, DS = double shield
tbm6.shieldLength=11.85+1. 
tbm6.frontShieldLength=4.82+1.
tbm6.frontShieldDiameter=10.58
tbm6.tailShieldDiameter=10.42
tbm6.excavationDiameter=10.64
tbm6.overcut=0.12
tbm6.loadPerCutter=315.
tbm6.cutterSize=19.*0.0254 #diameter
tbm6.cutterSpacing=0.085
tbm6.cutterThickness=0.02
tbm6.cutterCount=64
tbm6.referenceRpm=3.
tbm6.totalContactThrust=tbm6.loadPerCutter*tbm6.cutterCount
tbm6.nominalTorque=27000.
tbm6.breakawayTorque=30300.
tbm6.backupDragForce=8000.
tbm6.nominalThrustForce=79168.
tbm6.auxiliaryThrustForce=213000.
tbm6.openingRatio=0.05
tbm6.cutterheadThickness=1. # in metri lo spessore della testa di scavo
tbm6.dotationForProspection=1. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm6.name] = tbm6

#TBM 7
tbm7=TBMConfig()
tbm7.name = 'CE_S_HRK_6.74'
tbm7.alignmentCode='CE'
tbm7.manifacturer='Herrenknecht'
tbm7.type='S' # O = open, S = single shield, DS = double shield
tbm7.shieldLength=10.915+0.9
tbm7.frontShieldDiameter=6.69
tbm7.tailShieldDiameter=6.65
tbm7.excavationDiameter=6.74
tbm7.overcut=0.12
tbm7.loadPerCutter=315.
tbm7.cutterSize=19.*0.0254 #diameter
tbm7.cutterSpacing=0.085
tbm7.cutterThickness=0.02
tbm7.cutterCount=39
tbm7.totalContactThrust=tbm7.loadPerCutter*tbm7.cutterCount
tbm7.referenceRpm=5.
tbm7.nominalTorque=5250.
tbm7.breakawayTorque=11800.
tbm7.backupDragForce=4000.
tbm7.nominalThrustForce=42223.
tbm7.auxiliaryThrustForce=60236.
tbm7.openingRatio=0.05
tbm7.dotationForProspection=0.75 # da 0 a 1 se e' per niente o molto dotata
tbm7.cutterheadThickness=0.9 
tbms[tbm7.name] = tbm7

#TBM 8
tbm8=TBMConfig()
tbm8.name = 'CE_DS_HRK_6.82'
tbm8.alignmentCode='CE'
tbm8.manifacturer='Herrenknecht'
tbm8.type='DS' # O = open, S = single shield, DS = double shield
tbm8.shieldLength=11.695 + .9
tbm8.frontShieldDiameter=6.77
tbm8.frontShieldLength=4.595+.9
tbm8.tailShieldDiameter=6.65
tbm8.excavationDiameter=6.82
tbm8.overcut=0.12
tbm8.loadPerCutter=315.
tbm8.cutterSize=19.*0.0254 #diameter
tbm8.cutterSpacing=0.085
tbm8.cutterThickness=0.02
tbm8.cutterCount=39
tbm8.totalContactThrust=tbm8.loadPerCutter*tbm8.cutterCount
tbm8.referenceRpm=5.
tbm8.nominalTorque=5250.
tbm8.breakawayTorque=11800.
tbm8.backupDragForce=4000.
tbm8.nominalThrustForce=35539.
tbm8.auxiliaryThrustForce=60236.
tbm8.openingRatio=0.05
tbm8.dotationForProspection=0.75 # da 0 a 1 se e' per niente o molto dotata
tbm8.cutterheadThickness=0.9 
tbms[tbm8.name] = tbm8

#TBM 9
tbm9=TBMConfig()
tbm9.name = 'GL_O_RBS_9.72'
tbm9.alignmentCode='GLSUD'
tbm9.manifacturer='Robbins'
tbm9.type='O' # O = open, S = single shield, DS = double shield
tbm9.shieldLength=1. 
tbm9.frontShieldDiameter=9.62
tbm9.tailShieldDiameter=9.62
tbm9.excavationDiameter=9.72
tbm9.overcut=0.05
tbm9.loadPerCutter=333.
tbm9.cutterCount=62
tbm9.cutterSize=19.*0.0254 #diameter
tbm9.cutterSpacing=0.0732
tbm9.cutterThickness=0.02
tbm9.totalContactThrust=333.*62.
tbm9.referenceRpm=2.5
tbm9.nominalTorque=10220.
tbm9.breakawayTorque=15330.
tbm9.backupDragForce=6000.
tbm9.nominalThrustForce=22640.
tbm9.auxiliaryThrustForce=tbm9.nominalThrustForce
tbm9.openingRatio=0.1
tbm9.cutterheadThickness=1.0 # in metri lo spessore della testa di scavo
tbm9.dotationForProspection=1. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm9.name] = tbm9

#TBM 10
tbm10=TBMConfig()
tbm10.name = 'GL_DS_RBS_10.52'
tbm10.alignmentCode='GLSUD;GLNORD'
tbm10.manifacturer='Robbins'
tbm10.type='DS' # O = open, S = single shield, DS = double shield
tbm10.shieldLength=11.+1. 
tbm10.frontShieldLength=4.7+1.
tbm10.frontShieldDiameter=10.44
tbm10.tailShieldDiameter=10.32
tbm10.excavationDiameter=10.52
tbm10.overcut=0.1
tbm10.loadPerCutter=311.4
tbm10.cutterCount=72
tbm10.cutterSize=19.*0.0254 #diameter
tbm10.cutterSpacing=0.0732
tbm10.cutterThickness=0.02
tbm10.totalContactThrust=tbm10.cutterCount*tbm10.loadPerCutter
tbm10.referenceRpm=2.5
tbm10.nominalTorque=18696.
tbm10.breakawayTorque=33651.
tbm10.backupDragForce=8000.
tbm10.nominalThrustForce=69305.
tbm10.auxiliaryThrustForce=217519.
tbm10.openingRatio=0.1
tbm10.cutterheadThickness=1. # in metri lo spessore della testa di scavo
tbm10.dotationForProspection=1. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm10.name] = tbm10

#TBM 11
tbm11=TBMConfig()
tbm11.name = 'CE_DS_BBT_6.74'
tbm11.alignmentCode='CE'
tbm11.manifacturer='BBT'
tbm11.type='DS' # O = open, S = single shield, DS = double shield
tbm11.shieldLength=11.324+.9 
tbm11.frontShieldDiameter=6.705
tbm11.frontShieldLength=4.599+.9
tbm11.tailShieldDiameter=6.635
tbm11.excavationDiameter=6.739
tbm11.overcut=0.106
tbm11.loadPerCutter=250.
tbm11.cutterSize=17.*0.0254 #diameter
tbm11.cutterSpacing=0.086
tbm11.cutterThickness=0.02
tbm11.cutterCount=48
tbm11.totalContactThrust=tbm11.loadPerCutter*tbm11.cutterCount
tbm11.referenceRpm=5.
tbm11.nominalTorque=4000.
tbm11.breakawayTorque=7360.
tbm11.backupDragForce=4000.
tbm11.nominalThrustForce=21500.
tbm11.auxiliaryThrustForce=46180.
tbm11.openingRatio=0.084
tbm11.dotationForProspection=.5
tbm11.cutterheadThickness=.9 
tbms[tbm11.name] = tbm11

#TBM 12
tbm12=TBMConfig()
tbm12.name = 'CE_S_RBS_6.73'
tbm12.alignmentCode='CE'
tbm12.manifacturer='Robbins'
tbm12.type='S' # O = open, S = single shield, DS = double shield
tbm12.shieldLength=10.6+.9
tbm12.frontShieldDiameter=6.67
tbm12.tailShieldDiameter=6.56
tbm12.excavationDiameter=6.73
tbm12.overcut=0.10
tbm12.loadPerCutter=267.
tbm12.cutterSize=17.*0.0254 #diameter
tbm12.cutterSpacing=0.087
tbm12.cutterThickness=0.02
tbm12.cutterCount=42
tbm12.totalContactThrust=tbm12.loadPerCutter*tbm12.cutterCount
tbm12.referenceRpm=5.4
tbm12.nominalTorque=4053.
tbm12.breakawayTorque=14034.
tbm12.backupDragForce=4000.
tbm12.nominalThrustForce=57306.
tbm12.auxiliaryThrustForce=97205.
tbm12.openingRatio=0.1
tbm12.dotationForProspection=1. # da 0 a 1 se e' per niente o molto dotata
tbm12.cutterheadThickness=.9 
tbms[tbm12.name] = tbm12

#TBM 13
tbm13=TBMConfig()
tbm13.name = 'CE_DS_LOV_6.70'
tbm13.alignmentCode='CE'
tbm13.manifacturer='LOV'
tbm13.type='DS' # O = open, S = single shield, DS = double shield
tbm13.shieldLength=10.2+.95 
tbm13.frontShieldDiameter=6.689
tbm13.frontShieldLength=4.2+.95
tbm13.tailShieldDiameter=6.65
tbm13.excavationDiameter=6.697
tbm13.overcut=0.1
tbm13.loadPerCutter=320.
tbm13.cutterSize=19.*0.0254 #diameter
tbm13.cutterSpacing=0.085
tbm13.cutterThickness=0.02
tbm13.cutterCount=44
tbm13.totalContactThrust=tbm13.loadPerCutter*tbm13.cutterCount
tbm13.referenceRpm=4.2
tbm13.nominalTorque=5880.
tbm13.breakawayTorque=7360.
tbm13.backupDragForce=4000.
tbm13.nominalThrustForce=21500.
tbm13.auxiliaryThrustForce=46180.
tbm13.openingRatio=0.11
tbm13.dotationForProspection=0.
tbm13.cutterheadThickness=0.95 
tbms[tbm13.name] = tbm13

#TBM 14
tbm14=TBMConfig()
tbm14.name = 'CE_S_LOV_6.70'
tbm14.alignmentCode='CE'
tbm14.manifacturer='LOV'
tbm14.type='S' # O = open, S = single shield, DS = double shield
tbm14.shieldLength=9.4+.95
tbm14.frontShieldDiameter=6.676
tbm14.tailShieldDiameter=6.664
tbm14.excavationDiameter=6.684
tbm14.overcut=0.10
tbm14.loadPerCutter=320.
tbm14.cutterSize=19.*0.0254 #diameter
tbm14.cutterSpacing=0.085
tbm14.cutterThickness=0.02
tbm14.cutterCount=44
tbm14.totalContactThrust=tbm14.loadPerCutter*tbm14.cutterCount
tbm14.referenceRpm=4.22
tbm14.nominalTorque=5880.
tbm14.breakawayTorque=7360.
tbm14.backupDragForce=4000.
tbm14.nominalThrustForce=21500.
tbm14.auxiliaryThrustForce=46180.
tbm14.openingRatio=0.11
tbm14.dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata
tbm14.cutterheadThickness=0.95 
tbms[tbm14.name] = tbm14

#TBM 15
tbm15=TBMConfig()
tbm15.name = 'CE_DS_NFM_6.71'
tbm15.alignmentCode='CE'
tbm15.manifacturer='NFM'
tbm15.type='DS' # O = open, S = single shield, DS = double shield
tbm15.shieldLength=12.4 +0.85
tbm15.frontShieldDiameter=6.69
tbm15.frontShieldLength=5.3+.85
tbm15.tailShieldDiameter=6.68
tbm15.excavationDiameter=6.71
tbm15.overcut=0.105
tbm15.loadPerCutter=315.
tbm15.cutterSize=19.*0.0254 #diameter
tbm15.cutterSpacing=0.085
tbm15.cutterThickness=0.02
tbm15.cutterCount=42
tbm15.totalContactThrust=tbm15.loadPerCutter*tbm15.cutterCount
tbm15.referenceRpm=4.
tbm15.nominalTorque=6500.
tbm15.breakawayTorque=9750.
tbm15.backupDragForce=4000.
tbm15.nominalThrustForce=33800.
tbm15.auxiliaryThrustForce=60100.
tbm15.openingRatio=0.075
tbm15.dotationForProspection=0.
tbm15.cutterheadThickness=0.85 
tbms[tbm15.name] = tbm15

#TBM 16
tbm16=TBMConfig()
tbm16.name = 'CE_S_NFM_6.71'
tbm16.alignmentCode='CE'
tbm16.manifacturer='NFM'
tbm16.type='S' # O = open, S = single shield, DS = double shield
tbm16.shieldLength=8.65+.85
tbm16.frontShieldDiameter=6.69
tbm16.tailShieldDiameter=6.68
tbm16.excavationDiameter=6.71
tbm16.overcut=0.105
tbm16.loadPerCutter=315.
tbm16.cutterSize=19.*0.0254 #diameter
tbm16.cutterSpacing=0.085
tbm16.cutterThickness=0.02
tbm16.cutterCount=42
tbm16.totalContactThrust=tbm16.loadPerCutter*tbm16.cutterCount
tbm16.referenceRpm=4.
tbm16.nominalTorque=6500.
tbm16.breakawayTorque=9750.
tbm16.backupDragForce=4000.
tbm16.nominalThrustForce=33800.
tbm16.auxiliaryThrustForce=60100.
tbm16.openingRatio=0.075
tbm16.dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata
tbm16.cutterheadThickness=0.85 
tbms[tbm16.name] = tbm16

#TBM 18
tbm18=TBMConfig()
tbm18.name = 'GL_S_RBS_10.52'
tbm18.alignmentCode='GLSUD;GLNORD'
tbm18.manifacturer='Robbins'
tbm18.type='S' # O = open, S = single shield, DS = double shield
tbm18.shieldLength=9.5 +1.
tbm18.frontShieldDiameter=10.44
tbm18.tailShieldDiameter=10.32
tbm18.excavationDiameter=10.52
tbm18.overcut=0.1
tbm18.loadPerCutter=311.4
tbm18.cutterSize=19.*0.0254 #diameter
tbm18.cutterSpacing=0.0732
tbm18.cutterThickness=0.02
tbm18.cutterCount=72
tbm18.referenceRpm=2.45
tbm18.totalContactThrust=tbm18.loadPerCutter*tbm18.cutterCount
tbm18.nominalTorque=20159.
tbm18.breakawayTorque=39129.
tbm18.backupDragForce=8000.
tbm18.nominalThrustForce=137053.
tbm18.auxiliaryThrustForce=208558
tbm18.openingRatio=0.1
tbm18.cutterheadThickness=1. # in metri lo spessore della testa di scavo
tbm18.dotationForProspection=1. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm18.name] = tbm18

#TBM 19
tbm19=TBMConfig()
tbm19.name = 'GL_DS_LOV_10.50'
tbm19.alignmentCode='GLSUD;GLNORD'
tbm19.manifacturer='LOV'
tbm19.type='DS' # O = open, S = single shield, DS = double shield
tbm19.shieldLength=10.303+1. 
tbm19.frontShieldLength=4.445+1.
tbm19.frontShieldDiameter=10.453
tbm19.tailShieldDiameter=10.441
tbm19.excavationDiameter=10.479
tbm19.overcut=0.1
tbm19.loadPerCutter=320.
tbm19.cutterCount=68
tbm19.cutterSize=19.*0.0254 #diameter
tbm19.cutterSpacing=0.085
tbm19.cutterThickness=0.02
tbm19.totalContactThrust=tbm19.cutterCount*tbm19.loadPerCutter
tbm19.referenceRpm=5.39
tbm19.nominalTorque=6910.
tbm19.breakawayTorque=15900.
tbm19.backupDragForce=8000.
tbm19.nominalThrustForce=61680.
tbm19.auxiliaryThrustForce=77100.
tbm19.openingRatio=0.27
tbm19.cutterheadThickness=1.0 # in metri lo spessore della testa di scavo
tbm19.dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm19.name] = tbm19

#TBM 20
tbm20=TBMConfig()
tbm20.name = 'GL_S_LOV_10.47'
tbm20.alignmentCode='GLSUD;GLNORD'
tbm20.manifacturer='LOV'
tbm20.type='S' # O = open, S = single shield, DS = double shield
tbm20.shieldLength=9.563+1. 
tbm20.frontShieldDiameter=10.453
tbm20.tailShieldDiameter=10.441
tbm20.excavationDiameter=10.466
tbm20.overcut=0.1
tbm20.loadPerCutter=320.
tbm20.cutterSize=19.*0.0254 #diameter
tbm20.cutterSpacing=0.085
tbm20.cutterThickness=0.02
tbm20.cutterCount=68
tbm20.referenceRpm=5.39
tbm20.totalContactThrust=tbm20.loadPerCutter*tbm20.cutterCount
tbm20.nominalTorque=6910.
tbm20.breakawayTorque=15900.
tbm20.backupDragForce=8000.
tbm20.nominalThrustForce=53970.
tbm20.auxiliaryThrustForce=77100
tbm20.openingRatio=0.27
tbm20.cutterheadThickness=1. # in metri lo spessore della testa di scavo
tbm20.dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm20.name] = tbm20

#TBM 21
tbm21=TBMConfig()
tbm21.name = 'GL_DS_NFM_10.52'
tbm21.alignmentCode='GLSUD;GLNORD'
tbm21.manifacturer='NFM'
tbm21.type='DS' # O = open, S = single shield, DS = double shield
tbm21.shieldLength=12.65+1.2 
tbm21.frontShieldLength=5.2+1.2
tbm21.frontShieldDiameter=10.48
tbm21.tailShieldDiameter=10.44
tbm21.excavationDiameter=10.52
tbm21.overcut=0.105
tbm21.loadPerCutter=315.
tbm21.cutterCount=66
tbm21.cutterSize=19.*0.0254 #diameter
tbm21.cutterSpacing=0.09
tbm21.cutterThickness=0.02
tbm21.totalContactThrust=tbm21.cutterCount*tbm21.loadPerCutter
tbm21.referenceRpm=2.5
tbm21.nominalTorque=15000.
tbm21.breakawayTorque=22500.
tbm21.backupDragForce=8000.
tbm21.nominalThrustForce=71400.
tbm21.auxiliaryThrustForce=104200.
tbm21.openingRatio=0.075
tbm21.cutterheadThickness=1.2 # in metri lo spessore della testa di scavo
tbm21.dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm21.name] = tbm21

#TBM 22
tbm22=TBMConfig()
tbm22.name = 'GL_S_NFM_10.47'
tbm22.alignmentCode='GLSUD;GLNORD'
tbm22.manifacturer='NFM'
tbm22.type='S' # O = open, S = single shield, DS = double shield
tbm22.shieldLength=9.1+1.1 
tbm22.frontShieldDiameter=10.48
tbm22.tailShieldDiameter=10.44
tbm22.excavationDiameter=10.52
tbm22.overcut=0.105
tbm22.loadPerCutter=315.
tbm22.cutterSize=19.*0.0254 #diameter
tbm22.cutterSpacing=0.09
tbm22.cutterThickness=0.02
tbm22.cutterCount=66
tbm22.referenceRpm=2.5
tbm22.totalContactThrust=tbm22.loadPerCutter*tbm22.cutterCount
tbm22.nominalTorque=15000.
tbm22.breakawayTorque=22500.
tbm22.backupDragForce=8000.
tbm22.nominalThrustForce=71400.
tbm22.auxiliaryThrustForce=104200.
tbm22.openingRatio=0.075
tbm22.cutterheadThickness=1.1 # in metri lo spessore della testa di scavo
tbm22.dotationForProspection=0. # da 0 a 1 se e' per niente o molto dotata
tbms[tbm22.name] = tbm22

#TBM 23
tbm23=TBMConfig()
tbm23.name = 'CE_DS_RBS_6.73'
tbm23.alignmentCode='CE'
tbm23.manifacturer='Robbins'
tbm23.type='DS' # O = open, S = single shield, DS = double shield
tbm23.shieldLength=11.+1. 
tbm23.frontShieldDiameter=6.67
tbm23.frontShieldLength=4.3+1.
tbm23.tailShieldDiameter=6.56
tbm23.excavationDiameter=6.73
tbm23.overcut=0.12
tbm23.loadPerCutter=311.4
tbm23.cutterSize=19.*0.0254 #diameter
tbm23.cutterSpacing=0.087
tbm23.cutterThickness=0.02
tbm23.cutterCount=42
tbm23.totalContactThrust=tbm23.loadPerCutter*tbm23.cutterCount
tbm23.referenceRpm=5.4
tbm23.nominalTorque=4053.
tbm23.breakawayTorque=14034.
tbm23.backupDragForce=4000.
tbm23.nominalThrustForce=27630.
tbm23.auxiliaryThrustForce=97205.
tbm23.openingRatio=0.1
tbm23.dotationForProspection=1.
tbm23.cutterheadThickness=1. 
tbms[tbm23.name] = tbm23

#TBM 24
tbm24=TBMConfig()
tbm24.name = 'GL_DS_BBT_10.54'
tbm24.alignmentCode='GLSUD;GLNORD'
tbm24.manifacturer='BBT'
tbm24.type='DS' # O = open, S = single shield, DS = double shield
tbm24.shieldLength=11.551+1.05 
tbm24.frontShieldLength=4.791+1.05
tbm24.frontShieldDiameter=10.488
tbm24.tailShieldDiameter=10.41
tbm24.excavationDiameter=10.54
tbm24.overcut=0.101
tbm24.loadPerCutter=250.
tbm24.cutterCount=80
tbm24.cutterSize=17.*0.0254 #diameter
tbm24.cutterSpacing=0.083
tbm24.cutterThickness=0.02
tbm24.totalContactThrust=tbm24.cutterCount*tbm24.loadPerCutter
tbm24.referenceRpm=3.348
tbm24.nominalTorque=9500.
tbm24.breakawayTorque=15900.
tbm24.backupDragForce=8000.
tbm24.nominalThrustForce=61680.
tbm24.auxiliaryThrustForce=77100.
tbm24.openingRatio=0.124
tbm24.cutterheadThickness=1.05 # in metri lo spessore della testa di scavo
tbm24.dotationForProspection=0.5 # da 0 a 1 se e' per niente o molto dotata
tbms[tbm24.name] = tbm24

