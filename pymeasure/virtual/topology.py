class Topology():
    def __init__(self):
        self.input_voltage_range = np.array([0.0, 0.0])
        self.input_current_range = np.array([0.0, 0.0])
        self.input_power_range = np.array([0.0, 0.0])
        self.output_voltage_range = np.array([0.0, 0.0])
        self.output_current_range = np.array([0.0, 0.0])
        self.output_power_range = np.array([0.0, 0.0])
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
