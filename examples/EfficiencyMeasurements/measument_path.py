import numpy as np 

class Specifications():
    """Specification class for 2 ports device"""
    def __init__(self):
        self.nominal_voltage = [0, 0]
        self.minimum_voltage = [0, 0]
        self.maximum_voltage = [0, 0]
        self.ripple_voltage = [0, 0]
        self.ripple_voltage = [0, 0]
        self.nominal_power = [0, 0]
        self.minimum_power = [0, 0]
        self.maximum_power = [0, 0]
        self._points_voltage = 3
        self._voltages = self.voltages()

    @voltages.setter
    def voltages(self):
        if self._points_voltage == 3:
            self._voltages = np.vstack(self.minimum_voltage, self.nominal_voltage, self.maximum_voltage) 
        elif self._points_voltage > 3:
            

def generate_measurement_path():
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