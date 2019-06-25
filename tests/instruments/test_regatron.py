from pymeasure.instruments.regatron.regatron import Regatron
from time import sleep

# execute only if run as a script
com_port_source = 'COM7'
com_port_sink = 'COM6'
psu_source = Regatron(com_port_source)
psu_sink = Regatron(com_port_sink)

print("configure source")
psu_source.open()
print(psu_source._serial)
print(psu_source._fw)
print(psu_source.getSystemVoltageRange())
print(psu_source.getSystemCurrentRange())
print(psu_source.getSystemPowerRange())

psu_source.setVoltage(voltage=0)
print(psu_source.getVoltagePreset())
psu_source.setVoltage(voltage=10)
print(psu_source.getVoltagePreset())

print(psu_source.getCurrentPreset())
print(psu_source.getCurrentLimitQ4())
psu_source.setCurrent(neg=-2, pos=2)
print(psu_source.getCurrentPreset())
print(psu_source.getCurrentLimitQ4())
psu_source.setCurrent(neg=-1, pos=10)
print(psu_source.getCurrentPreset())
print(psu_source.getCurrentLimitQ4())

print(psu_source.getPowerPreset())
print(psu_source.getPowerLimitQ4())
psu_source.setPower(neg=-2, pos=2)
print(psu_source.getPowerPreset())
print(psu_source.getPowerLimitQ4())
psu_source.setPower(neg=-1, pos=10)
print(psu_source.getPowerPreset())
print(psu_source.getPowerLimitQ4())

psu_source.powerOn()
sleep(3)
print(psu_source.getTerminalVoltage())
sleep(3)
print(psu_source.getTerminalCurrent())
print(psu_source.getTerminalPower())


print("configure sink")
psu_sink.open()
print(psu_sink._serial)
print(psu_sink._fw)
print(psu_sink.getSystemVoltageRange())
print(psu_sink.getSystemCurrentRange())
print(psu_sink.getSystemPowerRange())

psu_sink.selectUnit(0)
psu_sink.setVoltage(voltage=0)
print(psu_sink.getVoltagePreset())
psu_sink.setVoltage(voltage=10)
print(psu_sink.getVoltagePreset())

print(psu_sink.getCurrentPreset())
print(psu_sink.getCurrentLimitQ4())
psu_sink.setCurrent(neg=-2, pos=2)
print(psu_sink.getCurrentPreset())
print(psu_sink.getCurrentLimitQ4())
psu_sink.setCurrent(neg=-1, pos=10)
print(psu_sink.getCurrentPreset())
print(psu_sink.getCurrentLimitQ4())

print(psu_sink.getPowerPreset())
print(psu_sink.getPowerLimitQ4())
psu_sink.setPower(neg=-2, pos=2)
print(psu_sink.getPowerPreset())
print(psu_sink.getPowerLimitQ4())
psu_sink.setPower(neg=-1, pos=10)
print(psu_sink.getPowerPreset())
print(psu_sink.getPowerLimitQ4())

print(psu_sink.getTerminalVoltage())
print(psu_sink.getTerminalCurrent())
print(psu_sink.getTerminalPower())


psu_source.powerOff()

psu_source.close()
psu_sink.close()