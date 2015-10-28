import math

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
    def __init__(self, gamma, ni, e, ucs,  st, psi):
        self.Gamma = gamma
        self.Ni = ni
        self.E = e
        self.Ucs = ucs
        self.Sigmat = st #tensile strength
        self.Psi = psi
        self.Lambda = e*ni/((1.0+ni)*(1.0-2.0*ni))
        self.G = e/(2.*(1.+ni))

class InSituCondition:
# caratteristiche dell'ammasso e stato tensionale locale
    def __init__(self, overburden, groundwaterdepth, gamma, k0min, k0max, gsi, rmr):
        self.Overburden = overburden #copertura netta
        self.Groundwaterdepth = groundwaterdepth #copertura netta
        self.K0 = 1.0
        self.K0min = k0min
        self.K0max = k0max
        self.Kp = 1.0
        self.Ka = 1.0 # posso definire RMR o GSI

        if gsi > 0.0:
            self.Gsi = gsi
        else:
            self.Gsi = rmr - 5.0
            
        if rmr > 0.0:
            self.Rmr = rmr
        else:
            self.Rmr = gsi+5
        self.SigmaV = gamma*overburden/1000.0 # MPa
    
    def UpdateK0KaKp(self, typ, fi):
        self.Kp = (1.0 + math.sin(math.radians(fi)))/(1.0 - math.sin(math.radians(fi)))
        self.Ka = 1.0 / self.Kp
        if typ == 'd':
            self.K0 = (self.K0min+self.K0max)/2.0
        else:
            self.K0 = self.Ka*(1.0+math.sin(math.radians(fi)))

class HoekBrown:	#caratteristiche ammasso secondo Hoek e Brown
    def __init__(self, gamma, ucs, mi, e, gsi, d, sv):
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
        dr = 0. # TODO mettere legge
        ucsr = ucs # TODO mettere legge
        gsir = gsi # TODO mettere legge
        self.dr = dr
        self.ucsr = ucsr
        self.gsir = gsir
        self.Mr = mi*math.exp((gsir-100.0)/(28.0-14.0*dr)) # parametro di Hoek & Brown
        self.Sr = math.exp((gsir-100.0)/(9.0-3.0*dr))	# parametro di Hoek & Brown
        if dr != 0.:
            self.Ar = 0.5 #min(0.5, self.A)
        else:
            self.Ar = 0.5 #self.A 
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
    
    #inizializzazione per terreni
    def SetSoil(self, fi, c, fir):
        self.Fi = fi
        self.C = c
        self.Fir = fir
        self.SigmaCm0 = 2.0*c*math.cos(math.radians(fi))/(1.0-math.sin(math.radians(fi)))/1000.0

