import os
import ivi
# import vxi11

scope = ivi.lecroy.lecroyWR104XIA("TCPIP0::146.136.35.134::INSTR")

#scope.utility.reset()

channels = ["C1", "C2", "C3", "C4"]

def print_summary(chan):
    print("------- ", chan, " -------")
    print("Enabled =", scope.channels[chan].enabled)
    print("Label =", scope.channels[chan].label)
    print("Label position =", scope.channels[chan].label_position)
    print("Coupling =", scope.channels[chan].coupling)
    print("Impedance =", scope.channels[chan].input_impedance)
    print("Invert =", scope.channels[chan].invert)
    print("Noise filter =", scope.channels[chan].noise_filter)
    print("Bandwidth Limit =", scope.channels[chan].bw_limit)
    print("Interpolation =", scope.channels[chan].interpolation)
    print("Probe attenuation =", scope.channels[chan].probe_attenuation)
    print("Probe skew =", scope.channels[chan].probe_skew)

def set_defaults(chan):
    scope.channels[chan].enabled = True
    scope.channels[chan].label = chan
    scope.channels[chan].label_position = 0
    scope.channels[chan].coupling = "dc"
    scope.channels[chan].input_impedance = 1000000
    scope.channels[chan].invert = False
    scope.channels[chan].noise_filter = "1bits"
    scope.channels[chan].bw_limit = "ON"
    scope.channels[chan].interpolation = "Linear"
    #scope.channels[chan].probe_attenuation = 10
    scope.channels[chan].probe_skew = 0.0


scope.acquisition.time_per_record = 100e-7
#scope.measurement.auto_setup()
#scope.measurement.auto_setup()
#scope.memory.save(1)
#scope.memory.recall(1)

print("------- Scope Settings -------")
print("Record Length =", scope.acquisition.record_length)
print("Time per record =", scope.acquisition.time_per_record)




for chan in channels:
    set_defaults(chan)
    print_summary(chan)


# Write image from screen
img = scope.display.fetch_screenshot()
with open('TEST.png', 'wb') as f:
    f.write(img)

# Test triggers

trig_chan = "C1"

print("------- Trigger -------")
print(scope.trigger.source)
print(scope.trigger.type)
print(scope.trigger.mode)
print(scope.channels[trig_chan].trigger_level)

scope.trigger.source = trig_chan
scope.trigger.type = "EDgE"
scope.trigger.mode = "single"
scope.channels[trig_chan].trigger_level = "15"

print("------- Trigger -------")
print(scope.trigger.source)
print(scope.trigger.type)
print(scope.trigger.mode)
print(scope.channels[trig_chan].trigger_level)


# Test reading waveform data from scope

scope.channels['C1'].measurement.fetch_waveform()