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


# Description: Combines DAP with Bus-Invert coding for both error detection and 
#             transition reduction. Duplicates bits, adds inversion flag and parity.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word
#             M: Optional[int] - Not used
#
# Outputs:    list[int] - Encoded/decoded word
#             encode(): [s_duplicated, INV_duplicated, parity]
#             decode(): Uses parity check and duplication for error detection

class DAPBI(CodingScheme):
    name = "Duplicate-Add-Parity Bus-Invert"
    supports_errors = True


    def get_bus_size(self, k, M=None) -> int:
        n = 2 * k + 3
        return n


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        s_copy = s_in[:] 

        c_notdup = c_prev[:-3:2]  

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
        parity = reduce(lambda x, y: x ^ y, data_bits)  

        if s_copy[-1] == 1:  
            parity = 1 - parity  

        s_copy.append(parity)

        # Current word: [s_copy, INV, parity]

        # 3. Duplicate the bits (excluding the parity bit)
        c = []
        for bit in s_copy[:-2]:  
            c.append(bit)
            c.append(bit)
        inv_bit = s_copy[-2]
        parity_bit = s_copy[-1]

        c.append(inv_bit)
        c.append(inv_bit)

        c.append(parity_bit)

        # Current word: [s_duplicated, INV_duplicated, parity]

        logging.debug(f"DAPBI encoded word:                     {c}")
        return c
    

    def decode(self, c, M=None) -> list[int]:
        # Extract the parity bit and remove it from the codeword
        parity = c[-1]  
        c = c[:-1]
        
        # Take all even bits
        s_out = c[::2]

        # XOR the calculated parity with the received parity
        calculated_parity = reduce(lambda x, y: x ^ y, s_out)
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
