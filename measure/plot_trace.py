"""
plot a single trace
"""

import matplotlib.pyplot as plt
import numpy as np
import os

plain_text = "0376B37C912E6333F6762E3F35F7218B"
path = r'D:\OneDrive - nyu.edu\temp\data\meas with one aes quick clock'
full_path = os.path.join(path, f"{plain_text}.npy")
trace, trigger = np.load(full_path)
plt.plot(trace)
plt.plot(trigger)
plt.show()
