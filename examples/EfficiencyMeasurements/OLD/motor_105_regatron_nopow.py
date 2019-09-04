"""
This example demonstrates how to make a graphical interface to preform
IV characteristic measurements. There are a two items that need to be 
changed for your system:

1) Correct the GPIB addresses in IVProcedure.startup for your instruments
2) Correct the directory to save files in MainWindow.queue

Run the program by changing to the directory containing this file and calling:

python iv_keithley.py

"""

import logging
import datetime

import sys
import numpy as np
import pandas as pd
import pprint
from time import sleep

import os
sys.path.append('D:/GitHub/rrr/pymeasure')

from pymeasure.instruments.agilent import Agilent34461A, Agilent34465A
from pymeasure.instruments.chroma import Chroma62024p6008
from pymeasure.instruments.regatron import Regatron
from pymeasure.instruments.lecroy import WaveRunner606Zi

def timeStamped(fname, fmt='%Y%m%d%H%M%S{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname = fname)

def ask_user():
    check = str(input("Continue ? ([y]/n): ")).lower().strip()
    try:
        if check[:1] == 'y':
            return True
        elif check[:1] == 'n':
            return False
        elif check[:1] == '':
            return True
        else:
            print('Invalid Input')
            return ask_user()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return ask_user()


def run():
    log_directory = 'D:\\HardCopy\\'

    # Set the input parameters
    D_set=.75
    fsw_set=25e3
    worst_case_efficiency = 0.1

    max_output_voltage = 800
    min_output_voltage = 100
    output_voltage_step = 50
    
    max_output_power = 100
    min_output_power = 0
    step_output_power = 50
    
    min_input_voltage = min_output_voltage*D_set
    step_input_voltage = output_voltage_step*D_set
    
    max_output_current = max_output_power/min_output_voltage
    
    max_input_voltage = max_output_voltage*D_set
    max_input_current = max_output_power/min_input_voltage/worst_case_efficiency
    max_input_power = max_output_power/worst_case_efficiency

    if max_input_voltage > 450:
        max_input_voltage = 450

    if max_input_current > 80:
        max_input_current = 80

    if max_input_power > 32e3:
        max_input_power = 32e3

    delay = .1 

    DATA_COLUMNS = ['DateTime',
                    'fs_set(Hz)',
                    'D_set(-)',
                    'SourceInputVoltage(V)',
                    'DMMInputVoltage(V)',
                    'SourceInputCurrent(A)',
                    
                    'SinkOutputVoltage(V)',
                    'DMMOutputVoltage(V)',
                    'SinkOutputCurrent(A)',
                    
                    'fs_meas(Hz)',
                    'Duty100(-)']

    data = pd.DataFrame(columns=DATA_COLUMNS)

    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    print('================================')
    print("Setting up instruments")
    logging.info("Setting up instruments")

    com_port_source = 'COM7'
    com_port_sink = 'COM6'
    
    source = Regatron(com_port_source)
    source.open()
    print(source._serial) 
    sink = Regatron(com_port_sink)
    sink.open()
    print(sink._serial)
      
    scope = WaveRunner606Zi('146.136.35.208')
    print(scope.id)
    dmm_vin = Agilent34465A('TCPIP0::146.136.35.174::inst0::INSTR')
    print(dmm_vin.id)
    dmm_vout = Agilent34465A('TCPIP0::146.136.35.176::inst0::INSTR')
    print(dmm_vout.id)

    source.powerOff()
    source.setVoltage(voltage=0)
    source.setCurrent(neg=0, pos=max_input_current)
    source.setPower(neg=0, pos=max_input_power)
    
    print('VQ1_source = %f' % source.getVoltagePreset())
    print('IQ1_source = %f' % source.getCurrentPreset())
    print('IQ4_source  = %f' % source.getCurrentLimitQ4())
    print('PQ1_source = %f' % source.getPowerPreset())
    print('PQ4_source  = %f' % source.getPowerLimitQ4())
    
    sink.powerOff()
    sink.setVoltage(voltage=1)
    sink.setCurrent(neg=-max_output_current, pos=0)
    sink.setPower(neg=0, pos=0)
    
    print('VQ1_sink = %f' % sink.getVoltagePreset())
    print('IQ1_sink = %f' % sink.getCurrentPreset())
    print('IQ4_sink  = %f' % sink.getCurrentLimitQ4())
    print('PQ1_sink = %f' % sink.getPowerPreset())
    print('PQ4_sink  = %f' % sink.getPowerLimitQ4())
    
    source.powerOn()
    source.setVoltage(voltage=min_input_voltage)
    sleep(1)
    print('Vdlink = %f' % dmm_vout.voltage_dc)
    print('dmm_vin = %f' % dmm_vin.voltage_dc)
    

    input_voltages = np.arange(min_input_voltage, max_input_voltage+step_input_voltage, step_input_voltage)
    #input_voltages_loop = np.concatenate(input_voltages, np.fliplr(input_voltages))
    output_powers = np.arange(min_output_power, max_output_power+step_output_power, step_output_power)
    #output_powers_loop = np.tile(output_powers, np.size(input_voltages))
    print(input_voltages)
    print(output_powers)
    # steps = len(voltages)

    print('================================')
    print("Starting to sweep through voltage")
    print('min input voltage: %f' % min_input_voltage)
    print('max input voltage: %f' % max_input_voltage)  
    
    logging.info("Starting to sweep through voltages and powers")
    
#    for j, power in enumerate(output_powers):
#    
#        print('================================')
#        print('Next load power: %f' % power)
#        logging.info('Next load power: %f' % power)
#    
#        sink.setPower(neg=-power, pos=0)
#        sink.powerOn()
    
    for i, voltage in enumerate(input_voltages):
        
        print('================================')
        print('Next input voltage: %f' % voltage)
        print('Expected output voltage: %f' % (voltage/D_set))
        logging.info('Next voltage step: %f' % voltage)   
        
        try:
            source.setVoltage(voltage=voltage)
            # Or use source.ramp_to_current(current, delay=0.1)
            sleep(2)
        except:
            source.powerOff()                 
    
        if ask_user() == True:
    
            try:
                source_input_voltage = source.getTerminalVoltage()
                source_input_current = source.getTerminalCurrent()
                
                sink_output_voltage = sink.getTerminalVoltage()
                sink_output_current = sink.getTerminalCurrent()
                
                meas_input_voltage = dmm_vin.voltage_dc
                meas_output_voltage = dmm_vout.voltage_dc
                
                switching_freq = float(scope.get_measurement_Px(8))
                duty_boost = float(scope.get_measurement_Px(7))
#                input_current_ph = np.nan #float(scope.get_measurement_Px(3))
                
            except:
                
                meas_input_voltage = dmm_vin.voltage_dc
                meas_output_voltage = dmm_vout.voltage_dc
                
                switching_freq = float(scope.get_measurement_Px(8))
                duty_boost = float(scope.get_measurement_Px(7))
        else:
            print('================================')
            print('Finishing') 
            scope.disconnect()
            
            source.setVoltage(voltage=0)
            sleep(1)
            source.powerOff()
            source.close()
            sink.setCurrent(neg=0, pos=0)
            sleep(1)
            sink.powerOff()
            sink.close()
            
            data.to_csv(timeStamped('_')+'.csv')
            
            return 0

        # filename_prtscr=(' foo.tif')
        #filename_prtscr = log_directory + time_filename
        scope.print_screen_autoname()
        #sleep(2)

        if abs(source_input_current) <= 1e-10:
            input_resistance = np.nan
        else:
            input_resistance = meas_input_voltage / source_input_current
            
        print('================================')
        print('Rin = %f' %input_resistance)
        Pin=(source_input_voltage*source_input_current)
        print('Pin = %f' % Pin)
        Pout=(sink_output_voltage*sink_output_current)
        print('Pout = %f' % Pout)
        Ploss=Pin-Pout
        print('Ploss = %f' % Ploss)
        Rloss=source_input_voltage**2/Ploss
        print('Rloss = %f' % Rloss)
        
        data_dict = { 
            'DateTime': timeStamped('_'),
            'fs_set(Hz)': fsw_set,
            'D_set(-)': D_set,
            
            'SourceInputVoltage(V)': source_input_voltage,
            'DMMInputVoltage(V)': meas_input_voltage,
            'SourceInputCurrent(A)': source_input_current,
            
            'SinkOutputVoltage(V)': sink_output_voltage,
            'DMMOutputVoltage(V)': meas_output_voltage,
            'SinkOutputCurrent(A)': sink_output_current,
            
            'fs_meas(Hz)': switching_freq,
            'Duty100(-)': duty_boost}

        pprint.pprint(data_dict, depth=1, width=60)

        df2 = pd.DataFrame([data_dict], columns=data_dict.keys())
        data = pd.concat([data, df2], axis=0, ignore_index=True)
        data.to_csv('temp.csv')
            
    print('================================')
    print('Finishing')     
    
    scope.disconnect() 
    
    source.setVoltage(voltage=0)
    sleep(1)
    source.powerOff()
    source.close()
    sink.setCurrent(neg=0, pos=0)
    sleep(1)
    sink.powerOff()
    sink.close()
    
    data.to_csv(timeStamped('_')+'.csv')
        
    return -1

if __name__ == "__main__":
    run()