import math
from pylab import *
from tbmconfig import *
import numpy as np

def probabilityAftes2012(percent):
    if percent <0.005:
        y0=0.
        slope=1./(.005)
        x=percent
    elif percent<0.02:
        y0=1.
        slope=1./(0.02-.005)
        x=percent-0.005
    elif percent<0.05:
        y0=2.
        slope=1./(0.05-.02)
        x=percent-0.02
    elif percent<0.2:
        y0=3.
        slope=1./(0.2-.05)
        x=percent-0.05
    elif percent<0.5:
        y0=4.
        slope=1./(0.5-.2)
        x=percent-0.2
    else:
        y0=5.
        slope=1./(2.-0.5)
        x=percent-0.5
    return y0+slope*x

def impactOnDelay(tDays):
    days=max(0., tDays)
    if days==0.:
        y0=0.
        slope=0.
        x=0
    elif days<7.:
        y0=1.
        slope=1./7.
        x=days
    elif days<30.:
        y0=2.
        slope=1./(30.-7.)
        x=days-7.
    elif days<90.:
        y0=3.
        slope=1./(90.-30.)
        x=days-30.
    elif days<270.:
        y0=4.
        slope=1./(270.-90.)
        x=days-90.
    else:
        y0=5.
        slope=0
        x=0.
    impact=y0+slope*x
    return impact

def impactOnCost(cost, costRef):
    if costRef<.0000000001:
        print 'Error: reference cost is almost zero'
        exit(-1)
    ratio = cost/costRef
    if ratio<=0.:
        y0=1.
        slope=0.
        x=ratio
    elif ratio>0. and ratio <=.05:
        y0=1.
        slope=1./(.05)
        x=ratio
    elif ratio>.05 and ratio <=.1:
        y0=2.
        slope=1./(.1-.05)
        x=ratio-.05
    elif ratio>.1 and ratio <=.5:
        y0=3.
        slope=1./(.5-.1)
        x=ratio-.1
    else:
        y0=4
        slope=0.
        x=0.
    impact=y0+slope*x
    return impact

def impactOnProduction(production, productionRef):
    if productionRef<.0000000001:
        print 'Error: reference production is zero'
        exit(-1)
    ratio = production/productionRef
    if ratio>=1.:
        y0=0.
        slope=0.
        x=ratio
    elif ratio<1. and ratio >=.5:
        y0=2.
        slope=-1./(1.-.5)
        x=ratio-.5
    elif ratio<.5 and ratio >=.1:
        y0=3.
        slope=-1./(.5-.1)
        x=ratio-.1
    elif ratio<.1 and ratio >=.05:
        y0=4.
        slope=-1./(.1-.05)
        x=ratio-.05
    else:
        y0=4
        slope=0.
        x=0.
    impact=y0+slope*x
    return impact


#obsoleta
def impactOfProductionDaysAftes2012(days):
    #devo pesare il tempo rispetto a un riferimento
    if days<7.:
        y0=1.
        slope=0.
        x=days
    elif days<30.:
        y0=1.
        slope=1./(30.-7.)
        x=days-7.
    elif days<90.:
        y0=2.
        slope=1./(90.-30.)
        x=days-30.
    elif days<270.:
        y0=3.
        slope=1./(270.-90.)
        x=days-90.
    elif days<810.:
        y0=4.
        slope=1./(810.-270.)
        x=days-270.
    elif days<2430.:
        y0=5.
        slope=1./(2430.-810.)
        x=days-810.
    return y0+slope*x


def tempoInterventiSpeciali(tbmType, length): #obsoleta
    #restituisce tempo in ore
    t = 0.
    if tbmType=='O':
        #3 ore per campo di 6 metri
        t = length/6.*3.
    elif tbmType=='S':
        #4 ore per campo di 6 metri
        t = length/6.*4.
    elif tbmType=='DS':
        #3 ore per campo di 6 metri
        t = length/6.*3.
    else:
        print "Errore! Tipo TBM inesistente!"
        exit(-1)
    return t


def derivative(f, x, nu, a, so, h):
    res = (f(x+h, nu, a, so) - f(x-h, nu, a, so)) / (2.0*h)
    if res ==0:
        res = 0.00001
    return res  # might want to return a small non-zero if ==0

def pcrit(x, nu, a, so):
    return nu*x**a+2.*x-2.*so     # just a function to show it works

def U(rho, u, uP, c1, c2):
    return c1/rho*uP-c1/(rho**2)*u+c2

def solve(f, x0, nu, a, so, h):
    lastX = x0
    nextX = lastX + 10* h  # "different than lastX so loop starts OK
    while (abs(lastX - nextX) > h):  # this is how you terminate the loop - note use of abs()
        newY = f(nextX, nu, a, so)                     # just for debug... see what happens
        lastX = nextX
        nextX = max(lastX - newY / derivative(f, lastX, nu, a, so, h), 2.*h)  # update estimate using N-R, lo limito a rimanere oltre lo zero
    return nextX

class Rock:
    # definisce le caratteristiche della roccia intatta
    def __init__(self, gamma, ni, e, ucs,  st):
        self.Gamma = gamma
        self.Ni = ni
        self.E = e
        self.Ucs = ucs
        if st>=0.:
            self.Sigmat = st #tensile strength
        else:
            self.Sigmat = ucs/12. # approssimazione qualora non siano note le caratteristiche
        self.Lambda = e*ni/((1.0+ni)*(1.0-2.0*ni))
        self.G = e/(2.*(1.+ni))

class InSituCondition:
# caratteristiche dell'ammasso e stato tensionale locale
    def __init__(self, overburden, h_2, groundwaterdepth, gamma, k0min, k0max, gsi, rmr):
        self.Overburden = overburden #copertura netta
        self.Groundwaterdepth = groundwaterdepth #copertura netta
        self.K0 = 1.0
        self.K0min = k0min
        self.K0max = k0max
        self.Kp = 1.0
        self.Ka = 1.0 # posso definire RMR o GSI

        if gsi > 0.0:
            self.Gsi = max(5., gsi)
        else:
            self.Gsi = max(5., rmr - 5.0)

        if rmr > 0.0:
            self.Rmr = max(5., rmr)
        else:
            self.Rmr = max(5., gsi+5)
        self.SigmaV = gamma*(overburden+h_2)/1000.0 # MPa

    def UpdateK0KaKp(self, typ, fi):
        self.Kp = (1.0 + math.sin(math.radians(fi)))/(1.0 - math.sin(math.radians(fi)))
        self.Ka = 1.0 / self.Kp
        if typ == 'd':
            self.K0 = (self.K0min+self.K0max)/2.0
        else:
            self.K0 = self.Ka*(1.0+math.sin(math.radians(fi)))

class HoekBrown:	#caratteristiche ammasso secondo Hoek e Brown
    def __init__(self, gamma, ucs, mi, e, gsi, d, sv):
        self.gsi = max(5., gsi)
        self.Mi = mi
        self.D = d
        self.Mb = mi*math.exp((gsi-100.0)/(28.0-14.0*d)) # parametro di Hoek & Brown
        self.S = math.exp((gsi-100.0)/(9.0-3.0*d))	# parametro di Hoek & Brown
        self.A = 0.5+(1.0/6.0)*((math.exp(-gsi/15.0))-(math.exp(-20.0/3.0)))	# parametro di Hoek & Brown
        self.SigmaC = ucs*self.S**self.A	# parametro di Hoek & Brown
        self.SigmaT = self.S*ucs/self.Mb # a meno del segno e' la resistenza a trazione
        self.SigmaCm = ucs*(((self.Mb+4.0*self.S-self.A*(self.Mb-8.0*self.S))*(self.Mb/4.0+self.S)**(self.A-1.0))/(2.0*(1.0+self.A)*(2.0+self.A)))	# parametro di Hoek & Brown
        if sv < 0.001 or self.SigmaCm < 0.001:
            print "ucs= %f mi= %f mb= %f s= %f a= %f SigmaCm= %f SigmaV= %f" %(ucs, mi, self.Mb, self.S, self.A, self.SigmaCm, sv)
            exit(-701)
        self.Sigma3max = (0.47*(self.SigmaCm/sv)**(-0.94))*self.SigmaCm # parametro di Hoek & Brown

        # parametri residui
        dr = d # TODO mettere legge
        ucsr = ucs # TODO mettere legge
        gsir = max(5., gsi*math.exp(-.0134*gsi))
        self.dr = dr
        self.ucsr = ucsr
        self.gsir = gsir
        self.Mr = mi*math.exp((gsir-100.0)/(28.0-14.0*dr)) # parametro di Hoek & Brown
        self.Sr = math.exp((gsir-100.0)/(9.0-3.0*dr))	# parametro di Hoek & Brown
        self.Ar = 0.5+(1.0/6.0)*((math.exp(-gsir/15.0))-(math.exp(-20.0/3.0)))	# parametro di Hoek & Brown
        self.SigmaCr = ucsr*self.Sr**self.Ar	# parametro di Hoek & Brown
        self.SigmaTr = self.Sr*ucsr/self.Mr # a meno del segno e' la resistenza a trazione
        self.SigmaCmr = ucsr*(((self.Mr+4.0*self.Sr-self.Ar*(self.Mr-8.0*self.Sr))*(self.Mr/4.0+self.Sr)**(self.Ar-1.0))/(2.0*(1.0+self.Ar)*(2.0+self.Ar)))	# parametro di Hoek & Brown
        self.Sigma3maxr = (0.47*(self.SigmaCmr/sv)**(-0.94))*self.SigmaCmr # parametro di Hoek & Brown

