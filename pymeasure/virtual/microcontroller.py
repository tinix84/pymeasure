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