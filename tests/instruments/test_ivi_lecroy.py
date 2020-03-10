# import Python IVI
import ivi
# connect to scope
scope1 = ivi.lecroy.lecroyWR104XIA('TCPIP0::146.136.35.134::inst0::INSTR')
#dmm = ivi.agilent.agilent34465A('TCPIP0::146.136.35.174::inst0::INSTR')
#scope = ivi.tektronix.tektronixMDO4104("TCPIP0::192.168.1.108::INSTR")
#scope = ivi.agilent.agilentMSO7104A("USB0::2391::5973::MY********::INSTR")
#scope = ivi.tektronix.tektronixMDO4104("USB0::1689::1036::C******::INSTR")
res = scope1.identity.description
scope1.channels[0].measurement.fetch_waveform_measurement('rise_time') #not working
scope1.channels[0].name
print(res)
