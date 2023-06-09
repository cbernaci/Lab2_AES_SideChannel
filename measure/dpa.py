import os
import numpy as np

import process_traces
from aes_sub import *

# Define the path to the directory containing the algorithm subfolders
# TODO: change this to your trace path
path = r'D:\OneDrive - nyu.edu\temp\data\meas2'

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

# load in traces
if os.path.exists(f'{path}/plain_texts_bytes.npy') and os.path.exists(f'{path}/trace.npy'):
    print("loading saved data...")
    plain_texts_bytes = np.load(f'{path}/plain_texts_bytes.npy')
    traces = np.load(f'{path}/trace.npy')
else:
    print("loading traces...")
    plain_texts, traces = process_traces.get_power_trace(
        num_of_traces=traces_to_load, path=path, VCC=5.25, keep_percent=0.5)

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

# create save directory for the difference visualization
save_dir = 'img_diff'
save_dir = os.path.join(path, save_dir)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

print("start DPA...")
for bit_use in tqdm(range(B8)):
    # guess the key by bytes, from the higher byte to the lower byte
    guess_key = []
    # Mean delta accumulation of traces, just for visualization
    mean_delta_accu_visualization = []
    last_guess_key = ''
    for byte_i in tqdm(range(B16), desc=f"Use bit {bit_use}", leave=False):
        max_diffs = np.zeros(256)
        mean_delta_accu_visualization.append([])
        for key_guess in tqdm(range(B256), leave=False, desc=f"last key: {last_guess_key}, guessing byte {B16 - byte_i}"):
            # the traces will be sum up into those two bins
            guess_zero = np.zeros_like(traces[0])
            guess_one = np.zeros_like(traces[0])
            zero_count = 0
            one_count = 0
            for i in range(trace_count):
                bit = (apply_sbox(
                    plain_texts_bytes[i][byte_i] ^ key_guess) >> bit_use) & 1
                if bit == 0:
                    guess_zero += traces[i]
                    zero_count += 1
                else:
                    guess_one += traces[i]
                    one_count += 1
            if zero_count == 0:
                # TODO: might not be the best way to handle this
                diff = guess_one/one_count
            elif one_count == 0:
                # TODO: might not be the best way to handle this
                diff = guess_zero/zero_count
            else:
                diff = guess_zero/zero_count - guess_one/one_count
            diff = np.abs(diff)
            max_diffs[key_guess] = np.max(diff)
            mean_delta_accu_visualization[byte_i].append(diff)
        # find the guess_key_i with max difference
        # note: the return type of np.argmax is np.int64, which cause trouble when
        # interpreting the result as a byte
        guess_key.append(int(np.argmax(max_diffs)))
        last_guess_key = f"{guess_key[-1]:02x}"

    res = 0
    for key_guess in guess_key:
        res += key_guess
        res <<= B8
    res >>= B8

    tqdm.write(f"Round {bit_use}: the guessed key is: {res:032x}")
    np.save(f"{save_dir}/diff_visualization_{res:032x}.npy",
            np.array(mean_delta_accu_visualization))
