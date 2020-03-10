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
        self.dut = s['powertrain']
        self.load = s['load']