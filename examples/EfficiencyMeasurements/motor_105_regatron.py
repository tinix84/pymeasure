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

from pymeasure.instruments.agilent import Agilent34461A, Agilent34465A
# from pymeasure.instruments.chroma import Chroma62024p6008
from pymeasure.instruments.regatron import Regatron
from pymeasure.instruments.lecroy import WaveRunner606Zi

eps = np.spacing(1)

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

    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    print('================================')
    print("Setting up instruments")
    logging.info("Setting up instruments")

    com_port_source = 'COM7'
    com_port_sink = 'COM6'

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
    # Waverunner 8104-MS
    scope = WaveRunner606Zi('146.136.35.134')
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

                    # if DSO the frequency and duty are measur. Nr7-8
                    switching_freq = float(scope.get_measurement_Px(8))
                    duty_boost = float(scope.get_measurement_Px(7))
                    scope.save_c2_trc()
                    scope.save_screen_to_file(filename=getFilenamePrintScreen(set_input_voltage,
                                                                                set_output_power,
                                                                                input_data.D_set,
                                                                                input_data.fsw_set))
                    # if waverunner the frequency and duty are measur. Nr1-2
                    # input_current_ph = np.nan #float(scope.get_measurement_Px(3))
                    # switching_freq = float(scope.get_measurement_Px(2))
                    # duty_boost = float(scope.get_measurement_Px(1))

                except:
                    print('error occurred at Vin=%f, Pout=%f' % (set_input_voltage, set_output_power))
                    # meas_input_voltage = dmm_vin.voltage_dc
                    # meas_output_voltage = dmm_vout.voltage_dc

                    # switching_freq = float(scope.get_measurement_Px(8))
                    # duty_boost = float(scope.get_measurement_Px(7))
                    # # switching_freq = float(scope.get_measurement_Px(2))
                    # # duty_boost = float(scope.get_measurement_Px(1))
                    source.powerOff()
                    sink.powerOff()
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

        data.to_csv(timeStamped('_') + '.csv')

    return -1

class Bias():

    def __init__(self, source, Vmeter, Imeter):
        try:
            self.supply = source # power supply object
            self.Vmtr = Vmeter # voltmeter object
            self.Imtr = Imeter # ammeter object
            pass
        except:
            print('BIAS: constructor failed\n\n')
            pass

    def setState(self, s):
        pass

    def getState(self):
        pass

class DCBias(Bias):

    def __init__(self, source, Vmeter, Imeter):
        try:
            self.supply = source #DC power supply object
            self.Vmtr = Vmeter #DC voltmeter object
            self.Imtr = Imeter #DC ammeter object
            pass
        except:
            print('BIAS: constructor failed\n\n')
            pass

    def getState(self):
        s=dict
        s['supply']=self.supply
        s['Vmtr']=self.Vmtr
        s['Imtr']=self.Imtr
        pass

class MotorData():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modulation = None
        self.D_set = None
        self.fsw_set = None
        self.worstcase_losses = None

        self.max_output_voltage = None
        self.min_output_voltage = None
        self.output_voltage_step = None

        self.max_output_power = None
        self.min_output_power = None
        self.step_output_power = None