class MohrCoulomb:
    def __init__(self):
        self.Fi =0.
        self.Fir = 0.
        self.C = 0. #in KPa
        self.Cr = 0. #in KPa
        self.SigmaCm0 = 0.

    # inizializzazione per rocce
    def SetRock(self, hb, ucs):
        self.Fi = math.degrees(math.asin((6.0*hb.A*hb.Mb*(hb.S+hb.Mb*hb.Sigma3max/ucs)**(hb.A-1.0))\
                /(2.0*(1.0+hb.A)*(2.0+hb.A)+(6.0*hb.A*hb.Mb*(hb.S+hb.Mb*hb.Sigma3max/ucs)**(hb.A-1.0)))))
        self.C = (ucs*((1.0+2.0*hb.A)*hb.S+(1.0-hb.A)*hb.Mb*(hb.Sigma3max/ucs))*(hb.S+hb.Mb*(hb.Sigma3max/ucs))**(hb.A-1.0)) \
        		/((1.0+hb.A)*(2.0+hb.A)*math.sqrt(1.0+(6.0*hb.A*hb.Mb*(hb.S+hb.Mb*(hb.Sigma3max/ucs))**(hb.A-1.0))/((1.0+hb.A)*(2.0+hb.A))))*1000.0 #in KPa
        self.SigmaCm0 = 2.0*self.C*math.cos(math.radians(self.Fi))/(1.0-math.sin(math.radians(self.Fi)))/1000.

        # parametri residui
        self.Fir = math.degrees(math.asin((6.*hb.Ar*hb.Mr*(hb.Sr+hb.Mr*hb.Sigma3maxr/ucs)**(hb.Ar-1.))\
        		/(2.*(1.+hb.Ar)*(2.+hb.Ar)+(6.*hb.Ar*hb.Mr*(hb.Sr+hb.Mr*hb.Sigma3maxr/ucs)**(hb.Ar-1.)))))
        self.Cr = (ucs*((1.+2.*hb.Ar)*hb.Sr+(1.-hb.Ar)*hb.Mr*(hb.Sigma3maxr/ucs))*(hb.Sr+hb.Mr*(hb.Sigma3maxr/ucs))**(hb.Ar-1.)) \
        		/((1.+hb.Ar)*(2.0+hb.Ar)*math.sqrt(1.+(6.*hb.Ar*hb.Mr*(hb.Sr+hb.Mr*(hb.Sigma3maxr/ucs))**(hb.Ar-1.))/((1.+hb.Ar)*(2.+hb.Ar))))*1000.0 #in KPa
        self.SigmaCm0r = 2.0*self.Cr*math.cos(math.radians(self.Fir))/(1.0-math.sin(math.radians(self.Fir)))/1000.0

        self.psi = (self.Fi-self.Fir)/1.5

    #inizializzazione per terreni
    def SetSoil(self, fi, c, fir):
        self.Fi = fi
        self.C = c
        self.Fir = fir
        self.SigmaCm0 = 2.0*c*math.cos(math.radians(fi))/(1.0-math.sin(math.radians(fi)))/1000.0

class Excavation:
    # caratteristiche legate allo scavo
    def __init__(self, typ, area, width, height, length, overburden, fi):
        # serve passare i valori di post picco di fi
        self.Type = typ 						#Mech
        self.Area = area						#Area della sezione di scavo
        self.Width = width						#ampiezza dello sezione di scavo
        self.Height = height					#altezza della sezione di scavo
        self.Length = length					#lunghezza di riferimento per il segmento di scavo (per il calcolo della convergenza in quel punto)
        self.Radius = math.sqrt(area/math.pi)	#raggio di scavo equivalente (se policentrica riconduce la sezione di scavo circolare)
        if abs(self.Height-2.*self.Radius)<0.01:
            # sono nel caso di scavo meccanizzato allora usiamo meta' altezza per il silo
            self.B1 = width+2.0*self.Radius*math.tan(math.radians(45.0-fi/2.0)) # Terzaghi silo width
        else:
            self.B1 = width+2.0*height*math.tan(math.radians(45.0-fi/2.0)) # Terzaghi silo width

        #overburdenType: s = shallow, d = deep
        if typ == 'Mech':
            if overburden < 2.5*2.0*self.Radius:
                self.OverburdenType = 's'
            else:
                self.OverburdenType = 'd'
        else:
            if overburden < 2.5*self.B1:
                self.OverburdenType = 's'
            else:
                self.OverburdenType = 'd'

class rockBursting:
    # rockbursting secondo Hoek
    def __init__(self, ucs, rmr, p0):
        if ucs > 105.0 and rmr > 60:
            self.Val = p0/ucs
        else:
            self.Val = 0.0
        if self.Val <= 0.1:
            self.Class = 'Stable behaviour'
        elif self.Val <= 0.2:
            self.Class = 'Spalling'
        elif self.Val <= 0.3:
            self.Class = 'Severe spalling - slabbing'
        elif self.Val < 0.4:
            self.Class = 'Need of important stabilization measure'
        else:
            self.Class = 'Cavity collapse (rock burst)'

class frontStability:
    # stabilita' del fronte secondo Panet (Ns e Lambdae)
    def __init__(self, ratio,  sigmaCm, p0, kp):

        if ratio < 2.5:
            # criterio non applicabile per basse coperture ratio = copertura/diametro di scavo equivalente
            self.Ns = 0
            self.State = 'Not applicable'
            self.lambdae = 1.5
            self.Class = 'Not applicable'


        self.Ns = 2.0*p0/sigmaCm
        if self.Ns <1:
            self.State = 'Elastic'
        elif self.Ns <2:
            self.State = 'Plastic zone not interesting tunnel face'
        elif self.Ns <5:
            self.State = 'Plastic zone partially interesting tunnel face'
        else:
            self.State = 'Plastic zone entirely interesting tunnel face'

        if self.Ns >1:
            self.lambdae = (kp-1.0+2.0/self.Ns)/(kp+1.0)
        else:
            self.lambdae = 0.0

        if self.lambdae > 0.6:
            self.Class = 'Stability'
        elif self.lambdae > 0.3:
            self.Class = 'Short term stability'
        else:
            self.Class = 'Instability'

class Breakaway:
    def __init__(self):
        self.D=0.
        self.fir =0.
        self.si = 0.
        self.T1 = 0.
        self.T2 = 0.
        self.T3 = 0.
        self.T5 = 0.
        self.torque = 0.
    
    def setupFrontInstability(self, overburden, mc, gamma, D):
        # nu e' opening Ratio della cutterhead
        # definisco tutto sulla base dei parametri di post picco del materiale
        self.D = D
        self.fir = mc.Fir
        f = min(mc.SigmaCm0r * 1000.0 / 100.0, mc.Cr/(mc.SigmaCm0r*1000.0)+math.tan(math.radians(mc.Fir))) #fattore di Protodyakonov
        b1 = D+D*math.tan(math.radians(45.0-mc.Fir/2.0)) # Terzaghi silo width
        h1 = min(max(1.7*D, b1/2.0/f), overburden)
        self.si = gamma*(h1+D/2.) # in KPa

    def setupRockburst(self, mc, gamma, D):
        # definisco tutto sulla base dei parametri di post picco del materiale
        self.D = D
        self.fir = mc.Fir
        self.si = gamma*D/2. # in KPa

    #definisco l'altezza di materiale di frana secondo tamez per terreni
    def calculate(self, nu, t, fiRi):
        # nu e' opening Ratio della cutterhead
        si = self.si
        D = self.D
