"""
used to plot the result after dpa/cpa attack
"""
import os
import numpy as np
import matplotlib.pyplot as plt

path = r'D:\OneDrive - nyu.edu\temp\data\meas3'

diff_path = os.path.join(path, 'img_diff')
if not os.path.isdir(diff_path):
    raise NotADirectoryError('Invalid path: {}'.format(diff_path))

for file in os.listdir(diff_path):
    if file.endswith('.npy'):
        full_path = os.path.join(diff_path, file)
        graphs = np.load(full_path)
        # graphs has shape 16 * 256 * traces
        for i in range(16):
            max_guess = np.argmax(graphs[i], axis=None)
            graph, _ = np.unravel_index(max_guess, graphs[i].shape)
            plt.plot(graphs[i][graph])
            plt.show()
            plt.cla()
            # break for now, only plot one graph
            break
        # break for now, only plot the guess with first bit
        break