class ASM_EZW1(MotorData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worstcase_losses = 8e3
        self.max_output_voltage = 800
        self.min_output_voltage = 20
        self.output_voltage_step = 50
        self.max_output_power = 100e3
        self.min_output_power = 0
        self.step_output_power = 750

class HSM_BMWi3(MotorData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worstcase_losses = 8e3
        self.max_output_voltage = 600
        self.min_output_voltage = 20
        self.output_voltage_step = 50
        self.max_output_power = 60e3
        self.min_output_power = 0
        self.step_output_power = 750


class Microcontroller():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the input parameters
        self.modulation = None  # YUVW configuration 1=enable
        # os.system("python .\hwrcommunication.py setFrequency 15")
        self.duty = None
        self.fsw = None
        self.cmd_path = "C:/Users/tinivella/workspace_v9/ILBST_CLA_voltage/hwrcommunication.py"
        pass

    def set_duty(self, duty):
        self.duty = duty
        cmd = (("python %s setDuty %d") % (self.cmd_path, self.duty*100))
        os.system(cmd)
        return cmd

    def set_switching_frequency(self, fsw):
        self.fsw = fsw
        cmd = (("python %s setFrequency %d") % (self.cmd_path, self.fsw/1e3))
        os.system(cmd)
        return cmd

    def set_V2W(self):
        self.modulation = '0011'  # YUVW configuration 1=enable
        cmd = (("python %s disableUHS") % (self.cmd_path))
        os.system(cmd)
        cmd = (("python %s disableULS") % (self.cmd_path))
        os.system(cmd)
        cmd = (("python %s enableVHS") % (self.cmd_path))
        os.system(cmd)
        cmd = (("python %s enableVLS") % (self.cmd_path))
        os.system(cmd)
        return cmd

    def set_UV2W(self):
        self.modulation = '0111'  # YUVW configuration 1=enable
        cmd = (("python %s enableUHS") % (self.cmd_path))
        os.system(cmd)
        cmd = (("python %s enableULS") % (self.cmd_path))
        os.system(cmd)
        cmd = (("python %s enableVHS") % (self.cmd_path))
        os.system(cmd)
        cmd = (("python %s enableVLS") % (self.cmd_path))
        os.system(cmd)
        return cmd

# class Tset():
#     source = DCBias()
#     load = DCLoad()
#     DUT = HSM_BMWi3()


class EfficiencyMeasurement():
    # input_voltage = None
    # input_current = None
    # output_voltage = None
    # output_current = None
    # input_power = None
    # output_power = None
    # loss_power = None
    # efficiency = None

    def __init__(self, input_voltage: float, input_current: float,
                        output_voltage: float, output_current: float):
        self.input_voltage = input_voltage
        self.input_current = input_current
        self.output_voltage = output_voltage
        self.output_current = output_current
        self.input_power = calc_power(voltage = input_voltage, current = input_current)
        self.output_power = calc_power(voltage = output_voltage, current = output_current)
        self.loss_power = calc_loss_power(input_power=self.input_power, ouput_power=self.output_power)

class TsetPoint():
    setup = None
    measurement = None #EfficiencyMeasurement()

class TestSet_Efficiency():
    def __init__(self, s: dict):
        self.source_bias = s['source_bias']
        self.powertrain = s['powertrain']
        self.load = s['load']

class Topology():
    def __init__(self):
        self.input_voltage_range = np.array([0.0 0.0])
        self.input_current_range = np.array([0.0 0.0])
        self.input_power_range = np.array([0.0 0.0])
        self.output_voltage_range = np.array([0.0 0.0])
        self.output_current_range = np.array([0.0 0.0])
        self.output_power_range = np.array([0.0 0.0])
        self.control = None
        self.power_train = None
        #measurement related
        self.output_voltage_step = None
        self.output_current_step = None
        self.output_power_step = None
        self.input_current_step = None
        self.input_voltage_step = None


def load_measurement_point():
    meas_map_file="C:/Users/tinivella/workspace_v9/pymeasure/examples/EfficiencyMeasurements/Book1.xlsx"
    measurement_map = pd.read_excel(meas_map_file,
                                    sheet_name=0,
                                    header=0,
                                    index_col=False,
                                    keep_default_na=True)
    print(measurement_map.head())

def calc_intermediate_pts(user_meas_pts):
    # To find the discrete difference row based
    df=user_meas_pts.diff(axis = 0, periods = 1)
    if df.fillna(0).astype(bool).sum(axis=1) > 1:
        raise Exception("2 elements changed in single step not allowed")



if __name__ == "__main__":

    input_data=HSM_BMWi3()
    # Set the input parameters
    input_data.modulation = '1110'  # YUVW configuration 1=enable
    # os.system("python .\hwrcommunication.py setFrequency 15")
    input_data.D_set = .55
    input_data.fsw_set = 25e3

    # dsp = Microcontroller()
    # dsp.set_duty(duty=input_data.D_set)
    # dsp.set_switching_frequency(input_data.fsw_set)
    # dsp.set_UV2W()

    input_data.worstcase_losses = 8000

    input_data.max_output_voltage = 780
    input_data.output_voltage_step = 50
    # max_output_voltage_step = 50

    input_data.max_output_power = 20000
    input_data.min_output_power = 0

    input_data.step_output_power = 500

    run(input_data)
