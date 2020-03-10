'''
File: 
Project:
Date:
Author:       Falk Kyburz
Comments:     Wayne Kerr *.CSV Processor
              This module recreates the impedance plot from the data exported 
              in .csv format.
'''

# Initialization
import numpy as np
import matplotlib
# matplotlib.use('Qt5AGG')
import matplotlib.pyplot as plt
import csv
from os import listdir



# -----------------------------------------------------------------------------
# Give List of filenames here
# -----------------------------------------------------------------------------
path = ''
# filenames = ('wima_mkp4_dclink_10u800v.csv',
#             'wima_mkp4_dclink_5u1300v.csv',
#             'wima_mkp4_dclink_7u1300v.csv')
filenames = [fn for fn in listdir('.') if fn.endswith('.csv')]

# -----------------------------------------------------------------------------
# Read CSV files
# -----------------------------------------------------------------------------
headings = dict()
data = dict()
freq = dict()
imp = dict()
phi = dict()

for fn in filenames:
    with open(path+fn) as file:
        reader=csv.reader(file, delimiter=',')
        rawdata = np.matrix(list(reader))
        headings[fn] = rawdata[0]
        data[fn] = rawdata[1:].astype(float)
        freq[fn] = np.array(data[fn][:,0].flatten())[0]
        imp[fn] = np.array(data[fn][:,1].flatten())[0]
        phi[fn] = np.array(data[fn][:,2].flatten())[0]
        #print(freq[fn])
        
# -----------------------------------------------------------------------------
# Plot Data and Annotations
# -----------------------------------------------------------------------------        
fig,axes = plt.subplots(2,1)

for fn in filenames:
    axes[0].loglog(freq[fn],imp[fn],label=fn)   
    axes[1].semilogx(freq[fn],phi[fn],label=fn)
    

axes[0].set_title('Impedance')
axes[0].set_xlabel('Frequency [Hz]')
axes[0].set_ylabel('[$\Omega$]')
axes[0].set_xlim(1e3,15e6)
axes[0].grid(True, which='minor' )
# axes[0].legend(loc='lower left', fontsize='default')
axes[1].legend(loc='upper left')
axes[1].set_title(' Phase')
axes[1].set_xlabel('Frequency [Hz]')
axes[1].set_ylabel('[°]')
axes[1].set_xlim(1e3,15e6)
axes[1].grid(True, which='major' )

fig.set_size_inches((12, 8), forward=True)
fig.patch.set_facecolor('white')
plt.tight_layout()
plt.show()