#        D = excav.Radius*2.
#        fiRi = 0.5 # fattore di riduzione dell'attrito per valutare il coefficiente di attrito dei vari casi
        u1 = math.tan(fiRi*math.radians(self.fir)) # coefficiente di attrito del materiale al fronte
        u2 = u1 # coefficiente di attrito del materiale su bordo della testa di scavo
        u3 = u1
        u5 = u1
        # Varie componenti del torque in kNm
        self.T1 = math.pi*D**3/12.*si*u1*(1-nu)
        self.T2 = math.pi*D**2/2.*si*u2*t
        self.T3 = math.pi*D**3/12.*si*u3*(1-nu)
        self.T5 = math.pi*D**3/12.*0.35*si*u5*nu
        self.torque = self.T1+self.T2+self.T3+self.T5

class Tamez:
	# stabilita' del fronte secondo Tamez
	def __init__(self, materialtype, overburden, excav, mc, insitu, gamma, pi, aunsupported):
		self.L = excav.Height*math.tan(math.radians(45.0-mc.Fi/2.0))
		if materialtype =='r': # r per rock, s per soil
			self.F = mc.SigmaCm0 * 1000.0 / 100.0 #fattore di Protodyakonov
		else: # caso di materiale sciolto
			self.F = mc.C/(mc.SigmaCm0*1000.0)+math.tan(math.radians(mc.Fi))
		if excav.OverburdenType =='d':
			self.H1 = min(1.7*excav.Width, overburden)
			self.Taum2 = mc.C+insitu.K0/2.0*(insitu.Groundwaterdepth*gamma+(insitu.Overburden-self.H1-insitu.Groundwaterdepth)*(gamma-10)\
						+3.4*mc.C/math.sqrt(insitu.Ka)-(gamma-10)*excav.Height/2.0)# taum2 in KPa
			self.Taum3 = mc.C+(0.25*(insitu.Groundwaterdepth*gamma+(insitu.Overburden-self.H1-insitu.Groundwaterdepth)*(gamma-10.0))\
						-10.0*(insitu.Overburden-insitu.Groundwaterdepth))*math.tan(math.radians(mc.Fi))
		else:
			self.H1 = min(excav.B1/2.0/self.F, overburden)
			self.Taum2 = mc.C+insitu.K0/2*(3.4*mc.C/math.sqrt(insitu.Ka)-(gamma-10.0)*excav.Height/2.0)
			self.Taum3 = mc.C
		self.FSgeneral = ((2*(self.Taum2-self.Taum3)/(1+aunsupported/self.L)**2+2*self.Taum3)*self.H1/excav.Width+2*self.Taum3/\
						(1+aunsupported/self.L)/math.sqrt(insitu.Ka)*self.H1/excav.Height+3.4*mc.C/(1+aunsupported/self.L)**2/\
						math.sqrt(insitu.Ka))/((1+2*excav.Height/(3*insitu.Overburden*(1+aunsupported/self.L)**2))*\
						(insitu.Groundwaterdepth*gamma+(insitu.Overburden-insitu.Groundwaterdepth)*(gamma-10.0)-pi))
		self.FS3 = 2*self.Taum3/(insitu.Groundwaterdepth*gamma+(insitu.Overburden-insitu.Groundwaterdepth)*(gamma-10)-pi)*self.H1/excav.Width*(1+excav.Width/aunsupported)
		self.FSmin = min(self.FSgeneral, self.FS3)
		if self.FSmin < 1.3:
			self.Class = 'C - instability'
		elif self.FSmin <1.5:
			self.Class = 'B - short-term stability (critical settlements)'
		elif self.FSmin <2.0:
			self.Class = 'B - short-term stability (admissible settlements)'
		else:
			self.Class = 'A - stability'

class TBM:
    def __init__(self, tbmData, LDP_type):
        self.type = tbmData.type # tipo tbm: O, S, DS
        self.rpm = tbmData.referenceRpm
        self.Slen = tbmData.shieldLength # shield length
        self.excavationDiam = tbmData.excavationDiameter    #shield maximum diameter
        self.frontShieldDiameter = tbmData.frontShieldDiameter
        self.tailShieldDiameter = tbmData.tailShieldDiameter
        
        self.dotation = tbmData.dotationForProspection #numero tra 0 e 1 dove 0 e' la meno dotata
        self.name = tbmData.name

        self.gap = tbmData.overcut + (self.excavationDiam-tbmData.tailShieldDiameter)/2. #gap in m
        self.gap1 = tbmData.overcut + (self.excavationDiam-tbmData.frontShieldDiameter)/2. #gap in m del primo scudo (per le DS)
        self.CutterNo = tbmData.cutterCount # numebr of cutters
        self.CutterRadius = tbmData.cutterSize/2.  #Cutter radius
        self.CutterThickness = tbmData.cutterThickness #Cutterthickness
        self.CutterSpacing = tbmData.cutterSpacing #Cutter spacing
#        self.Friction = tbmData.frictionCoefficient # coefficiente di attrito tra ammasso e scudo
        self.BackupDragForce = tbmData.backupDragForce # kN (8000 per la GL, 4000 per il CE
        self.openingRatio = tbmData.openingRatio
        self.cutterheadThickness = tbmData.cutterheadThickness
        self.Slen1 =tbmData.frontShieldLength

        # penetration rate per ogni decina di rmr: 0, 10, 20, 30.....100
        self.rop= array((1.2904525, 1.2904525,1.540995,1.7915375,1.97058,2.1246225,2.187465,2.2253075,1.97355,1.7217925, 1.7217925)) # m/h metri di scavo all'ora
        self.penetrationPerRevolution = self.rop/60./self.rpm  #in m per rivoluzione
        # definisco l'Utilization Factor
        uf0=array((0.110166666666667, 0.110166666666667,0.159111111111111,0.208055555555556,0.288194444444445,0.368333333333333,0.4335, \
                    0.498666666666667, 0.498666666666667,0.498666666666667,0.498666666666667))
        ufS=array((0.154166666666667,0.154166666666667,0.189583333333333,0.225,0.285416666666667,0.345833333333333, \
                    0.377083333333333,0.408333333333333,0.408333333333333,0.408333333333333,0.408333333333333))
        ufDS=array((0.15,0.15,0.219166666666667,0.288333333333333,0.354722222222222,0.421111111111111,0.442361111111111, \
                    0.463611111111111,0.463611111111111,0.463611111111111,0.463611111111111))
        if self.type == 'O': # per ogni decina di rmr: 0, 10, 20, 30.....100
            self.uf = uf0
        elif self.type =='S':
            self.uf = ufS
        elif self.type == 'DS':
            self.uf = ufDS
        else:
            print 'Errore: tipo TBM inesistente. Impossibile definire UF'
            exit(-700)
        # definisco la massima produzione giornaliera in metri possibile (serve per dare un peso alla produzione)
        productionMax = 0.
        for iii in range(0, 10):
            irop = self.rop[iii]
            iuf = max(uf0[iii], ufS[iii], ufDS[iii])
            productionMax = max(productionMax, 24.*irop*iuf)
        self.maxProduction = productionMax
        # angolo da definire in base alla macchina
        # come suggerito da Rostami et Al. lo faccio variare linearmente da -0.2 a 0.2 in modo inversamente proporzionale allo spessore del cutter
        tInf = 0.013 # 13 mm
        tSup = 0.024 # 24 mm
        self.psi = 0.2 - 0.4 * (self.CutterThickness-tInf) / (tSup-tInf) # angolo da definire in base alla macchina
        self.Ft = tbmData.loadPerCutter # kN max load per cutter ring
        self.totalContactThrust = tbmData.totalContactThrust
        self.installedThrustForce = tbmData.nominalThrustForce #in kN
        self.installedAuxiliaryThrustForce = tbmData.auxiliaryThrustForce #in kN
        self.nominalTorque = tbmData.nominalTorque #in kNm
        self.breakawayTorque = tbmData.breakawayTorque #in kNm
        self.LDP_type = LDP_type # tipo di formulazione per convergenza del cavo: P = Panet, V = Vlachopoulos-Dietrich

        # a questo livello possosolo inizializzare P2 (tempi di montaggio e smontaggio) e P6 (posa rivestimento) perche' potro' valutare il suo impatto
        # pesandolo sulla tempo minimo di produzine che ho a livello di main
        self.P2 = P2(self.type)
        self.P6 = P6()

        self.V1 = V1(self.type)
        self.V2 = V2(self.type, self.name)
        self.V3 = V3(self.type, self.dotation)
        self.V4 = V4(self.type)
        self.V5 = V5(self.type)
        self.V6 = V6(self.type)

