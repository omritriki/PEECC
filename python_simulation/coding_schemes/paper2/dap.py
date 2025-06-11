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


class DAP(CodingScheme):
    """
    Implements: Duplicate-Add-Parity coding scheme that provides simple error detection
                through bit duplication and parity checking without transition optimization.

    Args:
        None (inherits from CodingScheme base class)

    Returns:
        None (class definition)
    """
    name = "Duplicate Add-Parity"
    supports_errors = True  


    def get_bus_size(self, k, M=None) -> int:
        """
        Implements: Bus width calculation for DAP scheme, accounting for duplicated data bits
                    and a single parity bit.

        Args:
            k (int): Number of input data bits
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            int: Total bus width required (2k + 1 bits).
        """
        n = 2 * k + 1
        return n


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        """
        Implements: DAP encoding algorithm that duplicates each input bit and appends
                    a parity bit calculated from the original word.

        Args:
            s_in (list[int]): Input binary word to encode
            c_prev (list[int]): Previous encoded codeword (unused in this scheme)
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Encoded codeword with duplicated bits and parity bit [s0,s0,s1,s1,...,sk,sk,p].
        """
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
        """
        Implements: DAP decoding algorithm that uses parity checking to detect errors
                    and selects between even and odd positioned bits for error correction.

        Args:
            c (list[int]): Received encoded codeword to decode
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Decoded binary word with error detection applied.
        """
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
