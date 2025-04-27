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

    def encode(self, s, c_prev):
        # The DAPBI encoding process

        # 1. Calculate bus invert codeword
        logging.debug(f"Checking inversion for word: s={s}, c_prev={c_prev}")
        A = len(s)

        curr_transitions = sum(1 for i in range(A) if s[i] != c_prev[i])

        logging.debug(f"Current transitions: {curr_transitions}, Threshold: {A // 2}")

        if curr_transitions > A // 2 or (curr_transitions == A // 2 and c_prev[-1] == 1):
            # Invert the segment
            s = [bit ^ 1 for bit in s]  # Flip all bits using list comprehension
            s.append(1)  # Set INV bit to 1
            logging.debug(f"Segment inverted: {s}")
        else:
            s.append(0)  # Set INV bit to 0 (if no inversion)
            logging.debug(f"Segment not inverted: {s}")

        # Current word: [s, INV]

        # 2. Calculate parity bit using XOR of the input, and invert it if INV bit is set
        data_bits = s[:-1]
        parity = reduce(lambda x, y: x ^ y, data_bits)  # XOR all bits to calculate parity
        logging.debug(f"Calculated parity (before inversion): {parity}")

        # Invert the parity if the last bit (INV bit) is 1
        if s[-1] == 1:  # Check the INV bit
            parity = 1 - parity  # Invert the parity
            logging.debug(f"Parity inverted due to INV bit: {parity}")

        # Append the parity bit to the codeword
        s.append(parity)
        logging.debug(f"Final encoded word with parity: {s}")

        # Current word: [s, INV, parity]

        # 3ץ Duplicate the bits (excluding the parity bit)
        c = []
        for bit in s[:-1]:
            c.append(bit)
            c.append(bit)
        c.append(s[-1])
        logging.debug(f"Final encoded word with duplication: {c}")

        # Current word: [s_duplicated, INV_duplicated, parity]

        return c
    

    def decode(self, c):
        # Extract the parity bit and remove it from the codeword
        parity = c[-1]  
        c = c[:-1]

        # Take all even bits
        w = c[::2]

        # XOR all even bits to calculate parity
        calculated_parity = reduce(lambda x, y: x ^ y, w)

        # XOR the calculated parity with the received parity
        error = calculated_parity ^ parity

        if error == 0:
            logging.debug("No error detected in the received codeword.")
            if w[-1] == 1:
                # Invert the last bit of the word
                w = [1 - bit for bit in w[:-1]]
            return w[:-1]  # Return the word without the INV bit
        else:
            logging.debug("Error detected in the received codeword.")
            # Take all odd bits
            w = c[1::2]
            if w[-1] == 1:
                # Invert the last bit of the word
                w = [1 - bit for bit in w[:-1]]
            return w[:-1]   # Return the word without the INV bit
            