class TBMSegment:
    # definisco la condizione intrinseca (TODO verificare definizione con Luca o Paolo)
    def __init__(self, segment, tbm, fiRi, frictionCoeff): # gabriele@20151114 friction parametrica
        gamma = segment.gamma
        ni = .2
        e = segment.ei*1000.
        ucs = segment.sci
        st = segment.sti
        mi = segment.mi
        overburden = segment.co
        groundwaterdepth = segment.co
        k0min = segment.k0_min
        k0max = segment.k0_max
        gsi = segment.gsi
        rmr = segment.rmr
        self.segmentLength = segment.length
        excavArea = (tbm.excavationDiam**2)*math.pi/4.
        excavWidth = tbm.excavationDiam
        excavHeight = tbm.excavationDiam
        refLength = tbm.Slen
        aunsupported = tbm.Slen
        excavType = 'Mech'
        pi = 0.
        if ucs <= 1.0:
            print "gamma= %f E= %f ucs= %f" % (gamma, e, ucs)
        self.Rock = Rock(gamma, ni, e, ucs,  st)	#importo definizione di Rock
        self.InSituCondition = InSituCondition(overburden, excavHeight/2., groundwaterdepth, gamma, k0min, k0max, gsi, rmr)	#importo defizione di stato in situ
        if excavType == 'Mech':
            self.D = 0.0
        else:
            self.D = 0.2
        self.HoekBrown = HoekBrown(gamma, ucs, mi, e, self.InSituCondition.Gsi, self.D, self.InSituCondition.SigmaV)
        self.MohrCoulomb = MohrCoulomb()
        self.MohrCoulomb.SetRock(self.HoekBrown, ucs)

        # print "GSI= %f GSIr= %f " % (self.HoekBrown.gsi, self.HoekBrown.gsir)

        self.Excavation = Excavation(excavType, excavArea, excavWidth, excavHeight, refLength, overburden, self.MohrCoulomb.Fir)
        self.InSituCondition.UpdateK0KaKp(self.Excavation.OverburdenType,self.MohrCoulomb.Fi)
        self.rockBurst = rockBursting(ucs, rmr, self.InSituCondition.SigmaV)
        self.Tamez = Tamez('r',overburden, self.Excavation, self.MohrCoulomb, self.InSituCondition, gamma, pi, aunsupported)
        self.frontStability = frontStability(self.InSituCondition.Overburden/(2.0*self.Excavation.Radius), \
                                    self.MohrCoulomb.SigmaCm0, self.InSituCondition.SigmaV, self.InSituCondition.Kp) #, 1.0+math.sin(math.radians(self.MohrCoulomb.Fi)))
        # definisco il breakawayTorque per l'instabilita' del fronte
        bat = Breakaway()
        if self.frontStability.lambdae > 0.6:
            self.frontStabilityBreakawayTorque = 0.
        elif self.frontStability.lambdae > 0.3:
            # tra 0.3 e 0.6 ipotizzo che aumenti progressivamente il diametro di base
            dEq = self.Excavation.Radius*2.*(0.6-self.frontStability.lambdae)/.3 
            bat.setupFrontInstability(overburden, self.MohrCoulomb, gamma, dEq)
            bat.calculate(tbm.openingRatio, tbm.cutterheadThickness, fiRi)
#            print 'Breakaway torque for front stability mid = %f' % (bat.torque)
        else:
            dEq=self.Excavation.Radius*2.
            bat.setupFrontInstability(overburden, self.MohrCoulomb, gamma, dEq)
            bat.calculate(tbm.openingRatio, tbm.cutterheadThickness, fiRi)
#            print 'Breakaway torque for front stability full = %f' % (bat.torque)
        self.frontStabilityBreakawayTorque = bat.torque

        # definisco il breakawayTorque per il rockburst
        bat = Breakaway()
        if self.rockBurst.Val < .2:
            self.rockburstBreakawayTorque = 0.
        elif self.rockBurst.Val < .3:
            # tra 0.3 e 0.6 ipotizzo che aumenti progressivamente il diametro di base
            dEq = self.Excavation.Radius*2.*(self.rockBurst.Val-0.2)/.1 
            bat.setupRockburst(self.MohrCoulomb, gamma, dEq)
            bat.calculate(tbm.openingRatio, tbm.cutterheadThickness, fiRi)
#            print 'Breakaway torque for rockbursting mid = %f' % (bat.torque)
        else:
            dEq=self.Excavation.Radius*2.
            bat.setupRockburst(self.MohrCoulomb, gamma, dEq)
            bat.calculate(tbm.openingRatio, tbm.cutterheadThickness, fiRi)
#            print 'Breakaway torque for rockbursting full = %f' % (bat.torque)
        self.rockburstBreakawayTorque = bat.torque
        # definisco il breakawayTorque come il massimo tra quello richiesto per instabilita' del fronte e quello richesto dal rockbursting
        self.breakawayTorque = max(self.frontStabilityBreakawayTorque, self.rockburstBreakawayTorque)

        #gabriele@20151114 info fuorviante
