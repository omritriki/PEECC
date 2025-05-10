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

class DAPBI(CodingScheme):
    name = "Duplicate-Add-Parity Bus-Invert"
    supports_errors = True

    def get_bus_size(self, k, M=None) -> int:
        n = 2 * k + 3
        return n

    def encode(self, s_in, c_prev, M=None) -> list[int]:
        s_copy = s_in[:] 

        c_notdup = c_prev[:-3:2]  # Take all even bits

        # 1. Calculate bus invert codeword

        A = len(s_copy)
        curr_transitions = sum(1 for i in range(A) if s_copy[i] != c_notdup[i])

        if curr_transitions > (A // 2) or (curr_transitions == A // 2 and c_notdup[-1] == 1):
            # Invert the segment
            s_copy = [1 - bit for bit in s_copy]  
            s_copy.append(1)  
        else:
            s_copy.append(0)  

        # Current word: [s_copy, INV]

        # 2. Calculate parity bit using XOR of the input, and invert it if INV bit is set
        data_bits = s_copy[:-1]
        parity = reduce(lambda x, y: x ^ y, data_bits)  # XOR all bits to calculate parity

        # Invert the parity if the last bit (INV bit) is 1
        if s_copy[-1] == 1:  
            parity = 1 - parity  

        # Append the parity bit to the codeword
        s_copy.append(parity)

        # Current word: [s_copy, INV, parity]

        # 3. Duplicate the bits (excluding the parity bit)
        c = []
        for bit in s_copy[:-2]:  
            c.append(bit)
            c.append(bit)
        inv_bit = s_copy[-2]
        parity_bit = s_copy[-1]

        # Duplicate the INV bit 
        c.append(inv_bit)
        c.append(inv_bit)

        # Add parity once
        c.append(parity_bit)
        logging.debug(f"DAPBI encoded word:                     {c}")


        # Current word: [s_duplicated, INV_duplicated, parity]

        return c
    

    def decode(self, c, M=None) -> list[int]:
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
            logging.debug(f"No error detected")
            if s_out[-1] == 1:
                # Invert the bits
                s_out = [1 - bit for bit in s_out]
        else:
            logging.debug(f"ERROR DETECTED: Parity mismatch")
            # Take all odd bits
            s_out = c[1::2]

            if s_out[-1] == 1:
                # Invert the bits
                s_out = [1 - bit for bit in s_out]

        logging.debug(f"DAPBI decoded word:                     {s_out[:-1]}")

        return s_out[:-1]
