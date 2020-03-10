from pymeasure.instruments.lecroy.waverunner import WaveRunner
from pymeasure.adapters.activedso import ActiveDSOAdapter

DEFAULT_TIMEOUT = 1

scope = WaveRunner('TCPIP0::146.136.35.134::inst0::INSTR')
print(scope.id)
print(scope.measurement.top('C2'))
print(scope.measurement.rms('C2'))
print(scope.measurement.rms('C3'))
print(scope.measurement.peak2peak('C3'))
print(scope.measurement.mean('C3'))
print(scope.get_measurement_Px(7))