#        R = self.Excavation.Radius # in m
#        ni = self.Rock.Ni
#        fi = math.radians(self.MohrCoulomb.Fi)
#        c = self.MohrCoulomb.C / 1000. # MPa
#        fir = math.radians(self.MohrCoulomb.Fir)
#        cr = self.MohrCoulomb.C / 1000. # MPa
#        pi_cr_tan = cr / math.tan(fir)
#        p0 = self.Rock.Gamma * (self.InSituCondition.Overburden+self.Excavation.Height/2.0) / 1000.0 # in MPa
#        self.P_0 = p0
#        self.Pcr = p0 * (1.-math.sin(fi)) - c * math.cos(fi) # in MPa
#        self.Pocp = p0 + c / math.tan(fi)
#        self.Pocr = p0 + cr / math.tan(fir)
#        self.Nfir = (1.+math.sin(fir)) / (1.-math.sin(fir))
#        if self.Pcr < p0:
#            self.Rpl = (((self.Pocr-self.Pocp*math.sin(fir))/pi_cr_tan)**(1.0/(self.Nfir-1.)))*R
#        else:
#            self.Rpl = R

        self.Tbm = tbm

        self.TunnelClosureAtShieldEnd = self.TunnelClosure(self.Tbm.Slen) # min(self.TunnelClosure(self.Tbm.Slen, 'P'),  R)
        if self.Tbm.type =='DS':
            self.TunnelClosureAtShieldEnd1 = self.TunnelClosure(self.Tbm.Slen1) # delta convergenza alla fine del primo scudo
        else:
            self.TunnelClosureAtShieldEnd1 = 0.

        # definisco la possibile convergenza sullo scudo
        # contactType = 0 significa nessun contatto
        # contactType = 1 significa conatto solo sullo scudo posteriore
        # contactType = 2 significa contatto solo sullo scudo anteriore
        # contactType = 3 significa contatto su entrambe gli scudi
        if self.TunnelClosureAtShieldEnd<=self.Tbm.gap and self.TunnelClosureAtShieldEnd1<=self.Tbm.gap1:
            self.contactType = 0
            self.frontFrictionForce = 0.
            self.tailFrictionForce = 0.
            self.frictionForce = 0.0 # in kN quella che mi rallenta l'avanzamento
            self.Xcontact = tbm.Slen
        elif self.TunnelClosureAtShieldEnd>self.Tbm.gap and self.TunnelClosureAtShieldEnd1<=self.Tbm.gap1:
            self.Xcontact = self.xLim(self.Tbm.gap)
            # integrazione semplificata, assumo la pressione come triangolare
            maxPressure = self.PiUr(self.Tbm.gap) - self.PiUr(self.TunnelClosureAtShieldEnd)
            total = maxPressure*(self.Tbm.Slen-self.Xcontact)/2.0
            if self.Tbm.type =='DS':
                self.contactType = 1
                self.frontFrictionForce = 0.
                self.tailFrictionForce = total*self.Tbm.tailShieldDiameter*math.pi*frictionCoeff*1000.0 # forza in kN
                self.frictionForce = 0.
            else:
                self.contactType = 2
                self.frontFrictionForce = total*self.Tbm.tailShieldDiameter*math.pi*frictionCoeff*1000.0 # forza in kN
                self.tailFrictionForce = 0.
                self.frictionForce = self.frontFrictionForce
                
        elif self.TunnelClosureAtShieldEnd<=self.Tbm.gap and self.TunnelClosureAtShieldEnd1>self.Tbm.gap1:
            self.contactType = 2
            self.Xcontact = self.xLim(self.Tbm.gap1)
            # integrazione semplificata, assumo la pressione come triangolare
            maxPressure = self.PiUr(self.Tbm.gap1) - self.PiUr(self.TunnelClosureAtShieldEnd1)
            total = maxPressure*(self.Tbm.Slen1-self.Xcontact)/2.0
            self.frontFrictionForce = total*self.Tbm.frontShieldDiameter*math.pi*frictionCoeff*1000.0 # forza in kN
            self.tailFrictionForce = 0.
            self.frictionForce = self.frontFrictionForce
        else:
            self.contactType = 3
            # ipotizzo distribuzione triangolare su tutto lo scudo di dietro e calcolo normalmente quella dello scudo davanti
            self.Xcontact = self.xLim(self.Tbm.gap1)
            # forza su scudo anteriore
            maxPressure = self.PiUr(self.Tbm.gap1) - self.PiUr(self.TunnelClosureAtShieldEnd1)
            total = maxPressure*(self.Tbm.Slen1-self.Xcontact)/2.0
            self.frontFrictionForce = total*self.Tbm.frontShieldDiameter*math.pi*frictionCoeff*1000.0 # forza in kN
            #forza su scudo posteriore
            maxPressure = self.PiUr(self.Tbm.gap) - self.PiUr(self.TunnelClosureAtShieldEnd)
            total = maxPressure*(self.Tbm.Slen-self.Tbm.Slen1)/2.0
            self.tailFrictionForce = total*self.Tbm.tailShieldDiameter*math.pi*frictionCoeff*1000.0 # forza in kN
            self.frictionForce = self.frontFrictionForce

        #definisco il thrust che rimane per l'avanzamento tolti gli attriti e la convergenza sullo scudo
        if tbm.type == 'DS':
            self.availableThrust = max(0., self.Tbm.installedThrustForce - self.frictionForce)
        else:
            self.availableThrust = max(0., self.Tbm.installedThrustForce - self.frictionForce - self.Tbm.BackupDragForce)

        #se non mi rimane thurst devo consolidare o sbloccare la macchina
        ratio = self.availableThrust/self.Tbm.totalContactThrust
        if ratio > .25:
            self.cavityStabilityPar = 0.
        elif ratio > 0.:
            self.cavityStabilityPar = (0.25-ratio)*4. # varia da 0 a 1 passando da ratio = 0.25 a 0
        else:
            self.cavityStabilityPar = 1.
        #considerao anche il blocco dello scudo posteriore
        if self.Tbm.installedAuxiliaryThrustForce>self.tailFrictionForce:
            self.tailCavityStabilityPar = 0.
        else:
            self.tailCavityStabilityPar = 1.

        # definisco thrust e torque
        psi = self.Tbm.psi
        ucs = self.Rock.Ucs
        sigmat = self.Rock.Sigmat
        RMR = self.InSituCondition.Rmr
        rate = self.Tbm.penetrationPerRevolution
        uf = self.Tbm.uf

        i_1 = int(math.floor(RMR/10.0))
        i = i_1+1
        locpBase = rate[i_1]+(rate[i]-rate[i-1])/10.0*(RMR-i_1*10)
        locuf = uf[i_1]+(uf[i]-uf[i-1])/10.0*(RMR-i_1*10)
        locfi = math.acos((self.Tbm.CutterRadius-locpBase)/self.Tbm.CutterRadius)
        locP0 = 2.12*math.pow((self.Tbm.CutterSpacing*(ucs**2)*sigmat/(locfi*math.sqrt(self.Tbm.CutterRadius*self.Tbm.CutterThickness))), 1.0/3.0)
        locFt = 1000.0*locP0*locfi*self.Tbm.CutterRadius*self.Tbm.CutterThickness/(1.0+psi) # in kN
        pRateReduction = 0.0
        if self.cavityStabilityPar == 0:
            ftAvailable = min(self.Tbm.Ft,  self.availableThrust/self.Tbm.CutterNo)
        else:
            ftAvailable = self.Tbm.Ft
        if locFt > ftAvailable:
            locFt = ftAvailable
            locfi=locFt*(1.0+psi)/(1000.0*locP0*self.Tbm.CutterRadius*self.Tbm.CutterThickness)
            pRid = self.Tbm.CutterRadius*(1.-math.cos(locfi))
            pRateReduction = max(0., locpBase-pRid)
            locp = pRid
        else:
            locp = locpBase

        locFn = locFt*math.cos(locfi/2.0) # in kN
        locFr = locFt*math.sin(locfi/2.0) # in kN
        self.penetrationRate = locp # m / rotazione
        self.penetrationRateReduction = pRateReduction
        self.contactThrust = self.Tbm.CutterNo*locFn # in kN
        self.torque = 0.3*(self.Tbm.excavationDiam+2.0*self.Tbm.gap)*self.Tbm.CutterNo*locFr # in kNm
        self.availableBreakawayTorque = self.Tbm.breakawayTorque - self.torque
        self.torque+=self.breakawayTorque
        dar = 24.*locuf*locp*self.Tbm.rpm*60. # in m/gg con anni di 365 gg
        self.requiredThrustForce = self.Tbm.BackupDragForce+self.contactThrust+self.frictionForce

        # considerazioni sulla produzione
        productionMax = self.Tbm.maxProduction
        productionBase = 24.*locuf*locpBase*self.Tbm.rpm*60. # produzione teorica (in m/gg) a meno dei rallentamenti per rocce dure
        impactP1 = impactOnProduction(productionBase, productionMax)
        impactP3 = impactOnProduction(dar, productionBase)


        # indicatore di produzione
        #self.P0 = P0(self.t0, self.segmentLength) # giorni di produzione richiesto a scavare un metro del segmento
        self.P1 = P1(impactP1) # impatto sulla produzione
        self.P3 = P3(impactP3) # impatto del rallentamento per rocce dure
        self.P4 = P4(self.Tbm.type, 1., productionBase,  segment.length)
        self.P5 = P5(self.Tbm.type, self.cavityStabilityPar, self.frontStability.lambdae, productionBase,  segment.length)

        # tempi di produzione in giorni
        self.t0= self.segmentLength/(24.*locuf*locp*self.Tbm.rpm*60.) #giorni di scavo del segmento
        self.t1= self.segmentLength/(24.*locuf*locpBase*self.Tbm.rpm*60.) #giorni di scavo del segmento
        self.t3 = self.t0-self.t1 # extra tempo in giorni causato dalle rocce dure
        self.t4 = self.P4.duration
        self.t5 = self.P5.duration

        # ora che ho tutti i tempi ridetermino il dayly advance rate come segment length / (t1+t3+t4+t5)
        self.dailyAdvanceRate = self.segmentLength/(self.t1+self.t3+self.t4+self.t5)

        # indicatori geotecnici
        self.G1 = G1(self.Tbm.type, self.frontStability.lambdae, self.availableBreakawayTorque-self.frontStabilityBreakawayTorque)
        self.G2 = G2(self.Tbm.type, self.cavityStabilityPar, self.tailCavityStabilityPar, self.contactType)
        self.G5 = G5(self.Tbm.type, segment.descr, self.frontStability.lambdae)
        self.G6 = G6(self.Tbm.type)
        self.G7 = G7(self.Tbm.type)
        self.G8 = G8(self.Tbm.type)
        self.G11 = G11(self.Tbm.type, segment.descr, self.cavityStabilityPar)
        self.G12 = G12(self.Tbm.type, segment.descr, self.frontStability.lambdae, self.availableBreakawayTorque-self.frontStabilityBreakawayTorque)
        self.G13 = G13(self.Tbm.type, self.rockBurst.Val, self.availableBreakawayTorque-self.rockburstBreakawayTorque)

    def UrPi_HB(self, pi):
        #curva caratteristica con parametri di H-B secondo Carranza torres del 2006
        sigma0 = self.InSituCondition.SigmaV
        sci = self.Rock.Ucs
        R = self.Excavation.Radius
        psi = math.radians(self.MohrCoulomb.psi)
        ni = self.Rock.Ni
        G = self.Rock.G # riporto il modulo in MPa

        mb = self.HoekBrown.Mb
        s = self.HoekBrown.S
        a = self.HoekBrown.A
        nu = mb**((2.*a-1.)/a)
        mb_sci = sci*mb**((1.-a)/a)
        s_mb = s/(mb**(1./a))
        S0 = sigma0/mb_sci+s_mb
        # Pi = pi/mb_sci+s_mb
        x0 =((1.-math.sqrt(1.+16.*S0))/4.)**2
        Picr = solve(pcrit, x0, nu, a, S0, 0.00001)
        picr = (Picr-s_mb)*mb_sci
        self.Picr =picr
        sci_r = self.HoekBrown.ucsr
        mb_r = self.HoekBrown.Mr
        s_r = self.HoekBrown.Sr
        a_r = self.HoekBrown.Ar
        nu_r = mb_r**((2.*a_r-1.)/a_r)
        mb_sci_r = sci_r*mb_r**((1.-a_r)/a_r)
        s_mb_r = s_r/(mb_r**(1./a_r))
        S0_r = sigma0/mb_sci_r+s_mb_r
        Pi_r = pi/mb_sci_r+s_mb_r
        Picr_r = picr/mb_sci_r+s_mb_r
        #danzi.tn@20151113 utilizzo np.power per elevamento a potenza
