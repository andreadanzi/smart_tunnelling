import math

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
        self.G = e/(2*(1+ni))

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
        self.SigmaV = gamma*overburden/1000.0
    
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
        self.Mr = mi*math.exp((gsi-100.0)/(28.0-14.0*1.0)) # parametro di Hoek & Brown
        self.Sr = math.exp((gsi-100.0)/(9.0-3.0*1.0))	# parametro di Hoek & Brown
        self.Ar = min(0.5, self.A)
        self.SigmaC = ucs*self.S**self.A	# parametro di Hoek & Brown
        self.SigmaCm = ucs*(((self.Mb+4.0*self.S-self.A*(self.Mb-8.0*self.S))*(self.Mb/4.0+self.S)**(self.A-1.0))/(2.0*(1.0+self.A)*(2.0+self.A)))	# parametro di Hoek & Brown
        self.Sigma3max = (0.47*(self.SigmaCm/sv)**(-0.94))*self.SigmaCm # parametro di Hoek & Brown

class MohrCoulomb:
	def __init__(self):
		self.Fi =0.0
		self.Fir = 0.0
		self.C = 0.0
		self.SigmaCm0 = 0.0 
	
	# inizializzazione per rocce
	def SetRock(self, hb, ucs):
		self.Fi = math.degrees(math.asin((6.0*hb.A*hb.Mb*(hb.S+hb.Mb*hb.Sigma3max/ucs)**(hb.A-1.0))\
				/(2.0*(1.0+hb.A)*(2.0+hb.A)+(6.0*hb.A*hb.Mb*(hb.S+hb.Mb*hb.Sigma3max/ucs)**(hb.A-1.0)))))
		self.Fir = math.degrees(math.asin((6.0*hb.Ar*hb.Mr*(hb.Sr+hb.Mr*hb.Sigma3max/ucs)**(hb.Ar-1.0))\
				/(2.0*(1.0+hb.Ar)*(2.0+hb.Ar)+(6.0*hb.Ar*hb.Mr*(hb.Sr+hb.Mr*hb.Sigma3max/ucs)**(hb.Ar-1.0)))))
		self.C = (ucs*((1.0+2.0*hb.A)*hb.S+(1.0-hb.A)*hb.Mb*(hb.Sigma3max/ucs))*(hb.S+hb.Mb*(hb.Sigma3max/ucs))**(hb.A-1.0)) \
				/((1.0+hb.A)*(2.0+hb.A)*math.sqrt(1.0+(6.0*hb.A*hb.Mb*(hb.S+hb.Mb*(hb.Sigma3max/ucs))**(hb.A-1.0))/((1.0+hb.A)*(2.0+hb.A))))*1000.0
		self.SigmaCm0 = 2.0*self.C*math.cos(math.radians(self.Fi))/(1.0-math.sin(math.radians(self.Fi)))/1000.0
	
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

class BrittleFailureRisk:
	# come da Hoek, Carranza, Torres, 2002
	def __init__(self, scm, p0):
		self.Val = p0/scm
		if self.Val < 0.1:
			self.Class = 'Stable behaviour'
		elif self.Val < 0.2:
			self.Class = 'Spalling-Slabbing'
		elif self.Val < 0.3:
			self.Class = 'Rockbursting'
		elif self.Val < 0.4:
			self.Class = 'Squeezing'
		else:
			self.Class = 'Severe Squeezing'
			
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
    def __init__(self, slen, sdiammin, sdiammax, overexcav, cno, cr, ct, cs, friction):
        self.Slen = slen # shield length
        self.SdiamMin = sdiammin    #shield minimum diameter
        self.SdiamMax = sdiammax    #shield maximum diameter
        self.OverExcavation = overexcav #overexcavation in m
        self.CutterNo = cno # numebr of cutters
        self.CutterRadius = cr  #Cutter radius
        self.CutterThickness = ct #Cutterthickness
        self.CutterSpacing = cs #Cutter spacing
        self.Friction = friction # coefficiente di attrito tra ammasso e scudo
        self.BackupDragForce = 8000.0 # kN
       
    def SetThrustAndTorque(self, psi, ucs, sigmat,  RMR):
        rate = (0.003968, 0.003968, 0.00496, 0.005952, 0.007824, 0.009696, 0.011352, 0.013008, 0.011136, 0.009264, 0.009264) #in m per rivoluzione
        i_1 = int(math.floor(RMR/10.0))
        i = i_1+1
        locp = rate(i_1)+(rate(i)-rate(i-1))/10.0*(RMR-i_1*10)
        locfi = math.acos((self.CutterRadius-locp)/self.CutterRadius)
        locP0 = 2.12*math.pow((self.CutterSpacing*(ucs**2)*sigmat/(locfi*math.sqrt(self.CutterRadius*self.CutterThickness))), 1.0/3.0)
        locFt = locP0*locfi*self.CutterRadius*self.CutterThickness/(1.0+psi)
        locFn = locFt*math.cos(locfi/2.0)
        locFr = locFt*math.sin(locfi/2.0)
        self.Thrust = self.CutterNo*locFn
        self.Torque = 0.3*(self.SdiamMax+2.0*self.OverExcavation)*self.CutterNo*locFr

