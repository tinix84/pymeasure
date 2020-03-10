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