#        Rpl = R*math.exp((Picr_r**(1.-a_r)-Pi_r**(1.-a_r))/((1.-a_r)*nu_r))
        _esp = (np.power(Picr_r,1.-a_r)-np.power(Pi_r,1.-a_r))/((1.-a_r)*nu_r)
        Rpl = R*np.exp(_esp)
        self.Rpl = Rpl
        G_r = G/mb_sci_r

        Kpsi = (1.+math.sin(psi))/(1.-math.sin(psi))
        A1 = -Kpsi
        A2 = 1.-ni-ni*Kpsi
        A3 = ni-(1.-ni)*Kpsi

        # condizioni iniziali su ur (ur1) e urP (ur1P)
        rho = 1.
        Rpl_2G_r = Rpl/(2.*G_r)
        if Rpl > R:
            # roclab nel caso di utilizzo dei soli valori di picco imposta a_r = 0.5
            # altrimenti considera il valore modificato di a_r ma non usa runge kutta ma la formula semplificata
            """
            if a_r != .5:
                # integrazione con runge kutta. teoricamente corretta per l'esempio di carranza torres
                # ma manca verifica piu' stesa visto che il roc support implementa la formula approssimata
                # valida per a_r = 0.5
                ur = Rpl_2G_r*(S0_r-Picr_r)
                urP = A1*ur\
                    +Rpl_2G_r*(1.-ni*(1.-A1))*(Picr_r-S0_r)\
                    -Rpl_2G_r*(A1+ni*(1.-A1))*(Picr_r+nu_r*Picr_r**a_r-S0_r)
                intPntCnt = 5
                h = (R/Rpl-1.)/(intPntCnt-1.)
                h_2 = h/2.
                c1 = A1
                for i in range(1, intPntCnt+1):
                    Sr_r = (Picr_r**(1.-a_r)+(1.-a_r)*nu_r*math.log(rho))**(1./(1.-a_r))
                    SrP_r = nu_r/rho*Sr_r**a_r
                    StP_r = (1.+a_r*nu_r*Sr_r**(a_r-1.))*SrP_r
                    c1 = -mb_sci_r*SrP_r
                    A2 = 1.-ni-ni*mb_sci_r*SrP_r
                    A3 = ni-(1.-ni)*mb_sci_r*SrP_r
                    c2 = Rpl_2G_r*(A2*SrP_r-A3*StP_r)

                    Sr_r_h_2 = (Picr_r**(1.-a_r)+(1.-a_r)*nu_r*math.log(rho+h_2))**(1./(1.-a_r))
                    SrP_r_h_2 = nu_r/(rho+h_2)*Sr_r_h_2**a_r
                    StP_r_h_2 = (1.+a_r*nu_r*Sr_r_h_2**(a_r-1.))*SrP_r_h_2
                    c1_h_2 = -mb_sci_r*SrP_r_h_2
                    A2 = 1.-ni-ni*mb_sci_r*SrP_r_h_2
                    A3 = ni-(1.-ni)*mb_sci_r*SrP_r_h_2
                    c2_h_2 = Rpl_2G_r*(A2*SrP_r_h_2-A3*StP_r_h_2)

                    Sr_r_h = (Picr_r**(1.-a_r)+(1.-a_r)*nu_r*math.log(rho+h))**(1./(1.-a_r))
                    SrP_r_h = nu_r/(rho+h)*Sr_r_h**a_r
                    StP_r_h = (1.+a_r*nu_r*Sr_r_h**(a_r-1.))*SrP_r_h
                    c1_h = -mb_sci_r*SrP_r_h
                    A2 = 1.-ni-ni*mb_sci_r*SrP_r_h
                    A3 = ni-(1.-ni)*mb_sci_r*SrP_r_h
                    c2_h = Rpl_2G_r*(A2*SrP_r_h-A3*StP_r_h)

                    k1 = h * U(rho, ur, urP, c1, c2)
                    k2 = h * U(rho+h_2, ur+h_2*urP, urP+h_2*k1, c1_h_2, c2_h_2)
                    k3 = h * U(rho+h_2, ur+h_2*urP+h_2**2*k1, h_2*k2, c1_h_2, c2_h_2)
                    k4 = h * U(rho+h, ur+h*urP+(h**2)/2.*k2, urP+h*k3, c1_h, c2_h)

                    ur += h*(urP+(k1+k2+k3)/6.)
                    urP += (k1+2.*k2+2.*k3+k4)/6.

                    r = Rpl-(i-1.)/(intPntCnt-1.)*(Rpl - R)
                    rho = r/Rpl
            else:
            """
            rho = R/Rpl
            ur1 = Rpl_2G_r*(S0_r-Picr_r)
            ur1P = A1*ur1\
                +Rpl_2G_r*(1.-ni*(1.-A1))*(Picr_r-S0_r)\
                -Rpl_2G_r*(A1+ni*(1.-A1))*(Picr_r+nu_r*Picr_r**a_r-S0_r)
            ur = (rho**A1-A1*rho)/(1.-A1)*ur1\
                +(rho-rho**A1)/(1.-A1)*ur1P\
                +Rpl_2G_r/4.*(A2-A3)/(1.-A1)*rho*(math.log(rho))**2\
                +Rpl_2G_r*((A2-A3)/(1.-A1)**2*math.sqrt(Picr_r)-.5*(A2-A1*A3)/(1.-A1)**3)\
                *(rho**A1-rho+(1.-A1)*rho*math.log(rho))

        else:
            ur = (S0_r-Picr_r)/(2.*G_r)*Rpl**2/R
        return ur

    def UrPi(self, pi):
        # ur in m
        # pi in MPa (1 MPa = 1000 kN/m2)
        coefTanFi = 1.0
        coefC = 1.0
        R = self.Excavation.Radius # in m
        ni = self.Rock.Ni
        E = self.Rock.E
        fi = math.radians(self.MohrCoulomb.Fi)
        fi = math.atan(math.tan(fi)/coefTanFi)
        #c = self.MohrCoulomb.C / 1000.0 / coefC # MPa
        psi = math.radians(self.Rock.Psi)

        fir = math.radians(self.MohrCoulomb.Fir)
        fir = math.atan(math.tan(fir)/coefTanFi)
        cr = self.MohrCoulomb.Cr / 1000.0 / coefC # MPa

        p0 = self.P0
        pcr = self.Pcr # in MPa
        pocp = self.Pocp
        pocr = self.Pocr
        Nfir = self.Nfir
        uremax = (1.0+ni)/E*(p0-pi)*R
        if pcr < p0:
            Ki = (1.0+math.sin(psi))/(1.0-math.sin(psi))
            pi_cr_tan = pi + cr / math.tan(fir)
            Rpl = (((pocr-pocp*math.sin(fi))/pi_cr_tan)**(1.0/(Nfir-1.0)))*R
            RplK_1rK = Rpl**(Ki+1.0)/R**Ki
            RplK_KrK = Rpl**(Nfir+Ki)/R**Ki-R**Nfir
            primaparte = RplK_1rK*pocp*math.sin(fi)+pocr*(1.0-2.0*ni)*(RplK_1rK-R)
            secondaparte = (1.0+Nfir*Ki-ni*(Ki+1)*(Nfir+1.0))*pi_cr_tan
            terzaparte = 1.0/((Nfir+Ki)*R**(Nfir-1.0))*RplK_KrK
            urplmax = ((1.0+ni)/E)*(primaparte-secondaparte*terzaparte)
        else:
            urplmax = 0.0
        return max(urplmax, uremax)

    def LDP_Panet_1995(self, x):
        # risultato in m
        # x in m
        urmax = self.UrPi_HB(0.0)
        R = self.Excavation.Radius # in m
        urx=urmax*(0.25+0.75*(1.0-(0.75/(0.75+x/R))**2)) # convergenza del cavo in m alla distanza x dal fronte
        return urx

    def LDP_Vlachopoulos_2009(self, x):
        # risultato in m
        # x in m
        umax = self.UrPi_HB(0.0)
        Rt = self.Excavation.Radius # in m
        Rp = self.Rpl
        Rstar = Rp/Rt
        u0star = math.exp(-0.15*Rstar)/3.0
        xstar = x/Rt
        ustar = 1-(1.0-u0star)*math.exp(-3.0*xstar/2.0/Rstar)
        return umax*ustar # convergenza del cavo in m alla distanza x dal fronte

    def CavityConvergence(self, x):
        # risultato in m
        # x in m
        # opt e' opzione di calcolo P = panet, V = Vlachopoulos
        opt = self.Tbm.LDP_type
        if opt == 'p' or opt == 'P':
            return self.LDP_Panet_1995(x)
        else:
            return self.LDP_Vlachopoulos_2009(x)

    def TunnelClosure(self, x):
        # risultato in m
        # x in m
        return self.CavityConvergence(x) - self.CavityConvergence(0.0)

    def PiUr(self, dur):
        # restituisce il valore di pressione equivalente a una convergenza del cavo pari a dur
        # iol risultato e' in MPa (1 MPa = 1000 kN/m2)
        p0 = self.InSituCondition.SigmaV
        ur = self.CavityConvergence(0.0) + dur
        pi = 0.0
        for i in range(0, int(math.floor(p0*200.0))):
            pi = i / 200.0
            urcur = self.UrPi_HB(pi)
            if urcur <= ur:
                return pi
        return pi

    def xLim(self, urlim):
        # risultato in m
        # urlim in m
        x = 0.0
        while self.TunnelClosure(x)<urlim and x < self.Tbm.Slen:
            x += 0.005 # incremento di 5 mm
        return x

    def pkCe2Gl(self, pkCe):
        #semplice conversione tra pk del cunicolo con la pk della galleria di linea (vale per la tratta nord)
        pkGl = 59230.0-pkCe
        return pkGl

