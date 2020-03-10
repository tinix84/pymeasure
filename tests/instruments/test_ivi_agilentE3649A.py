# import Python IVI
import ivi
# connect to E3649A via GPIB
#psu = ivi.agilent.agilentE3649A("GPIB0::5::INSTR")
# connect to E3649A via E2050A GPIB to VXI11 bridge
psu = ivi.agilent.agilentE3649A("TCPIP0::192.168.1.105::gpib,5::INSTR")
# connect to E3649A via serial
#psu = ivi.agilent.agilentE3649A("ASRL::/dev/ttyUSB0,9600::INSTR")
# configure output
psu.outputs[0].configure_range('voltage', 12)
psu.outputs[0].voltage_level = 12.0
psu.outputs[0].current_limit = 1.0
psu.outputs[0].ovp_limit = 14.0
psu.outputs[0].ovp_enabled = True
psu.outputs[0].enabled = True