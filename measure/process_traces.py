import os
import random

import numpy as np


def get_power_trace(num_of_traces, path, VCC, keep_percent=0.75):
    """
    get the power traces as np array

    keep_percent: how many percentage of trace to keep, last part are cut off

    return: plaintext_lst, power_traces
    """
    # Check if the path is valid
    if not os.path.isdir(path):
        raise NotADirectoryError('Invalid path: {}'.format(path))

    power_traces = []
    plaintext_lst = []

    if num_of_traces > len(os.listdir(path)) or num_of_traces <= 0:
        voltage_traces = os.listdir(path)
    else:
        voltage_traces = random.sample(os.listdir(path), num_of_traces)

    # Loop over the directory and process the first num_of_traces traces
    for dirname in voltage_traces:
        if dirname.endswith('.npy'):
            plain_text = dirname[:-4]
            full_path = os.path.join(path, dirname)
            trace, trigger = np.load(full_path)
            start_i = 0
            for i in range(len(trigger)):
                if trigger[i] > 3:
                    start_i = i
                    break
            trace = trace[start_i:]
            if power_traces:
                # if power_traces is not empty, make later traces the same size as the first one
                if len(trace) < len(power_traces[0]):
                    print(f"Warning: trace {plain_text} too short, ignored")
                    # if shorter, pad with 0s
                    continue
                elif len(trace) > len(power_traces[0]):
                    # if longer, truncate
                    trace = trace[:len(power_traces[0])]
            else:
                # exclude last 25% of the trace to avoid the end of the trace
                trace = trace[:int(len(trace)*keep_percent)]
            # note: the resistance value doesn't matter, since
            # P = IV = (VCC-V) * (V/R) is proportional to (VCC-V) * V
            # TODO: maybe use voltage directly would be better?
            plaintext_lst.append(int(plain_text, 16))
            power_traces.append((VCC - trace) * trace)

    assert len(plaintext_lst) == len(power_traces)
    return plaintext_lst, np.array(power_traces)


if __name__ == "__main__":
    # randomly get one power trace and plot it
    p, power = get_power_trace(
        1, r"C:\Users\Jerry\OneDrive - nyu.edu\temp\data\meas2", VCC=5.25)
    import matplotlib.pyplot as plt
    plt.plot(power[0])
    plt.show()
