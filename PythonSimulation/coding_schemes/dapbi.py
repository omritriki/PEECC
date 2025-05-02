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
# configure_logging()


class DAPBI(CodingScheme):
    name = "DAPBI"

    def encode(self, s_in, c_prev, M=None):
        s_copy = s_in[:] 

        c_notdup = c_prev[:-3:2]  # Take all even bits

        # 1. Calculate bus invert codeword
        logging.debug(f" ")
        logging.debug(f"info word word with duplication:        {s_in}")
        logging.debug(f"Previous codeword:                      {c_notdup}")

        A = len(s_copy)

        curr_transitions = sum(1 for i in range(A) if s_copy[i] != c_notdup[i])

        if curr_transitions > (A // 2) or (curr_transitions == A // 2 and c_notdup[-1] == 1):
            # Invert the segment
            s_copy = [1 - bit for bit in s_copy]  
            s_copy.append(1)  # Set INV bit to 1
        else:
            s_copy.append(0)  # Set INV bit to 0 

        # Current word: [s_copy, INV]
        logging.debug(f"  ")
        logging.debug(f"bi word:                                {s_copy}")
        logging.debug(f"  ")

      
        # 2. Calculate parity bit using XOR of the input, and invert it if INV bit is set
        data_bits = s_copy[:-1]
        parity = reduce(lambda x, y: x ^ y, data_bits)  # XOR all bits to calculate parity

        # Invert the parity if the last bit (INV bit) is 1
        if s_copy[-1] == 1:  # Check the INV bit
            parity = 1 - parity  # Invert the parity

        # Append the parity bit to the codeword
        s_copy.append(parity)

        # Current word: [s_copy, INV, parity]

        # 3. Duplicate the bits (excluding the parity bit)
        c = []
        for bit in s_copy[:-2]:  # duplicate only data bits
            c.append(bit)
            c.append(bit)
        inv_bit = s_copy[-2]
        parity_bit = s_copy[-1]

        # Duplicate the INV bit too
        c.append(inv_bit)
        c.append(inv_bit)

        # Add parity once
        c.append(parity_bit)
        logging.debug(f"Final encoded word with duplication:    {c}")

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
            # logging.debug("No error detected in the received codeword.")
            if s_out[-1] == 1:
                # Invert the bits
                s_out = [1 - bit for bit in s_out]
        else:
            # logging.debug("Error detected in the received codeword.")
            # Take all odd bits
            s_out = c[1::2]

            if s_out[-1] == 1:
                # Invert the bits
                s_out = [1 - bit for bit in s_out]

        logging.debug(f"Final decoded word:                     {s_out[:-1]}")

        return s_out[:-1]
