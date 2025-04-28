"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.base_coding_scheme import CodingScheme
from logging_config import configure_logging
import logging
from functools import reduce

# Configure logging
configure_logging()


class DAPBI(CodingScheme):
    name = "DAPBI"

    def encode(self, s_in, c_prev, M=None):
        # Work on a copy of s to avoid modifying the original input
        s_copy = s_in[:]  # Create a shallow copy of s

        # The DAPBI encoding process

        # 1. Calculate bus invert codeword
        logging.debug(f"Checking inversion for word: s={s_copy}, c_prev={c_prev}")
        A = len(s_copy)

        curr_transitions = sum(1 for i in range(A) if s_copy[i] != c_prev[i])

        logging.debug(f"Current transitions: {curr_transitions}, Threshold: {A // 2}")

        if curr_transitions > A // 2 or (curr_transitions == A // 2 and c_prev[-1] == 1):
            # Invert the segment
            s_copy = [bit ^ 1 for bit in s_copy]  # Flip all bits using list comprehension
            s_copy.append(1)  # Set INV bit to 1
            logging.debug(f"Segment inverted: {s_copy}")
        else:
            s_copy.append(0)  # Set INV bit to 0 (if no inversion)
            logging.debug(f"Segment not inverted: {s_copy}")

        # Current word: [s_copy, INV]

        # 2. Calculate parity bit using XOR of the input, and invert it if INV bit is set
        data_bits = s_copy[:-1]
        parity = reduce(lambda x, y: x ^ y, data_bits)  # XOR all bits to calculate parity
        logging.debug(f"Calculated parity (before inversion): {parity}")

        # Invert the parity if the last bit (INV bit) is 1
        if s_copy[-1] == 1:  # Check the INV bit
            parity = 1 - parity  # Invert the parity
            logging.debug(f"Parity inverted due to INV bit: {parity}")

        # Append the parity bit to the codeword
        s_copy.append(parity)
        logging.debug(f"Final encoded word with parity: {s_copy}")

        # Current word: [s_copy, INV, parity]

        # 3. Duplicate the bits (excluding the parity bit)
        c = []
        for bit in s_copy[:-1]:
            c.append(bit)
            c.append(bit)
        c.append(s_copy[-1])
        logging.debug(f"Final encoded word with duplication: {c}")

        # Current word: [s_duplicated, INV_duplicated, parity]

        return c
    

    def decode(self, c, M=None):
        # Extract the parity bit and remove it from the codeword
        parity = c[-1]  
        c = c[:-1]
        
        # Take all even bits
        s_out = c[::2]

        # XOR all even bits to calculate parity
        calculated_parity = reduce(lambda x, y: x ^ y, s_out)

        # XOR the calculated parity with the received parity
        error = calculated_parity ^ parity

        if error == 0:
            logging.debug("No error detected in the received codeword.")
            if s_out[-1] == 1:
                # Invert the bits
                s_out = [1 - bit for bit in s_out]
        else:
            logging.debug("Error detected in the received codeword.")
            # Take all odd bits
            s_out = c[1::2]

            if s_out[-1] == 1:
                # Invert the bits
                s_out = [1 - bit for bit in s_out]

        return s_out[:-1]