class TBMSegment:
    # definisco la condizione intrinseca (TODO verificare definizione con Luca o Paolo)
    def __init__(self, gamma, ni, e, ucs, st, psi, mi, overburden, groundwaterdepth, k0min, k0max, rcType, rcValue, excavType, excavArea, excavWidth, excavHeight, refLength, pi, aunsupported, tbm):
        self.Rock = Rock(gamma, ni, e, ucs,  st, psi)	#importo definizione di Rock
        self.InSituCondition = InSituCondition(overburden, groundwaterdepth, gamma, k0min, k0max, rcType, rcValue)	#importo defizione di stato in situ
        if excavType == 'Mech':
            self.D = 0.0
        else:
            self.D = 0.2			
        self.HoekBrown = HoekBrown(gamma, ucs, mi, e, self.InSituCondition.Gsi, self.D, self.InSituCondition.SigmaV)
        self.MohrCoulomb = MohrCoulomb()
        self.MohrCoulomb.SetRock(self.HoekBrown, ucs)
        self.Excavation = Excavation(excavType, excavArea, excavWidth, excavHeight, refLength, overburden, self.MohrCoulomb.Fi)
        self.InSituCondition.UpdateK0KaKp(self.Excavation.OverburdenType,self.MohrCoulomb.Fi)
        self.BrittleFailureRisk = BrittleFailureRisk(self.HoekBrown.SigmaCm,self.InSituCondition.SigmaV)
        self.Tamez = Tamez('r',overburden, self.Excavation, self.MohrCoulomb, self.InSituCondition, gamma, pi, aunsupported)
 
        R = self.Excavation.Radius # in m
        ni = self.Rock.Ni
        fi = math.radians(self.MohrCoulomb.Fi)
        fir = math.radians(self.MohrCoulomb.Fir)
        c = self.MohrCoulomb.C / 1000.0 # MPa
        pi_c_tan = c / math.tan(fir)
        p0 = self.Rock.Gamma * (self.InSituCondition.Overburden+self.Excavation.Height/2.0) / 1000.0 # in MPa
        self.P0 = p0
        self.Pcr = p0 * (1.0-math.sin(fi)) - c * math.cos(fi) # in MPa
        self.Pocp = p0 + c / math.tan(fi)
        self.Pocr = p0 + c / math.tan(fir)
        self.Nfir = (1.0+math.sin(fir)) / (1.0-math.sin(fir))
        if self.Pcr < p0:
            self.Rpl = (((self.Pocr-self.Pocp*math.sin(fi))/pi_c_tan)**(1.0/(self.Nfir-1.0)))*R
        else:
            self.Rpl = R
        
        self.Tbm = tbm
        self.TunnelClosureAtShieldEnd = self.TunnelClosure(self.Tbm.Slen)
        """
        if self.TunnelClosureAtShieldEnd>self.Tbm.OverExcavation:
            # definisco il punto di contatto sullo scudo
            self.Xcontact = self.xLim(self.Tbm.OverExcavation)
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
            self.PressureOnShield = total*self.Tbm.SdiamMin*math.pi*self.Tbm.Friction*1000.0 # forza in kN
        else:
            self.PressureOnShield = 0.0 # in kN
            self.Xcontact = tbm.OverExcavation
        """
    
    def UrPi(self, pi):
        # ur in m
        # pi in MPa (1 MPa = 1000 kN/m2)
        R = self.Excavation.Radius # in m
        ni = self.Rock.Ni
        E = self.Rock.E
        fi = math.radians(self.MohrCoulomb.Fi)
        fir = math.radians(self.MohrCoulomb.Fir)
        c = self.MohrCoulomb.C / 1000.0 # MPa
        psi = math.radians(self.Rock.Psi)
        p0 = self.P0
        pcr = self.Pcr # in MPa
        pocp = self.Pocp
        pocr = self.Pocr
        Nfir = self.Nfir
        uremax = (1.0+ni)/E*(p0-pi)*R
        if pcr < p0:
            Ki = (1.0+math.sin(psi))/(1.0-math.sin(psi))
            pi_c_tan = pi + c / math.tan(fir)
            Rpl = (((pocr-pocp*math.sin(fi))/pi_c_tan)**(1.0/(Nfir-1.0)))*R
            RplK_1rK = Rpl**(Ki+1.0)/R**Ki
            RplK_KrK = Rpl**(Nfir+Ki)/R**Ki-R**Nfir
            primaparte = RplK_1rK*pocp*math.sin(fi)+pocr*(1.0-2.0*ni)*(RplK_1rK-R)
            secondaparte = (1.0+Nfir*Ki-ni*(Ki+1)*(Nfir+1.0))*pi_c_tan
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
        #return self.LDP_Panet_1995(x)
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
        

