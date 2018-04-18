from pypulse import PulseGeneration, PulseInterface
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from scipy import signal

data = sio.loadmat('TestData/testData.mat')
plume = data['plume']
plume = plume[0][0:30000]
print(len(plume))

resampled = signal.resample(plume, 30000*3)

plt.figure()
plt.plot(np.linspace(0, 1, 30000), plume, 'k.')
plt.plot(np.linspace(0, 1, 90000), resampled, 'r.')
plt.show()



# x = np.linspace(0, 10, 20, endpoint=False)
# y = np.cos(-x**2/6.0)
# f = signal.resample(y, 100)
# xnew = np.linspace(0, 10, 100, endpoint=False)
#
# plt.plot(x, y, 'go-', xnew, f, '.-', 10, y[0], 'ro')
# plt.legend(['data', 'resampled'], loc='best')
# plt.show()
