import numpy as np
import matplotlib.pyplot as plt


fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)


voltages = np.load('partial_samples.npy')
ax1.plot(voltages)

ax2.plot(np.load("samples.npy"))

# window_size = 100
# ma = np.convolve(voltages, np.ones(window_size)/window_size, mode='valid')
# plt.plot(ma)

plt.show()
