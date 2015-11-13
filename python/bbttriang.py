import numpy as np
import matplotlib.pyplot as plt
from tbmkpi import FrictionCoeff
from bbtutils import bbtConfig
fig, ax = plt.subplots(1, 1)

#LEGGO I PARAMETRI DA FILE DI CONFIGURAZIONE
fCShiledMin = bbtConfig.getfloat('Alignment','frictionCShiledMin')
fCShiledMode = bbtConfig.getfloat('Alignment','frictionCShiledMode')
fCShiledMax = bbtConfig.getfloat('Alignment','frictionCShiledMax')
#CREO OGGETTO
fcShield = FrictionCoeff(fCShiledMin,fCShiledMode,fCShiledMax)

#LEGGO I PARAMETRI DA FILE DI CONFIGURAZIONE
fCCutterdMin = bbtConfig.getfloat('Alignment','frictionCCutterMin')
fCCutterMode = bbtConfig.getfloat('Alignment','frictionCCutterMode')
fCCutterMax = bbtConfig.getfloat('Alignment','frictionCCutterMax')
#CREO OGGETTO
fcCutter =  FrictionCoeff(fCCutterdMin,fCCutterMode,fCCutterMax)

# Mostro Output
si = np.zeros(shape=(1000,), dtype=float)
ci = np.zeros(shape=(1000,), dtype=float)
for i in range(1000):
    si[i] = fcShield.rvs()
    ci[i] = fcCutter.rvs()

ax.hist(si,bins=100,label="On Shiled")
ax.hist(ci,bins=100,label="On Cutter Head")
ax.legend(loc='best', frameon=False)
plt.show()
