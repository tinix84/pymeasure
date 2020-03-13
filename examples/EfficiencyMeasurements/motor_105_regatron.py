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

import numpy as np
import pandas as pd
# import pprint
from time import sleep

import os
import sys, time, msvcrt

askuser_timeout = 3

# sys.path.append('D:/GitHub/pymeasure')

from pymeasure.instruments.agilent import Agilent34465A, Agilent34970A
# from pymeasure.virtual.thermometer import Thermometer
from pymeasure.virtual.motor import HSM_BMWi3, ASM_EZW1, SSM_ZOE
# from pymeasure.instruments.chroma import Chroma62024p6008
from pymeasure.instruments.regatron import Regatron
from pymeasure.instruments.lecroy import WaveRunner606Zi

eps = np.spacing(1)

def close_all_visa_resources():
    import visa
    rm = visa.ResourceManager()
    rm.close()
    rm.list_resources()

def calc_power(current: float, voltage: float):
    power = voltage*current
    return power

def calc_loss_power(input_power: float, ouput_power: float):
    loss_power = input_power-ouput_power
    return loss_power

def derating_current_point(Vcurr: float, Pcurr: float, Vmax: float, Imax: float, Pmax: float):
    # applying current and voltage derating to power
    Inew = np.minimum(Imax, Pcurr / (Vcurr+eps))
    Pnew = Vcurr * Inew
    return Inew, Pnew

def measurements_pts():
    pass

