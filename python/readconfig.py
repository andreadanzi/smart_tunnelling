import ConfigParser, os

path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
##########
sCFGName = 'bbt.cfg'
sCFGPath = os.path.join(os.path.abspath('..'),'resources', sCFGName)


config = ConfigParser.RawConfigParser()
config.read(sCFGPath)
power1 = config.get('TBM1', 'power')
torque1 = config.getfloat('TBM1', 'torque')
power2 = config.getint('TBM2', 'power')
print "TMB1.power = %s  torque=%f TMB2.power = %d " % (power1,torque1,power2)

print "\n#################\n"
for each_section in config.sections():
    print each_section
    print config.items(each_section)
    for (each_key, each_val) in config.items(each_section):
        print "%s=%f" % (each_key, float(each_val))
    print "\n########\n"
