# import Python IVI
import ivi
# connect to scope
dmm = ivi.agilent.agilent34465A('TCPIP0::146.136.35.174::inst0::INSTR')
#scope = ivi.tektronix.tektronixMDO4104("TCPIP0::192.168.1.108::INSTR")
#scope = ivi.agilent.agilentMSO7104A("USB0::2391::5973::MY********::INSTR")
#scope = ivi.tektronix.tektronixMDO4104("USB0::1689::1036::C******::INSTR")
id=dmm.identity.instrument_manufacturer
print(id)
print(dmm.measurement_function)
# dmm.trigger.source = 'immediate'
# print(dmm.measurement.fetch(1.0))
print(dmm.measurement.read(1.0))