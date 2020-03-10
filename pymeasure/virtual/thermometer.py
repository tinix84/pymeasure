from pymeasure.instruments.agilent.agilent34970A import Agilent34970A
from examples.EfficiencyMeasurements.kty84 import KTY184_30
from time import sleep

import collections

Sensor = collections.namedtuple('Sensor', [
    'name', 
    'channel',
    'type', 
    'minimum', 
    'maximum', 
    'average'])

def take_param_listcomp(param, temperatures):
    try:
        return [f for f in temperatures if f.name == param][0]
    except IndexError:
        return None

class Thermometer():
    '''thermometer CLASS 
    Constructor for the class thermometer, that represent a generic thermometer.
    This immutable data structure
    '''
    def __init__(self, ThermometerDevice):
        self._data_logger=ThermometerDevice   
        self._temperatures = [
                Sensor('TS1',      101, 'KTY84-130',  0,  0,  0),
                Sensor('TS2',      102, 'KTY84-130',  0,  0,  0),
                Sensor('TC11',     105, 'TC_K',       0,  0,  0),
                Sensor('TC12',     106, 'TC_K',       0,  0,  0),
                Sensor('TSCR11',   107, 'KTY84-130',  0,  0,  0),
                Sensor('TSCR12',   108, 'KTY84-130',  0,  0,  0),
                Sensor('TC21',     109, 'KTY84-130',  0,  0,  0),
                Sensor('TC22',     110, 'KTY84-130',  0,  0,  0),
                Sensor('TSCR21',   112, 'KTY84-130',  0,  0,  0),
                Sensor('TSCR22',   113, 'KTY84-130',  0,  0,  0),
                Sensor('TSCR23',   114, 'KTY84-130',  0,  0,  0),
                Sensor('TSCR24',   115, 'KTY84-130',  0,  0,  0)]
        self.kty84_130=KTY184_30()
    
    def id(self):
        return self._data_logger.id
    
    def temperature(self, sensor_name):
        sensor = take_param_listcomp(sensor_name, self._temperatures)
        if  sensor.type == 'TC_K':
            # print('sensor is thermo K')            
            temperature = self._data_logger.meas_temperature_TC_K(sensor.channel)
        elif sensor.type == 'KTY84-130':
            # print('sensor is kty84-130')
            resistance = self._data_logger.meas_resistance(sensor.channel)
            temperature = self.kty84_130.getTempC(ohm=resistance)
        return temperature
    
    def get_all_temperatures(self):
        temperatures_lst = []
        try:
            for sensor in self._temperatures:
                temperatures_lst.append((sensor.name, self.temperature(sensor.name)))
                sleep(0.2)   
            return temperatures_lst  
        except IndexError:
            return None
    
    def close(self):
        self._data_logger.adapter.connection.close()
        
    def __del__(self):
        self._data_logger.adapter.connection.close()


if __name__ == "__main__":
    ThermometerDevice=Agilent34970A('ASRL1::INSTR')
    thermo = Thermometer(ThermometerDevice)
    print(thermo.id())
    temp_lst=thermo.get_all_temperatures()
    print(dict(temp_lst))
    thermo.close()

