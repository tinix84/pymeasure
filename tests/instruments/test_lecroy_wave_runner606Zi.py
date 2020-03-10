from pymeasure.instruments.lecroy.waverunner606zi import WaveRunner606Zi
from pymeasure.adapters.activedso import ActiveDSOAdapter

DEFAULT_TIMEOUT = 1
scope_address = '146.136.35.134'

scope = WaveRunner606Zi(address=scope_address)
print(scope.id)
print(scope.measurement.top('C2'))
print(scope.measurement.rms('C2'))
print(scope.measurement.rms('C3'))
print(scope.measurement.peak2peak('C3'))
print(scope.measurement.mean('C3'))
print(scope.get_measurement_Px(7))
scope.save_all_displayed_trc()

scope.save_screen_to_file('prt1')
scope.save_screen_to_file('prt2')

scope.recall_setup_from_file("D:\\Setups\\190123_DSOSetupOpenLoop.lss")

scope.disconnect()