class StabilizationMeasure:
    def __init__(self, pkFrom, pkTo, type, len):
        self.pkFrom =pkFrom
        self.pkTo = pkTo
        self.type = type
        self.len = len

class G1:
    def __init__(self, tbmType, lambdae, availableTorque):
        self.definition='Front stability'
        if tbmType=='O':
            imax = 2.5 # todo verificare valore
        elif tbmType=='S':
            imax = 2.25
        elif tbmType=='DS':
            imax = 1.5
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)

        if lambdae<.6:
            # tra 0.3 e 0.6 faccio calare linearmente sia la probabilita' che l'impatto
            self.probability = (.6-lambdae)/.3
            self.impact = (.6-lambdae)/.3*imax
        elif lambdae<.3:
            self.probability = 1.
            self.impact = imax
        else:   
            self.probability = 0.
            self.impact = 0.
        if availableTorque>=0.:
            # rimedio con la coppia e quindi annullo l'impatto
            self.impact = 0.

class G2:
    def __init__(self, tbmType, cavityStabilityPar, tailCavityStabilityPar, contactType): #, whichShield):
        self.definition='Cavity stability'
        if contactType==0:
            imax=0.
            self.probability = 0.
            self.impact = 0.
        elif contactType==1:
            imax=1.
            self.probability = 1.
            self.impact = imax
        elif contactType==2:
            imax=2.5
            self.probability = 1.
            self.impact = imax*cavityStabilityPar
        else:
            imax=2.75
            self.probability = 1.
            self.impact = imax

class G5:
    def __init__(self, tbmType, mat, lambdae):
        self.definition='Spalling - cavity'
        if tbmType=='O':
            imax = 2.5
        elif tbmType=='S':
            imax = 1
        elif tbmType=='DS':
            imax = 1.25
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)

        if 'KS' in mat:
            if lambdae >0.6:
                self.probability = 0.
                self.impact = 0.
            elif lambdae >.3:
                self.probability = 1.
                self.impact = imax*(0.6-lambdae)*2.
            else:
                self.probability = 1.
                self.impact = imax
        else:
            self.probability = 0.
            self.impact = 0.

class G6:
    def __init__(self, tbmType):
        self.definition='Cavities'
        if tbmType=='O':
            imax = 3.25
        elif tbmType=='S':
            imax = 1.5
        elif tbmType=='DS':
            imax = 1.75
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)

        self.probability = 1.
        self.impact = imax

class G7:
    def __init__(self, tbmType):
        self.definition='Water overflow'
        if tbmType=='O':
            imax = 1.75
        elif tbmType=='S':
            imax = 1.
        elif tbmType=='DS':
            imax = 1.25
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)

        self.probability = 1.
        self.impact = imax

class G8:
    def __init__(self, tbmType):
        self.definition='Gas overflow'
        if tbmType=='O':
            imax = 2.25
        elif tbmType=='S':
            imax = 2.25
        elif tbmType=='DS':
            imax = 2.25
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)

        self.probability = 1.
        self.impact = imax


class G11:
    def __init__(self, tbmType, mat, cavityStabilityPar):
        self.definition='Swelling'
        if tbmType=='O':
            imax = 0.
        elif tbmType=='S':
            imax = 1.
        elif tbmType=='DS':
            imax = 1.0
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        self.probability = 0.

        if '-R-' in mat:
            if cavityStabilityPar>0.:
                self.probability = 1.
                self.impact = imax*cavityStabilityPar
            else:
                self.impact = 0.
        else:
            self.probability = 0.
            self.impact = 0.

class G12:
    def __init__(self, tbmType, mat, lambdae, availableTorque):
        self.definition='Spalling - front'
        if tbmType=='O':
            imax = 2.25
        elif tbmType=='S':
            imax = 1.
        elif tbmType=='DS':
            imax = 1.5
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)

        if 'KS' in mat:
            if lambdae<.6:
                # tra 0.3 e 0.6 faccio calare linearmente sia la probabilita' che l'impatto
                self.probability = (.6-lambdae)/.3
                self.impact = (.6-lambdae)/.3*imax
            elif lambdae<.3:
                self.probability = 1.
                self.impact = imax
            else:   
                self.probability = 0.
                self.impact = 0.
            if availableTorque>0.:
                # rimedio con la coppia e quindi annullo l'impatto
                self.impact = 0.
        else:
            self.probability = 0.
            self.impact = 0.

class G13:
    def __init__(self, tbmType, rockBurstingPar, availableTorque):
        self.definition='Rockburst'
        if tbmType=='O':
            imax = 2.75
        elif tbmType=='S':
            imax = 1.5
        elif tbmType=='DS':
            imax = 1.
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)

        if rockBurstingPar<0.2:
            self.probability = 0.
            self.impact = 0.
        elif rockBurstingPar<0.3:
            self.probability = 1.
            self.impact = imax*(rockBurstingPar-0.2)/.1
        else:
            self.probability = 1.
            self.impact = imax
        if availableTorque>=0.:
            # rimedio con la coppia e quindi annullo l'impatto
            self.impact = 0.

# i parametri di produzione possono essere applicati solo alla fine sommando tutti i segmenti
class P0: #tempo di scavo effettivo
    def __init__(self, par,  length):
        self.probability = 1.
        self.impact = par/length

class P1: #tempo di scavo in condizioni standard si applica sempre
    def __init__(self, par):
        self.probability = 1.
        self.impact = par

class P2: #tempo di montaggio e smontaggio lo si puo' associare direttamente alla tbm e lo spalmo su tutto il tracciato
    def __init__(self, tbmType):
        self.definition='Assembly and disassembly'
        # imax definito come il tempo in giorni di montaggio/smontaggio/spostamento
        if tbmType=='O':
            imax = 7.*30.
        elif tbmType=='S':
            imax = 8.2*30.
        elif tbmType=='DS':
            imax = 9.*30.
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        self.duration = imax
        self.impact=0.
        self.probability=0.

    def defineImpact(self, tRef):
        #calcolo l'impatto come produzione pesata sul tempo minimo di produzione possibile
        # la produzione e' inversamente proporzionale al tempo di produzine
        refProd = 1./tRef
        newProd = 1./(self.duration+tRef)
        impact = impactOnProduction(newProd, refProd)
        if impact>0.:
            self.probability = 1.
            self.impact = impact
        else:
            self.probability = 0.
            self.impact = 0.


