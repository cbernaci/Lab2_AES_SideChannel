import os

import numpy as np
import matplotlib.pyplot as plt
import tqdm

import process_traces
import aes_sub

ignore_tqdm = False  # whether to not use tqdm progress bar
plotting = True  # whether to save the trace diff plots
traces_to_load = 2000


def tqdm_sub(x, *args, **kwargs):
    return x


if ignore_tqdm:
    tqdm.tqdm = tqdm_sub

# Define the path to the directory containing the algorithm subfolders
# Change this to your trace path
path = r'D:\OneDrive - nyu.edu\temp\data'

print("loading traces...")
plain_texts, power_traces = process_traces.get_power_trace(
    num_of_traces=traces_to_load, path=path, VCC=5.25)

assert len(plain_texts) == len(power_traces)

BYTE_SIZE = 8
BYTE_MASK = 0xff
TOTAL_BYTE = 16

print("guessing key...")
# guess the key by bytes, from the higher byte to the lower byte
guess_key = []
shift = TOTAL_BYTE * BYTE_SIZE
mask = BYTE_MASK << shift
last_guess_key = None
for byte_i in tqdm.tqdm(range(TOTAL_BYTE), desc="guessing key"):
    shift -= BYTE_SIZE
    mask >>= BYTE_SIZE
    max_diffs = np.zeros(256)
    # TODO: remove this after collecting new traces
    if byte_i >= 2:
        break
    for guess_key_i in tqdm.tqdm(range(BYTE_MASK + 1), leave=False, desc=f"guessing byte {TOTAL_BYTE - byte_i}, last guess: {last_guess_key}"):
        # the traces will be sum up into those two bins
        guess_zero = np.zeros_like(power_traces[0])
        guess_one = np.zeros_like(power_traces[0])
        zero_count = 0
        one_count = 0
        for i, plain_text in enumerate(plain_texts):
            plain_text_i = (plain_text & mask) >> shift
            bit = aes_sub.subbytes(guess_key_i, plain_text_i) & 1
            if bit == 0:
                guess_zero += power_traces[i]
                zero_count += 1
            else:
                guess_one += power_traces[i]
                one_count += 1
        if zero_count == 0:
            diff = guess_one/one_count
        elif one_count == 0:
            diff = guess_zero/zero_count
        else:
            diff = guess_zero/zero_count - guess_one/one_count
        max_diffs[guess_key_i] = np.max(np.abs(diff))
        if plotting:
            store_path = f"data/byte{byte_i}"
            if not os.path.exists(store_path):
                os.makedirs(store_path)
            plt.title(f'guess_key_i = {guess_key_i}')
            plt.plot(diff, label='diff')
            plt.savefig(f'{store_path}/diff_{guess_key_i}.png')
            plt.clf()
    # find the guess_key_i with max difference
    # note: the return type of np.argmax is np.int64, which cause trouble when
    # interpreting the result as a byte
    guess_key.append(int(np.argmax(max_diffs)))
    print(f"guess_key_i = {guess_key[-1]:02x}")  # TODO: remove this line

res = 0
for guess_key_i in guess_key:
    res += guess_key_i
    res <<= BYTE_SIZE
res >>= BYTE_SIZE

print(f"the guessed key is:\n\t{res:032x}")