class Excavation:
    # caratteristiche legate allo scavo
    def __init__(self, typ, area, width, height, length, overburden, fi):
        self.Type = typ 						#Mech
        self.Area = area						#Area della sezione di scavo
        self.Width = width						#ampiezza dello sezione di scavo
        self.Height = height					#altezza della sezione di scavo
        self.Length = length					#lunghezza di riferimento per il segmento di scavo (per il calcolo della convergenza in quel punto)
        self.Radius = math.sqrt(area/math.pi)	#raggio di scavo equivalente (se policentrica riconduce la sezione di scavo circolare)
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
    def __init__(self, type,  slen, sdiammin, sdiammax, overexcav, cno, cr, ct, cs, rpm, Ft, totalContactThrust,  installedThrustForce, installedAuxiliaryThrustForce, nominalTorque, breakawayTorque, backupDragForce, friction, LDP_type):
        self.type = type # tipo tbm: O, S, DS
        self.rpm = rpm
        self.Slen = slen # shield length
        self.SdiamMin = sdiammin    #shield minimum diameter
        self.SdiamMax = sdiammax    #shield maximum diameter
        self.OverExcavation = overexcav #overexcavation in m
        self.CutterNo = cno # numebr of cutters
        self.CutterRadius = cr  #Cutter radius
        self.CutterThickness = ct #Cutterthickness
        self.CutterSpacing = cs #Cutter spacing
        self.Friction = friction # coefficiente di attrito tra ammasso e scudo
        self.BackupDragForce = backupDragForce # kN (8000 per la GL, 4000 per il CE
        # penetration rate per ogni decina di rmr: 0, 10, 20, 30.....100
        self.penetrationPerRevolution = (0.00430150833333333, 0.00430150833333333, 0.00513665, 0.00597179166666667, 0.0065686, 0.007082075, 0.00729155, 0.00741769166666667, 0.0065785, 0.00573930833333333, 0.00573930833333333)  #in m per rivoluzione
        # definisco l'Utilization Factor
        if self.type == 'O':
            self.uf = (0.110166666666667,0.110166666666667,0.159111111111111,0.208055555555556,0.288194444444445,0.368333333333333,0.4335,0.498666666666667,0.498666666666667,0.498666666666667,0.498666666666667)
        elif self.type =='D':
            self.uf = (0.154166666666667,0.154166666666667,0.189583333333333,0.225,0.285416666666667,0.345833333333333,0.377083333333333,0.408333333333333,0.408333333333333,0.408333333333333,0.408333333333333)
        elif self.type == 'DS':
            self.uf = (0.15,0.15,0.219166666666667,0.288333333333333,0.354722222222222,0.421111111111111,0.442361111111111,0.463611111111111,0.463611111111111,0.463611111111111,0.463611111111111)
        else:
            exit(-700)
        # angolo da definire in base alla macchina
        # come suggerito da Rostami et Al. lo faccio variare linearmente da -0.2 a 0.2 in modo inversamente proporzionale allo spessore del cutter
        tInf = 0.013 # 13 mm
        tSup = 0.024 # 24 mm
        self.psi = 0.2 - 0.4 * (ct-tInf) / (tSup-tInf) # angolo da definire in base alla macchina
        self.Ft = Ft # kN max load per cutter ring
        self.totalContactThrust = totalContactThrust #in kN
        self.installedThrustForce = installedThrustForce #in kN
        self.installedAuxiliaryThrustForce = installedAuxiliaryThrustForce #in kN
        self.nominalTorque = nominalTorque #in kNm
        self.breakawayTorque = breakawayTorque #in kNm
        self.LDP_type = LDP_type # tipo di formulazione per convergenza del cavo: P = Panet, V = Vlachopoulos-Dietrich

