# import Python IVI
import ivi
# import numpy
from numpy import *
# connect to AWG2021 via GPIB
#awg = ivi.tektronix.tektronixAWG2021("GPIB0::25::INSTR")
# connect to AWG2021 via E2050A GPIB to VXI11 bridge
awg = ivi.tektronix.tektronixAWG2021("TCPIP0::192.168.1.105::gpib,25::INSTR")
# connect to AWG2021 via serial
#awg = ivi.tektronix.tektronixAWG2021("ASRL::/dev/ttyUSB0,9600::INSTR")
# create a waveform
n = 128
f = 1
a = 1
wfm = a*sin(2*pi/n*f*arange(0,n))
# transfer to AWG2021
awg.outputs[0].arbitrary.create_waveform(wfm)
# 2 volts peak to peak
awg.outputs[0].arbitrary.gain = 2.0
# zero offset
awg.outputs[0].arbitrary.offset = 0.0
# sample rate 128 MHz
arb.arbitrary.sample_rate = 128e6
# enable ouput
awg.outputs[0].enabled = True