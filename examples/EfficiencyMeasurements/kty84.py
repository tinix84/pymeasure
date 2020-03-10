import numpy as np

class KTY84_130():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._names = ['C', 'F', 'coeffK', 'minOhm', 'typOhm', 'maxOhm', 'errK']
        self._data = [  [-40, -40, 0.84, 340, 359, 379, 6.48],
                            [-30, -22, 0.83, 370, 391, 411, 6.36],
                            [-20, -4, 0.82, 403, 424, 446, 6.26],
                            [-10, 14, 0.80, 437, 460, 483, 6.16],
                            [0, 32, 0.79, 474, 498, 522, 6.07],
                            [10, 50, 0.77, 514, 538, 563, 5.98],
                            [20, 68, 0.75, 555, 581, 607, 5.89],
                            [25, 77, 0.74, 577, 603, 629, 5.84],
                            [30, 86, 0.73, 599, 626, 652, 5.79],
                            [40, 104, 0.71, 645, 672, 700, 5.69],
                            [50, 122, 0.70, 694, 722, 750, 5.59],
                            [60, 140, 0.68, 744, 773, 801, 5.47],
                            [70, 158, 0.66, 797, 826, 855, 5.34],
                            [80, 176, 0.64, 852, 882, 912, 5.21],
                            [90, 194, 0.63, 910, 940, 970, 5.06],
                            [100, 212, 0.61, 970, 1000, 1030, 4.9],
                            [110, 230, 0.60, 1029, 1062, 1096, 5.31],
                            [120, 248, 0.58, 1089, 1127, 1164, 5.73],
                            [130, 266, 0.57, 1152, 1194, 1235, 6.17],
                            [140, 284, 0.55, 1216, 1262, 1309, 6.63],
                            [150, 302, 0.54, 1282, 1334, 1385, 7.1],
                            [160, 320, 0.53, 1350, 1407, 1463, 7.59],
                            [170, 338, 0.52, 1420, 1482, 1544, 8.1],
                            [180, 356, 0.51, 1492, 1560, 1628, 8.62],
                            [190, 374, 0.49, 1566, 1640, 1714, 9.15],
                            [200, 392, 0.48, 1641, 1722, 1803, 9.71],
                            [210, 410, 0.47, 1719, 1807, 1894, 10.28],
                            [220, 428, 0.46, 1798, 1893, 1988, 10.87],
                            [230, 446, 0.45, 1879, 1982, 2085, 11.47],
                            [240, 464, 0.44, 1962, 2073, 2184, 12.09],
                            [250, 482, 0.44, 2046, 2166, 2286, 12.73],
                            [260, 500, 0.42, 2132, 2261, 2390, 13.44],
                            [270, 518, 0.41, 2219, 2357, 2496, 14.44],
                            [280, 536, 0.38, 2304, 2452, 2600, 15.94],
                            [290, 554, 0.34, 2384, 2542, 2700, 18.26],
                            [300, 572, 0.29, 2456, 2624, 2791, 22.12]]

        # Init Data:
        self._data_mat = np.matrix(self._data)
        self._data_C = np.array(self._data_mat[:,0].flatten())[0]
        self._data_K = np.array(self._data_mat[:,1].flatten())[0]
        self._data_coeffK = np.array(self._data_mat[:,2].flatten())[0]
        self._data_minOhm = np.array(self._data_mat[:,3].flatten())[0]
        self._data_typOhm = np.array(self._data_mat[:,4].flatten())[0]
        self._data_maxOhm = np.array(self._data_mat[:,5].flatten())[0]
        self._data_errK = np.array(self._data_mat[:,6].flatten())[0]
        #print(kty84_130_data_C)
        #print(kty84_130_data_typOhm)
        
        # set fitting model to help meas postprocess weigthed to ave better accurary low temp
        fit_coeff = np.polyfit(x=self._data_typOhm, y=self._data_C, deg=4, w=1/self._data_errK)
        self.fit_temp_obj = np.poly1d(fit_coeff)

    def getTempC(self, ohm):
        # check range
        if (ohm > np.amin(self._data_typOhm)) and (ohm < np.amax(self._data_typOhm)):
            idx_upper = list(np.less(ohm,self._data_typOhm)).index(True)
            idx_lower = list(np.greater(ohm,self._data_typOhm)).index(False)-1
            #print(kty84_130_data_typOhm[idx_upper])
            #print(kty84_130_data_typOhm[idx_lower])
            # Set up aliases
            x = ohm
            x0 = self._data_typOhm[idx_lower]
            x1 = self._data_typOhm[idx_upper]
            y0 = self._data_C[idx_lower]
            y1 = self._data_C[idx_upper]   
            temp = float(y0 * (1 - (x - x0) / (x1 - x0)) + y1 * (1 - (x1 - x) / (x1 - x0)))
        else:
            temp = float('inf')
        return temp
    
    def getTempC_fit(self, ohm):
        return self.fit_temp_obj(ohm)
        
    
    
def test():
    thermo = KTY84_130()
    print('Exact values:')
    for ohm in thermo._data_typOhm:
        print('T={0:3.2f} degC, R={1:3.2f} Ohm'.format(thermo.getTempC(ohm), ohm))
    print('Interpolated values:')
    for ohm in np.linspace(500,3000):
        print('T={0:3.2f} degC, R={1:3.2f} Ohm'.format(thermo.getTempC(ohm), ohm))
        
def test_vector():
    import matplotlib.pyplot as plt
    
    thermo = KTY84_130()
    print('Exact values:')
    for ohm in np.linspace(500,3000):
        temp_lut = thermo.getTempC(ohm)
#        print(temp_lut)
        temp_fit = thermo.getTempC_fit(ohm)
        diff = temp_lut - temp_fit
        print(f'T={temp_lut} degC, T={temp_fit} degC, dT={diff}, R={ohm} Ohm')
    
        
def test_vector_operation():
    import matplotlib.pyplot as plt
    
    thermo = KTY84_130()
    ohm_vector = np.linspace(500,3000)
    temp_vect = thermo.getTempC_fit(ohm_vector)
    
    fig, ax = plt.subplots()
    ax.plot(ohm_vector, temp_vect)
    
    ax.set(xlabel='ohm', ylabel='temperature', title='KTY84-130')
    ax.grid()
    plt.show()
    

if __name__ == "__main__":
#    test()
    test_vector()
#    test_vector_operation()
