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


# Description: 

# Inputs:

# Outputs:


class DAP(CodingScheme):
    name = "Duplicate-Add-Parity"

    def get_bus_size(self, k, M=None):
        n = 2 * k + 1
        return n

    def encode(self, s_in, c_prev, M=None):
        s_copy = s_in[:] 

        # Duplicate every bit in the input
        c = []
        for bit in s_copy:
            c.append(bit)
            c.append(bit)

        # Calculate parity bit using XOR of the input
        parity = reduce(lambda x, y: x ^ y, s_in)  

        # Append the parity bit to the codeword
        c.append(parity)
        c.append(parity)

        logging.debug(f"DAP encoded word:                       {c}")

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
            logging.debug(f"No error detected")
            s_out = c[::2]
        else:
            logging.warning(f"ERROR DETECTED: Parity mismatch")
            # Take all odd bits
            s_out = c[1::2]

        logging.debug(f"DAP decoded word:                       {s_out}")

        return s_out
