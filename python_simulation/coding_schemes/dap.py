"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.base_coding_scheme import CodingScheme
import logging
from functools import reduce


# Description: Implements the Duplicate-Add Parity Bus Invert (DAPBI) encoding and decoding scheme.
#              The encoding process minimizes transitions by comparing the input binary sequence
#              with the previous sequence, inverting the input if necessary, and appending an
#              inversion (INV) bit. A parity bit is then calculated and appended to ensure error
#              detection. The decoding process reverses this operation to recover the original
#              binary sequence while handling potential errors.
# Inputs:
#              s_in (list[int]): The input binary sequence to be encoded.
#              c_prev (list[int]): The previous encoded sequence for transition comparison.
#              M (int, optional): Parameter for compatibility with other schemes (not used here).
# Outputs:
#              encode(): The encoded binary sequence with minimized transitions, including
#                        duplicated bits, an INV bit, and a parity bit.
#              decode(): The decoded binary sequence, recovering the original input and
#                        handling potential errors.

class DAP(CodingScheme):
    name = "DAP"

    def encode(self, s_in, c_prev, M=None):
        s_copy = s_in[:] 

        # 1. duplicate every bit in the input
        c = []
        for bit in s_copy:
            c.append(bit)
            c.append(bit)

        # 2. Calculate parity bit using XOR of the input, and invert it if INV bit is set
        parity = reduce(lambda x, y: x ^ y, s_in)  # XOR all bits to calculate parity

        # Append the parity bit to the codeword
        c.append(parity)
        c.append(parity)

        logging.debug(f"Final encoded word with duplication:    {c}")

        # Current word: [s_duplicated, INV_duplicated, parity]

        return c
    

    def decode(self, c, M=None):
        # Extract the parity bit and remove it from the codeword
        parity = c[-1]  
        c = c[:-2]

        # XOR all bits to calculate parity
        calculated_parity = reduce(lambda x, y: x ^ y, c)

        # XOR the calculated parity with the received parity
        error = calculated_parity ^ parity

        if error == 0:
            logging.debug(f" No error detected")
            s_out = c[::2]
        else:
            logging.debug(f" ERROR DETECTED: Parity mismatch")
            # Take all odd bits
            s_out = c[1::2]

        logging.debug(f"Final decoded word:                     {s_out[:-1]}")

        return s_out