def timeStamped(fname: str, fmt='%Y%m%d%H%M%S{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

def getFilenamePrintScreen(set_input_voltage, set_output_power, set_duty, set_fsw):
    filename = ('%sVin%d_Po%.2e_D%.2f_fsw%.1fk' % (timeStamped('_'),
                set_input_voltage,
                set_output_power,
                set_duty,
                set_fsw/1000))
    return filename

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

def print_preset_value(psu:Regatron):
    print('VQ1[V] = %f' % psu.getVoltagePreset())
    print('IQ1[A] = %f' % psu.getCurrentPreset())
    print('IQ4[A]  = %f' % psu.getCurrentLimitQ4())
    print('PQ1[kW] = %f' % psu.getPowerPreset())
    print('PQ4[kW]  = %f' % psu.getPowerLimitQ4())


def run(input_data: dict):
    min_input_voltage = input_data.min_output_voltage * input_data.D_set
    step_input_voltage = input_data.output_voltage_step * input_data.D_set

    #max_output_current = max_output_power/min_output_voltage

    max_input_voltage = input_data.max_output_voltage * input_data.D_set
    max_input_power = input_data.max_output_power + input_data.worstcase_losses
    max_input_current = max_input_power / min_input_voltage
    max_input_power = input_data.max_output_power + input_data.worstcase_losses

    if max_input_voltage > 470:
        max_input_voltage = 470

    if max_input_current > 80:
        max_input_current = 80

    if max_input_power > 32e3:
        max_input_power = 32e3

#    delay = .1
#
#    DATA_COLUMNS = ['DateTime',
#                    'Modulation',
#                    'fs_set(Hz)',
#                    'D_set(-)',
#                    'Vin_set',
#                    'Pout_set',
#                    # INPUT MEASUREMENTS
#                    'SourceInputVoltage(V)',
#                    'DMMInputVoltage(V)',
#                    'SourceInputCurrent(A)',
#                    'SourceInputPower(A)',
#                    # OUTPUT MEASUREMENTS
#                    'SinkOutputVoltage(V)',
#                    'DMMOutputVoltage(V)',
#                    'SinkOutputCurrent(A)',
#                    'SinkOutputPower(A)',
#                    # OSCILLOSCOPE MEASUREMENTS
#                    'fs_meas(Hz)',
#                    'Duty100(-)']
#    data = pd.DataFrame(columns=DATA_COLUMNS)

    data =  pd.DataFrame()

    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    print('================================')
    print("Setting up instruments")
    logging.info("Setting up instruments")

    com_port_source = 'COM13'
    com_port_sink = 'COM7'

    source = Regatron(com_port_source)
    source.open()
    print(source.getSerialNumber())
    sink = Regatron(com_port_sink)
    sink.open()
    print(sink.getSerialNumber())

    # # DSO 10GHz BW
    # scope = WaveRunner606Zi('146.136.35.172')
    # # Waverunner 3024
    # scope = WaveRunner606Zi('146.136.35.170')
    # # Waverunner 8104-MS
    # scope = WaveRunner606Zi('146.136.35.134')
    # Waverunner 625Zi
    scope = WaveRunner606Zi('146.136.35.172')
    print(scope.id)
    dmm_vin = Agilent34465A('TCPIP0::146.136.35.174::inst0::INSTR')
    print(dmm_vin.id)
    dmm_vout = Agilent34465A('TCPIP0::146.136.35.176::inst0::INSTR')
    print(dmm_vout.id)
    # thermo = Thermometer(Agilent34970A('ASRL1::INSTR'))
    # print(thermo.id())
    

    source.powerOff()
    source.setVoltage(voltage=0)
    source.setCurrent(neg=0, pos=max_input_current)
    source.setPower(neg=0, pos=max_input_power)
    print('==SOURCE INIT==============================')
    print_preset_value(source)

    sink.powerOff()
    sink.setVoltage(voltage=20)
    sink.setCurrent(neg=-0, pos=0)
    sink.setPower(neg=-max_input_power, pos=0)
    print('==SINK INIT==============================')
    print_preset_value(sink)

    input_voltages = np.linspace(min_input_voltage, max_input_voltage,
                                 np.ceil((max_input_voltage - min_input_voltage) / step_input_voltage))
    output_powers = np.arange(input_data.min_output_power, input_data.max_output_power * 1.05,
                              input_data.step_output_power)
    input_voltages_rev = np.flip(input_voltages, axis=0)
    output_powers_rev = np.flip(output_powers, axis=0)

    loop_v = np.zeros((1, 2))

    # build startup voltage ramp
    startup_input_voltages = np.arange(step_input_voltage, max_input_voltage, step_input_voltage)
    for ii, voltage in enumerate(startup_input_voltages):
        loop_v = np.vstack((loop_v, [voltage, 0]))

    # build loops voltage/power
    direction = 1
    for ii, voltage in enumerate(input_voltages_rev):
        direction = (direction + 1) % 2
        for jj, power in enumerate(output_powers):
            if direction == 0:
                loop_v = np.vstack((loop_v, [voltage, output_powers[jj]]))
            elif direction == 1:
                loop_v = np.vstack((loop_v, [voltage, output_powers_rev[jj]]))

    input_powers = loop_v[:, 1] + input_data.worstcase_losses
    input_currents = input_powers / (loop_v[:, 0] + eps)
    output_voltages = loop_v[:, 0] / input_data.D_set

    print('==LOOPS OVERVIEW==============================')
    print('min input voltage: %f' % min_input_voltage)
    print('max input voltage: %f' % max_input_voltage)
    print('loop iterations:')
    print('¦¦ Input Voltage ¦¦ Output power ¦¦')
    print(loop_v)

    if ask_user():

        logging.info("Starting to sweep through voltages and powers")
        source_input_voltage = 0
        source_input_current = 0

        sink_output_voltage = 0
        sink_output_current = 0

        for row in loop_v:
            set_output_power = row[1]
            set_input_voltage = row[0]

            print('\n==NEXT STEP===============================')
            # logging.info('Next load power: %f' % set_output_power)
            print('Next input voltage: %f' % set_input_voltage)
            print('Next output voltage: %f' % (set_input_voltage / input_data.D_set))
            print('Next load power: %f' % set_output_power)
            set_output_current = -float(set_output_power / (set_input_voltage + eps) * input_data.D_set)
            print('Next load current: %f' % set_output_current)

            # logging.info('Next voltage step: %f' % set_input_voltage)

            if ask_user_timeout():
                source.powerOn()
                sink.powerOn()
                try:
                    source.setVoltage(voltage=set_input_voltage)
                    sleep(2)
                    #set_output_current = -1
                    sink.setCurrent(neg=set_output_current, pos=0)
                    sleep(2)
                    print('\n==SOURCE READOUT==============================')
                    print_preset_value(source)

                    print('\n==SINK READOUT==============================')
                    print_preset_value(sink)

                except:
                    source.powerOff()
                    sink.powerOff()

                try:
                    source_input_voltage = source.getTerminalVoltage()
                    source_input_current = source.getTerminalCurrent()
                    source_input_power = source.getTerminalPower() * 1000

                    sink_output_voltage = sink.getTerminalVoltage()
                    sink_output_current = sink.getTerminalCurrent()
                    sink_output_power = sink.getTerminalPower() * 1000

                    meas_input_voltage = dmm_vin.voltage_dc
                    meas_output_voltage = dmm_vout.voltage_dc
                except:
                    print('error occurred at Vin=%f, Pout=%f' % (set_input_voltage, set_output_power))
                    source.powerOff()
                    sink.powerOff()


                try:
                    # if waverunner the frequency and duty are measur. Nr1-2
                    # input_current_ph = np.nan #float(scope.get_measurement_Px(3))
                    # switching_freq = float(scope.get_measurement_Px(2))
                    # duty_boost = float(scope.get_measurement_Px(1))
                    # if DSO the frequency and duty are measur. Nr7-8

                    switching_freq = float(scope.get_measurement_Px(8))
                    duty_boost = float(scope.get_measurement_Px(7))
                except:
                    switching_freq = None
                    duty_boost = None

                scope.save_screen_to_file(filename=getFilenamePrintScreen(set_input_voltage,
                                                                            set_output_power,
                                                                            input_data.D_set,
                                                                            input_data.fsw_set))
            else:
                print('\n================================')
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

                data.to_csv(timeStamped('_') + '.csv')

                return 0


            # sleep(2)

            if abs(source_input_current) <= 1e-10:
                input_resistance = np.nan
            else:
                input_resistance = meas_input_voltage / source_input_current

            print('\n== ACTUAL STEP ===============================')
            print('Vin_meas = %f' % meas_input_voltage)
            print('Iin_meas = %f' % source_input_current)
            print('Vout_meas = %f' % meas_output_voltage)
            print('Iout_meas = %f' % sink_output_current)
            # print('Rin = %f' %input_resistance)
            Pin = (source_input_voltage * source_input_current)
            # print('Pin_calc = %f' % Pin)
            print('Pin_meas = %f' % source_input_power)
            Pout = (sink_output_voltage * sink_output_current)
            # print('Pout_calc = %f' % Pout)
            print('Pout_meas = %f' % sink_output_power)
            Ploss = Pin + Pout
            print('Ploss = %f' % Ploss)
            # Rloss=source_input_voltage**2/(Ploss+eps)
            # print('Rloss = %f' % Rloss)

            data_dict = {
                'DateTime': timeStamped('_'),
                'Modulation': input_data.modulation,
                'fs_set(Hz)': input_data.fsw_set,
                'D_set(-)': input_data.D_set,
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

            # pprint.pprint(data_dict, depth=1, width=60)
            # temp_lst=thermo.get_all_temperatures()
            # print(dict(temp_lst))
            
            df2 = pd.DataFrame([data_dict], columns=data_dict.keys())
            # df_temp = pd.DataFrame([dict(temp_lst)])
            # foo=pd.concat([df2, df_temp], axis=1, ignore_index=False)
            foo=pd.concat([df2], axis=1, ignore_index=False)

            data = pd.concat([data, foo], axis=0, ignore_index=True)
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
        # thermo.close()

        data.to_csv(timeStamped('_') + '.csv')

    return -1


if __name__ == "__main__":

    input_data=SSM_ZOE()
    # Set the input parameters
    input_data.modulation = 'CCM_Y2VW'  # YUVW configuration 1=enable
    # os.system("python .\hwrcommunication.py setFrequency 15")
    input_data.D_set = .5
    input_data.fsw_set = 25e3

    # dsp = Microcontroller()
    # dsp.set_duty(duty=input_data.D_set)
    # dsp.set_switching_frequency(input_data.fsw_set)
    # dsp.set_UV2W()

    input_data.worstcase_losses = 8000
    input_data.max_output_voltage = 200
    input_data.output_voltage_step = 50
    # max_output_voltage_step = 50

    input_data.max_output_power = 0
    input_data.min_output_power = 0
    input_data.step_output_power = 500

    run(input_data)
