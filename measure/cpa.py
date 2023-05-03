"""
correlation power analysis using Hamming weight model and earson correlation coefficient equation

reference: https://www.tandfonline.com/doi/epdf/10.1080/23742917.2016.1231523?needAccess=true&role=button
"""
import os
import numpy as np

import process_traces
from aes_sub import *

# Define the path to the directory containing the algorithm subfolders
# TODO: change this to your trace path
path = r'D:\OneDrive - nyu.edu\temp\data\meas3'

use_tqdm = True  # whether to not use tqdm progress bar
traces_to_load = 0
B8 = 8
B16 = 16
B256 = 256
B8_MASK = 0xff
SIZE = 32


def tqdm_sub(x, *args, **kwargs):
    return x


if not use_tqdm:
    tqdm = tqdm_sub
    tqdm.write = print
else:
    try:
        from tqdm import tqdm
    except ImportError:
        use_tqdm = False
        tqdm = tqdm_sub
        tqdm.write = print

assert len(sbox) == B16*B16
assert len(inv_sbox) == B16*B16

# load in traces
if os.path.exists(f'{path}/plain_texts_bytes.npy') and os.path.exists(f'{path}/trace.npy'):
    print("loading saved data...")
    plain_texts_bytes = np.load(f'{path}/plain_texts_bytes.npy')
    traces = np.load(f'{path}/trace.npy')
else:
    print("loading traces...")
    plain_texts, traces = process_traces.get_power_trace(
        num_of_traces=0, path=path, VCC=5.25, keep_percent=0.5)

    plain_texts_bytes = []
    for i, c in enumerate(plain_texts):
        ci = []
        for j in range(int(SIZE/2)):
            ci.append(c & B8_MASK)
            c >>= B8
        ci.reverse()
        plain_texts_bytes.append(ci)

    np.save(f'{path}/plain_texts_bytes.npy', plain_texts_bytes)
    np.save(f'{path}/trace.npy', traces)
    print("saved traces and plain texts")

trace_count = len(traces)
trace_length = len(traces[0])
assert (trace_count == len(plain_texts_bytes))

# create save directory for correlation images
save_dir = 'img_corr'
save_dir = os.path.join(path, save_dir)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

print("start CPA...")
for const_use in tqdm(range(B256), desc="const use"):
    key = []
    mean_t = np.mean(traces, axis=0)
    # Mean delta accumulation of traces, just for visualization
    correlation_on_trace_visualization = []
    last_guess_key = ''
    for byte_i in tqdm(range(B16), desc=f"const use: {const_use}", leave=False):
        max_cpa = [0]*B256
        correlation_on_trace_visualization.append([])

        for key_guess in tqdm(range(B256), desc=f"last key: {last_guess_key}", leave=False):
            power_mode = np.zeros(trace_count)
            numerator = np.zeros(trace_length)
            denominator_model = np.zeros(trace_length)
            denominator_measured = np.zeros(trace_length)

            for trace_index in range(trace_count):
                vij = apply_sbox(
                    plain_texts_bytes[trace_index][byte_i] ^ key_guess)
                power_mode[trace_index] = HW[vij ^ const_use]

            mean_h = np.mean(power_mode)

            for trace_index in range(trace_count):
                # h - h_bar
                h_diff = power_mode[trace_index] - mean_h
                # t - t_bar
                t_diff = traces[trace_index][:] - mean_t
                # (h - h_bar)(t - t_bar)
                numerator += h_diff * t_diff
                # (h - h_bar)^2
                denominator_model += h_diff ** 2
                # (t - t_bar)^2
                denominator_measured += t_diff ** 2
            correlation_on_trace = numerator / \
                np.sqrt(denominator_model*denominator_measured)
            max_cpa[key_guess] = max(abs(correlation_on_trace))
            correlation_on_trace_visualization[byte_i].append(
                correlation_on_trace)
        key.append(np.argmax(max_cpa))
        last_guess_key = f"{key[-1]:02x}"

    res = 0
    for key_guess in guess_key:
        res += key_guess
        res <<= B8
    res >>= B8

    tqdm.write(f"Round {bit_use}: the guessed key is: {res:032x}")
    np.save(f"{save_dir}/corr_visualization_{const_use}.npy",
            np.array(correlation_on_trace_visualization))
