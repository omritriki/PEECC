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


# Description: Simple error detection through bit duplication and parity.
#             Duplicates each input bit and adds parity bit of original word.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word (not used)
#             M: Optional[int] - Not used
#
# Outputs:    list[int] - Encoded/decoded word
#             encode(): [s0,s0,s1,s1,...,sk,sk,p]
#             decode(): even/odd bits based on parity check

class DAP(CodingScheme):
    name = "Duplicate-Add-Parity"
    supports_errors = True  


    def get_bus_size(self, k, M=None) -> int:
        n = 2 * k + 1
        return n


    def encode(self, s_in, c_prev, M=None) -> list[int]:
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

        logging.debug(f"DAP encoded word:                       {c}")
        return c
    

    def decode(self, c, M=None) -> list[int]:
        # Extract the parity bit and remove it from the codeword
        parity = c[-1]  
        c = c[:-1]

        # XOR all even bits to calculate parity
        calculated_parity = reduce(lambda x, y: x ^ y, c[::2])

        # XOR the calculated parity with the received parity
        error = calculated_parity ^ parity

        if error == 0:
            logging.debug(f"No error detected")
            s_out = c[::2]
        else:
            logging.debug(f"ERROR DETECTED: Parity mismatch")
            # Take all odd bits
            s_out = c[1::2]

        logging.debug(f"DAP decoded word:                       {s_out}")
        return s_out