class TBMSegment:
    # definisco la condizione intrinseca (TODO verificare definizione con Luca o Paolo)
    def __init__(self, gamma, ni, e, ucs, st, psi, mi, overburden, groundwaterdepth, k0min, k0max, gsi, rmr, excavType, excavArea, excavWidth, excavHeight, refLength, pi, aunsupported, tbm):
        if ucs <= 1.0:
            print "gamma= %f E= %f ucs= %f" % (gamma, e, ucs)
        self.Rock = Rock(gamma, ni, e, ucs,  st, psi)	#importo definizione di Rock
        self.InSituCondition = InSituCondition(overburden, groundwaterdepth, gamma, k0min, k0max, gsi, rmr)	#importo defizione di stato in situ
        if excavType == 'Mech':
            self.D = 0.0
        else:
            self.D = 0.2			
        self.HoekBrown = HoekBrown(gamma, ucs, mi, e, self.InSituCondition.Gsi, self.D, self.InSituCondition.SigmaV)
        self.MohrCoulomb = MohrCoulomb()
        self.MohrCoulomb.SetRock(self.HoekBrown, ucs)
        self.Excavation = Excavation(excavType, excavArea, excavWidth, excavHeight, refLength, overburden, self.MohrCoulomb.Fi)
        self.InSituCondition.UpdateK0KaKp(self.Excavation.OverburdenType,self.MohrCoulomb.Fi)
        self.rockBurst = rockBursting(ucs, rmr, self.InSituCondition.SigmaV)
        self.Tamez = Tamez('r',overburden, self.Excavation, self.MohrCoulomb, self.InSituCondition, gamma, pi, aunsupported)
        self.frontStability = frontStability(self.InSituCondition.Overburden/(2.0*self.Excavation.Radius), \
                                    self.MohrCoulomb.SigmaCm0, self.InSituCondition.SigmaV, self.InSituCondition.Kp) #, 1.0+math.sin(math.radians(self.MohrCoulomb.Fi)))
 
        R = self.Excavation.Radius # in m
        ni = self.Rock.Ni
        fi = math.radians(self.MohrCoulomb.Fi)
        c = self.MohrCoulomb.C / 1000. # MPa
        fir = math.radians(self.MohrCoulomb.Fir)
        cr = self.MohrCoulomb.C / 1000. # MPa
        pi_cr_tan = cr / math.tan(fir)
        p0 = self.Rock.Gamma * (self.InSituCondition.Overburden+self.Excavation.Height/2.0) / 1000.0 # in MPa
        self.P0 = p0
        self.Pcr = p0 * (1.-math.sin(fi)) - c * math.cos(fi) # in MPa
        self.Pocp = p0 + c / math.tan(fi)
        self.Pocr = p0 + cr / math.tan(fir)
        self.Nfir = (1.+math.sin(fir)) / (1.-math.sin(fir))
        if self.Pcr < p0:
            self.Rpl = (((self.Pocr-self.Pocp*math.sin(fi))/pi_cr_tan)**(1.0/(self.Nfir-1.)))*R
        else:
            self.Rpl = R
        
        self.Tbm = tbm
        self.TunnelClosureAtShieldEnd = self.TunnelClosure(self.Tbm.Slen) # min(self.TunnelClosure(self.Tbm.Slen, 'P'),  R)
        
        # definisco thrust e torque
        psi = self.Tbm.psi
        ucs = self.Rock.Ucs
        sigmat = ucs/12.0 # self.Rock.Sigmat
        RMR = self.InSituCondition.Rmr
        rate = self.Tbm.penetrationPerRevolution
        uf = self.Tbm.uf

        i_1 = int(math.floor(RMR/10.0))
        i = i_1+1
        locp = rate[i_1]+(rate[i]-rate[i-1])/10.0*(RMR-i_1*10)
        locuf = uf[i_1]+(uf[i]-uf[i-1])/10.0*(RMR-i_1*10)
        locfi = math.acos((self.Tbm.CutterRadius-locp)/self.Tbm.CutterRadius)
        locP0 = 2.12*math.pow((self.Tbm.CutterSpacing*(ucs**2)*sigmat/(locfi*math.sqrt(self.Tbm.CutterRadius*self.Tbm.CutterThickness))), 1.0/3.0)
        locFt = 1000.0*locP0*locfi*self.Tbm.CutterRadius*self.Tbm.CutterThickness/(1.0+psi) # in kN
        pRateReduction = 0.0
        if locFt > self.Tbm.Ft:
            locFt = self.Tbm.Ft
            locfi=locFt*(1.0+psi)/(1000.0*locP0*self.Tbm.CutterRadius*self.Tbm.CutterThickness)
            pRid = self.Tbm.CutterRadius*(1.-math.cos(locfi))
            pRateReduction = locp-pRid
            locp = pRid
            
        locFn = locFt*math.cos(locfi/2.0) # in kN
        locFr = locFt*math.sin(locfi/2.0) # in kN
        self.penetrationRate = locp # m / rotazione
        self.penetrationRateReduction = pRateReduction
        self.contactThrust = self.Tbm.CutterNo*locFn # in kN
        self.torque = 0.3*(self.Tbm.SdiamMax+2.0*self.Tbm.OverExcavation)*self.Tbm.CutterNo*locFr # in kNm
        self.dailyAdvanceRate = 24.*locuf*locp*self.Tbm.rpm*60.*340./365. # in m/gg con anni di 340 gg
        
        if self.TunnelClosureAtShieldEnd>self.Tbm.OverExcavation:
            # definisco il punto di contatto sullo scudo
            self.Xcontact = self.xLim(self.Tbm.OverExcavation)
            # integrazione semplificata, assumo la pressione come triangolare
            maxPressure = self.PiUr(self.Tbm.OverExcavation) - self.PiUr(self.TunnelClosureAtShieldEnd)
            total = maxPressure*(self.Tbm.Slen-self.Xcontact)/2.0
            
            """
            # integro la pressione sullo scudo dal punto di contatto a fine scudo
            pref = self.PiUr(self.Tbm.OverExcavation)
            x = self.xLim(self.Tbm.OverExcavation)
            pcurr = self.PiUr(x)
            pi_1 = pref - pcurr
            pi = 0.0
            step = 0.05 #(self.Tbm.Slen - self.Xcontact)/1000.0 # step di integrazione in m
            x += step
            total = 0.0
            while x <= self.Tbm.Slen:
                currClosure = self.TunnelClosure(x)
                pcurr = self.PiUr(currClosure)
                pi = pref - pcurr
                total += (pi+pi_1)/2.0*step
                pi_1 = pi
                x += step
            """
            self.frictionForce = total*self.Tbm.SdiamMax*math.pi*self.Tbm.Friction*1000.0 # forza in kN
        else:
            self.frictionForce = 0.0 # in kN
            self.Xcontact = tbm.Slen
        self.availableThrust = self.Tbm.installedThrustForce - self.contactThrust - self.Tbm.BackupDragForce
        self.requiredThrustForce = self.Tbm.BackupDragForce+self.contactThrust+self.frictionForce

   
    def UrPi_HB(self, pi):
        #curva caratteristica con parametri di H-B secondo Carranza torres del 2006
        sigma0 = self.InSituCondition.SigmaV
        sci = self.Rock.Ucs
        R = self.Excavation.Radius
        psi = math.radians(self.Rock.Psi)
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
        Rpl = R*math.exp((Picr_r**(1.-a_r)-Pi_r**(1.-a_r))/((1.-a_r)*nu_r))
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
                intPntCnt = 20
                h = (R/Rpl-1.)/(intPntCnt-1.)
                h_2 = h/2.
                c1 = A1
                for i in range(1, intPntCnt+1):
                    Sr_r = (Picr_r**(1.-a_r)+(1.-a_r)*nu_r*math.log(rho))**(1./(1.-a_r))
                    SrP_r = nu_r/rho*Sr_r**a_r
                    StP_r = (1.+a_r*nu_r*Sr_r**(a_r-1.))*SrP_r
                    c2 = Rpl_2G_r*(A2*SrP_r-A3*StP_r)

                    Sr_r_h_2 = (Picr_r**(1.-a_r)+(1.-a_r)*nu_r*math.log(rho+h_2))**(1./(1.-a_r))
                    SrP_r_h_2 = nu_r/(rho+h_2)*Sr_r_h_2**a_r
                    StP_r_h_2 = (1.+a_r*nu_r*Sr_r_h_2**(a_r-1.))*SrP_r_h_2
                    c2_h_2 = Rpl_2G_r*(A2*SrP_r_h_2-A3*StP_r_h_2)

                    Sr_r_h = (Picr_r**(1.-a_r)+(1.-a_r)*nu_r*math.log(rho+h))**(1./(1.-a_r))
                    SrP_r_h = nu_r/(rho+h)*Sr_r_h**a_r
                    StP_r_h = (1.+a_r*nu_r*Sr_r_h**(a_r-1.))*SrP_r_h
                    c2_h = Rpl_2G_r*(A2*SrP_r_h-A3*StP_r_h)

                    k1 = h * U(rho, ur, urP, c1, c2)
                    k2 = h * U(rho+h_2, ur+h_2*urP, urP+h_2*k1, c1, c2_h_2)
                    k3 = h * U(rho+h_2, ur+h_2*urP+h_2**2*k1, h_2*k2, c1, c2_h_2)
                    k4 = h * U(rho+h, ur+h*urP+(h**2)/2.*k2, urP+h*k3, c1, c2_h)
                    
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
        urmax = self.UrPi(0.0)
        R = self.Excavation.Radius # in m
        return urmax*(0.25+0.75*(1.0-(0.75/(0.75+x/R))**2)) # convergenza del cavo in m alla distanza x dal fronte

    def LDP_Vlachopoulos_2009(self, x):
        # risultato in m
        # x in m
        umax = self.UrPi(0.0)
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
        p0 = self.P0
        ur = self.CavityConvergence(0.0) + dur
        pi = 0.0
        for i in range(0, int(math.floor(p0*200.0))):
            pi = i / 200.0
            urcur = self.UrPi(pi)
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
