import visa
rm = visa.ResourceManager()
print(rm.list_resources())

inst = rm.open_resource('ASRL1::INSTR')
print(inst.query("*IDN?"))

# inst = rm.open_resource('TCPIP0::146.136.35.247::inst0::INSTR')
# print(inst.query("*IDN?"))

# inst = rm.open_resource('TCPIP0::146.136.35.210::inst0::INSTR')
# print(inst.query("*IDN?"))
