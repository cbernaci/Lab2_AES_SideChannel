import numpy as np
import matplotlib.pyplot as plt
import os

# Define the path to the directory containing the algorithm subfolders
path = 'data'

# Loop over each subdirectory in the algorithm directory
for dirname in os.listdir(path):
    fullpath = os.path.join(path, dirname)
    print(dirname.rstrip('.npy'))


# fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)


voltages = np.load("data/00112233445566778899AABBCCDDEEFF.npy")
print(voltages.shape)
sample = -1
plt.plot(voltages[0][:sample])
print(voltages[0][:sample].mean())
# plt.plot(voltages[1][:sample])

window_size = 1000
ma = np.convolve(voltages[0][:sample], np.ones(window_size)/window_size, mode='valid')
plt.plot(ma)

plt.show()
