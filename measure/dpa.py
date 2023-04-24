import numpy as np
import matplotlib.pyplot as plt
import tqdm

import process_traces
import aes_sub

# Define the path to the directory containing the algorithm subfolders
# Change this to your trace path
path = r'D:\OneDrive - nyu.edu\temp\data'

plain_texts, power_traces = process_traces.get_power_trace(
    num_of_traces=10, path=path, VCC=5.25)

assert len(plain_texts) == len(power_traces)

BYTE_SIZE = 8
BYTE_MASK = 0xff
TOTAL_BYTE = 16

# guess the key by bytes, from the higher byte to the lower byte
guess_key = []
shift = TOTAL_BYTE * BYTE_SIZE
mask = BYTE_MASK << shift
for byte_i in tqdm.tqdm(range(TOTAL_BYTE), desc="guessing key"):
    # the traces will be sum up into those two bins
    guess_zero = np.zeros_like(power_traces[0])
    guess_one = np.zeros_like(power_traces[0])
    shift -= BYTE_SIZE
    mask >>= BYTE_SIZE
    max_diffs = np.zeros(256)
    for guess_key_i in tqdm.tqdm(range(BYTE_MASK + 1), leave=False, desc=f"guessing byte {TOTAL_BYTE - byte_i}"):
        for i, plain_text in enumerate(plain_texts):
            plain_text_i = (plain_text & mask) >> shift
            bit = aes_sub.subbytes(guess_key_i, plain_text_i) & 1
            if bit == 0:
                guess_zero += power_traces[i]
            else:
                guess_one += power_traces[i]
        max_diffs[guess_key_i] = np.max(np.abs(guess_zero - guess_one))
    # find the guess_key_i with max difference
    guess_key.append(np.argmax(max_diffs))

res = 0
for guess_key_i in guess_key:
    res += guess_key_i
    res <<= BYTE_SIZE

print(f"the guessed key is:\n\t{res:032x}")
