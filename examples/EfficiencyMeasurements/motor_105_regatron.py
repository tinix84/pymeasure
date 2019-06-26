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
import sys, time, msvcrt
askuser_timeout = 3

sys.path.append('D:/GitHub/rrr/pymeasure')

from pymeasure.instruments.agilent import Agilent34461A, Agilent34465A
from pymeasure.instruments.chroma import Chroma62024p6008
from pymeasure.instruments.regatron import Regatron
from pymeasure.instruments.lecroy import WaveRunner606Zi

eps=np.spacing(1)

def timeStamped(fname, fmt='%Y%m%d%H%M%S{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname = fname)

def ask_user():
    print('================================')
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

def ask_user_timeout():
    startTime = time.time()
    inp = None
    print('\n================================')
    print("Press any key to stop or wait x seconds...")
    while True:
        if msvcrt.kbhit():
            inp = msvcrt.getch()
            break
        elif time.time() - startTime > askuser_timeout:
            break
    if inp:
        print("Stopping...")
        return False
    else:
        print("Timed out and go on...")
        return True

def run():
    log_directory = 'D:\\HardCopy\\'

    # Set the input parameters
    modulation = '111' #UVW configuration 1=enable
    D_set=.60
    fsw_set=55e3
    worstcase_losses = 4000

    max_output_voltage = 650
    min_output_voltage = 400
    output_voltage_step = 100
    max_output_voltage_step = 50
    
    max_output_power = 22000
    min_output_power = 200
    step_output_power = 750
    
    min_input_voltage = min_output_voltage*D_set
    step_input_voltage = output_voltage_step*D_set
    
    max_output_current = max_output_power/min_output_voltage
    
    max_input_voltage = max_output_voltage*D_set
    max_input_power = max_output_power+worstcase_losses
    max_input_current = max_input_power/min_input_voltage
    max_input_power = max_output_power+worstcase_losses

    if max_input_voltage > 470:
        max_input_voltage = 470

    if max_input_current > 80:
        max_input_current = 80

    max_output_current = max_input_current

    if max_input_power > 32e3:
        max_input_power = 32e3

    delay = .1 

    DATA_COLUMNS = ['DateTime',
                    'Modulation',
                    'fs_set(Hz)',
                    'D_set(-)',
                    'Vin_set',
                    'Pout_set',  
                    # INPUT MEASUREMENTS
                    'SourceInputVoltage(V)',
                    'DMMInputVoltage(V)',
                    'SourceInputCurrent(A)',
                    'SourceInputPower(A)',
                    # OUTPUT MEASUREMENTS
                    'SinkOutputVoltage(V)',
                    'DMMOutputVoltage(V)',
                    'SinkOutputCurrent(A)',
                    'SinkOutputPower(A)',
                    # OSCILLOSCOPE MEASUREMENTS
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
    print('==SOURCE INIT==============================')
    print('VQ1_source[V] = %f' % source.getVoltagePreset())
    print('IQ1_source[A] = %f' % source.getCurrentPreset())
    print('IQ4_source[A]  = %f' % source.getCurrentLimitQ4())
    print('PQ1_source[kW] = %f' % source.getPowerPreset())
    print('PQ4_source[kW]  = %f' % source.getPowerLimitQ4())
    
    sink.powerOff()
    sink.setVoltage(voltage=20)
    sink.setCurrent(neg=-0, pos=0)
    sink.setPower(neg=-max_input_power, pos=0)
    print('==SINK INIT==============================')
    print('VQ1_sink[V] = %f' % sink.getVoltagePreset())
    print('IQ1_sink[A] = %f' % sink.getCurrentPreset())
    print('IQ4_sink[A]  = %f' % sink.getCurrentLimitQ4())
    print('PQ1_sink[kW] = %f' % sink.getPowerPreset())
    print('PQ4_sink[kW]  = %f' % sink.getPowerLimitQ4())
    

    input_voltages = np.linspace(min_input_voltage, max_input_voltage, np.ceil((max_input_voltage-min_input_voltage)/step_input_voltage))
    output_powers = np.arange(min_output_power, max_output_power*1.05, step_output_power)
    input_voltages_rev = np.flip(input_voltages, axis=0)
    output_powers_rev = np.flip(output_powers, axis=0)
  
    loop_v = np.zeros((1,2))
    # build startup voltage ramp
    startup_input_voltages = np.arange(step_input_voltage, max_input_voltage, step_input_voltage)
    for ii, voltage in enumerate(startup_input_voltages):
        loop_v=np.vstack((loop_v,[voltage, 0]))

    # build loops voltage/power
    direction = 1
    for ii, voltage in enumerate(input_voltages_rev):
        direction = (direction+1)%2
        for jj, power in enumerate(output_powers):
            if direction == 0:      
                loop_v=np.vstack((loop_v,[voltage, output_powers[jj]]))
            elif direction == 1:
                loop_v=np.vstack((loop_v,[voltage, output_powers_rev[jj]]))

    print('==LOOPS OVERVIEW==============================')
    print('min input voltage: %f' % min_input_voltage)
    print('max input voltage: %f' % max_input_voltage)  
    print('loop iterations:')
    print('¦¦ Input Voltage ¦¦ Output power ¦¦')
    print(loop_v)
    
    ask_user()

    logging.info("Starting to sweep through voltages and powers")
    source_input_voltage = 0
    source_input_current = 0
    
    sink_output_voltage = 0
    sink_output_current = 0
    set_output_power=(sink_output_voltage*sink_output_current)

    for row in loop_v:
        set_output_power = row[1]
        set_input_voltage = row[0]
            
        print('\n==NEXT STEP===============================')
        # logging.info('Next load power: %f' % set_output_power)
        print('Next input voltage: %f' % set_input_voltage)
        print('Next output voltage: %f' % (set_input_voltage/D_set))
        print('Next load power: %f' % set_output_power)
        set_output_current=-float(set_output_power/(set_input_voltage+eps)*D_set)
        print('Next load current: %f' % set_output_current)
        
        # logging.info('Next voltage step: %f' % set_input_voltage)                 
    
        if ask_user_timeout() == True:
            source.powerOn()
            sink.powerOn()
            try:
                #source.setCurrent(neg=0, pos=(set_output_power/(set_input_voltage+eps)/worst_case_efficiency+20))
                source.setVoltage(voltage=set_input_voltage) 
                # source.ramp_to_voltage(self, act_voltage=source_input_voltage, fin_voltage=set_input_voltage, max_voltage_step=max_output_voltag*D_set)
                # Or use source.ramp_to_current(current, delay=0.1)
                sleep(2)
                #set_output_current=-float(set_output_power/(set_input_voltage+eps))  
                #sink.setPower(neg=-float(set_output_power), pos=0)

                sink.setCurrent(neg=set_output_current, pos=0)
                sleep(2)
                print('\n==SOURCE READOUT==============================')
                print('VQ1_source[V] = %f' % source.getVoltagePreset())
                print('IQ1_source[A] = %f' % source.getCurrentPreset())
                print('IQ4_source[A]  = %f' % source.getCurrentLimitQ4())
                print('PQ1_source[kW] = %f' % source.getPowerPreset())
                print('PQ4_source[kW]  = %f' % source.getPowerLimitQ4())
                
                print('\n==SINK READOUT==============================')
                print('VQ1_sink[V] = %f' % sink.getVoltagePreset())
                print('IQ1_sink[A] = %f' % sink.getCurrentPreset())
                print('IQ4_sink[A]  = %f' % sink.getCurrentLimitQ4())
                print('PQ1_sink[kW] = %f' % sink.getPowerPreset())
                print('PQ4_sink[kW]  = %f' % sink.getPowerLimitQ4())                         

            except:
                source.powerOff() 
                sink.powerOff()  
    
            try:
                source_input_voltage = source.getTerminalVoltage()
                source_input_current = source.getTerminalCurrent()
                source_input_power = source.getTerminalPower()*1000

                sink_output_voltage = sink.getTerminalVoltage()
                sink_output_current = sink.getTerminalCurrent()
                sink_output_power = sink.getTerminalPower()*1000
                
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
            print('================================\n')
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
            
        print('\n== ACTUAL STEP ===============================')
        print('Vin_meas = %f' % meas_input_voltage)
        print('Iin_meas = %f' % source_input_current)
        print('Vout_meas = %f' % meas_output_voltage)
        print('Iout_meas = %f' % sink_output_current)
        #print('Rin = %f' %input_resistance)
        Pin=(source_input_voltage*source_input_current)
        #print('Pin_calc = %f' % Pin)
        print('Pin_meas = %f' % source_input_power)
        Pout=(sink_output_voltage*sink_output_current)
        #print('Pout_calc = %f' % Pout)
        print('Pout_meas = %f' % sink_output_power)
        Ploss=Pin+Pout
        print('Ploss = %f' % Ploss)
        #Rloss=source_input_voltage**2/(Ploss+eps)
        #print('Rloss = %f' % Rloss)
        
        data_dict = { 
            'DateTime': timeStamped('_'),
            'Modulation': modulation,
            'fs_set(Hz)': fsw_set,
            'D_set(-)': D_set,
            'Vin_set': set_input_voltage,
            'Pout_set': set_output_power,  

            'SourceInputVoltage(V)': source_input_voltage,
            'DMMInputVoltage(V)': meas_input_voltage,
            'SourceInputCurrent(A)': source_input_current,
            'SourceInputPower(A)': source_input_power,
            
            'SinkOutputVoltage(V)': sink_output_voltage,
            'DMMOutputVoltage(V)': meas_output_voltage,
            'SinkOutputCurrent(A)': sink_output_current,
            'SinkOutputPower(A)': sink_output_power,
            
            'fs_meas(Hz)': switching_freq,
            'Duty100(-)': duty_boost}

        #pprint.pprint(data_dict, depth=1, width=60)

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