class P3: #tempo extra in giorni per scavo in rocce dure
    def __init__(self, par):
        if par > 0.:
            self.probability = 1.
            self.impact = par
        else:
            self.probability = 0.
            self.impact = 0.

class P4:
    def __init__(self, tbmType,  par, refProductivity, length ):
        self.definition='Preparatory works for borehole in advance'
        if tbmType=='O':
            imax = .5/24. #ore al giorno spese per le prospezioni
        elif tbmType=='S':
            imax = .5/24. #ore al giorno spese per le prospezioni
        elif tbmType=='DS':
            imax = .5/24. #ore al giorno spese per le prospezioni
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        # danzi.tn@20151112 duration modificata
        newProductivity = refProductivity/(1.+imax)
        self.duration = length*(1/newProductivity-1/refProductivity) # impatto in giorni sulla produzione di quel segmento
        impact = impactOnProduction(newProductivity, refProductivity)

        if par>0. and impact>0.:
            self.probability = 1.
            self.impact = impact # impatto in ore per la tratta di lunghezza length
        else:
            self.probability = 0.
            self.impact = 0.


class P5:
    def __init__(self, tbmType, par, lambdae, refProductivity,  length):
        # considera un incremento dei tempi per eseguire i consolidamenti.
        # il tempo richiesto per i consolidamenti e' gia' contato nell'UF
        # considerate le ipotesi di TC servono 4.5 ore per ogni m di apprestamento di consolidamento
        self.definition='Preparatory works for consolidation'
        if tbmType=='O':
            imax = 4.5/24.
        elif tbmType=='S':
            imax = 4.5/24. # giorni per metro di apprestamento
        elif tbmType=='DS':
            imax = 4.5/24. # giorni per metro di apprestamento
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        imax*=length # tempo richiesto in giorni per consolidare tutta la lunghezza del segmento
        newProductivity = refProductivity/(1.+imax)
        impact = impactOnProduction(newProductivity, refProductivity)

        if par>0. and impact>0.:
            self.probability = 1.
            self.impact = impact # impatto in ore per la tratta di lunghezza length
            self.duration = imax # impatto in giorni per la produzione di quel segmento
        elif lambdae<.6 and lambdae>=.3 and impact>0.:
            self.probability = 1.
            self.impact = impact*(.6-lambdae)/.3 # impatto in ore per la tratta di lunghezza length
            self.duration = imax*(.6-lambdae)/.3 # impatto in giorni per la produzione di quel segmento
        elif lambdae<.3 and impact>0.:
            self.probability = 1.
            self.impact = impact # impatto in ore per la tratta di lunghezza length
            self.duration = imax # impatto in giorni per la produzione di quel segmento
        else:
            self.probability = 0.
            self.impact = 0.
            self.duration = 0.

class P6: #realizzaqzione del rivestimento . Si applica solo a tbm aperta direzione sud
    def __init__(self):
        self.definition='Lining execution'
        self.impact=0.
        self.probability=0.
        self.duration=0.

    def defineImpact(self, tRef, tbmType, alnKey):
        #calcolo l'impatto come produzione pesata sul tempo minimo di produzione possibile
        # la produzione e' inversamente proporzionale al tempo di produzine
        # imax definito come il tempo in giorni per l'esecuzione
        if alnKey=='CE' and tbmType=='O':
            imax = 11.2*30.
        else:
            imax=0.
        self.duration = imax
        refProd = 1./tRef
        newProd = 1./(self.duration+tRef)
        impact = impactOnProduction(newProd, refProd)
        if impact>0.:
            self.probability = 1.
            self.impact = impact
        else:
            self.probability = 0.
            self.impact = 0.


# i parametri vari si applicano genericamente alla tbm e sono indipendenti dai punti del tracciato
class V1:
    def __init__(self, tbmType):
        self.definition='HSE'
        self.probability=1.
        if tbmType=='O':
            imax = 2.5
        elif tbmType=='S':
            imax = 1.25
        elif tbmType=='DS':
            imax = 1.5
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        self.impact=imax

class V2:
    def __init__(self, tbmType, tbmName):
        # definisco il costo base in proporzione al diametro (1 mln al metro) in mln
        # DS sui 26 mln / 16mln
        # S sui 24 mln /14.5 mln
        # O sui 15
        self.definition='Cost'
        self.probability=0.
        if 'CE' in tbmName:
            if tbmType=='O':
                self.cost = 7. 
            elif tbmType=='S':
                self.cost = 14.5 
            elif tbmType=='DS':
                self.cost = 16. 
            else:
                print 'Errore tipo di tbm inesistente!'
                exit(1)
        else:
            if tbmType=='O':
                self.cost = 15. 
            elif tbmType=='S':
                self.cost = 24 
            elif tbmType=='DS':
                self.cost = 26. 
            else:
                print 'Errore tipo di tbm inesistente!'
                exit(1)
        self.impact=0.

    def defineImpact(self, costRef):
        impact = impactOnCost(self.cost, costRef)
        if impact>0.:
            self.probability = 1.
            self.impact = impact
        else:
            self.probability = 0.
            self.impact = 0.


class V3:
    def __init__(self, tbmType, dotation): 
        # servira' avvantaggiare rbs perche' meglio dotata
        self.definition='Prospection tools'
        self.probability=1.
        if tbmType=='O':
            imax = 1.
        elif tbmType=='S':
            imax = 1.25
        elif tbmType=='DS':
            imax = 1.5
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        self.impact=imax*(1.-dotation)

class V4:
    def __init__(self, tbmType):
        self.definition='Alignment'
        self.probability=1.
        if tbmType=='O':
            imax = 1.
        elif tbmType=='S':
            imax = 2.
        elif tbmType=='DS':
            imax = 1.5
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        self.impact=imax

class V5:
    def __init__(self, tbmType):
        self.definition='Lining integrity'
        self.probability=1.
        if tbmType=='O':
            imax = 0.
        elif tbmType=='S':
            imax = 2.
        elif tbmType=='DS':
            imax = 1.
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        self.impact=imax

class V6:
    def __init__(self, tbmType):
        self.definition='TBM complexity'
        self.probability=1.
        if tbmType=='O':
            imax = 1.
        elif tbmType=='S':
            imax = 1.25
        elif tbmType=='DS':
            imax = 1.5
        else:
            print 'Errore tipo di tbm inesistente!'
            exit(1)
        self.impact=imax

class PerformanceIndex:
    def __init__(self, definition):
        self.definition=definition
        self.minImpact=0.
        self.maxImpact=0.
        self.avgImpact=0.
        self.appliedLength=0.
        self.percentOfApplication=0.
        self.totalImpact=0.
        self.probabilityScore=0.

    def updateIndex(self, pCur, iCur, length):
        if pCur >0.:
            if self.minImpact>0.:
                self.minImpact=min(self.minImpact, iCur)
            else:
                self.minImpact=iCur
            self.maxImpact=max(self.maxImpact, iCur)
            self.avgImpact+=length*pCur*iCur
            self.appliedLength+=length*pCur

    def convertDaysToImpactAndFinalizeIndex(self, refLength):
        days = self.avgImpact
        self.avgImpact = impactOfProductionDaysAftes2012(days)
        self.minImpact = self.avgImpact
        self.maxImpact = self.avgImpact
        self.percentOfApplication=self.appliedLength/refLength
        self.probabilityScore = probabilityAftes2012(self.percentOfApplication)
        self.totalImpact=self.avgImpact*self.probabilityScore

    def finalizeIndex(self, refLength):
        if self.appliedLength >0.:
            self.avgImpact/=self.appliedLength
        self.percentOfApplication=self.appliedLength/refLength
        self.probabilityScore = probabilityAftes2012(self.percentOfApplication)
        self.totalImpact=self.avgImpact*self.probabilityScore

    def printOut(self):
        print '%s: min impact=%f; max impact=%f; avg impact=%f; applied length=%f; percent of application=%f; probability score=%f; total impact=%f' \
            % (self.definition, self.minImpact, self.maxImpact, self.avgImpact, self.appliedLength, self.percentOfApplication, self.probabilityScore, self.totalImpact)

class InfoAlignment:
    # gabriele@20151114 friction parametrica
    def __init__(self, descr, tbmKey, pkStart, pkEnd, fiRi, frictionCoeff):
        self.description=descr
        self.tbmKey=tbmKey
        self.pkStart=pkStart
        self.pkEnd=pkEnd
        self.length=max(pkStart, pkEnd)-min(pkStart, pkEnd)
        # gabriele@20151114 friction parametrica
        self.fiRi = fiRi
        self.frictionCoeff = frictionCoeff
