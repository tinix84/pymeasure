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