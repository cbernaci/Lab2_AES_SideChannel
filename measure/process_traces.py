import numpy as np
import matplotlib.pyplot as plt
import os

# Define the path to the directory containing the algorithm subfolders
path = 'data'

# Loop over each subdirectory in the algorithm directory
for dirname in os.listdir(path):
    if dirname.endswith('.npy'):
        plain_text = dirname[:-4]
        plt.title(f"trace of {plain_text}")

        full_path = os.path.join(path, dirname)
        voltages = np.load(full_path)
        sample = -1
        plt.plot(voltages[0][:sample], label='trace')
        plt.plot(voltages[1][:sample], label='trigger')

        window_size = 1000
        ma = np.convolve(voltages[0][:sample], np.ones(
            window_size)/window_size, mode='valid')
        plt.plot(ma, label='moving average')

        plt.legend()
        plt.show()
    
    break


# fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
