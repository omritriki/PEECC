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


class DAPBI(CodingScheme):
    """
    Implements: Duplicate-Add-Parity Bus-Invert coding scheme that combines bit duplication,
                parity checking, and bus inversion for both error detection and transition reduction.

    Args:
        None (inherits from CodingScheme base class)

    Returns:
        None (class definition)
    """
    name = "Duplicate Add-Parity Bus-Invert"
    supports_errors = True


    def get_bus_size(self, k, M=None) -> int:
        """
        Implements: Bus width calculation for DAPBI scheme, accounting for duplicated data bits,
                    duplicated inversion flag, and single parity bit.

        Args:
            k (int): Number of input data bits
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            int: Total bus width required (2k + 3 bits).
        """
        n = 2 * k + 3
        return n


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        """
        Implements: DAPBI encoding algorithm that applies bus inversion, calculates parity,
                    and duplicates all bits except the final parity bit for error detection.

        Args:
            s_in (list[int]): Input binary word to encode
            c_prev (list[int]): Previous encoded codeword for transition comparison
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Encoded codeword with duplicated data, duplicated inversion flag, and parity bit.
        """
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
        """
        Implements: DAPBI decoding algorithm that uses parity checking and bit duplication
                    for error detection, selecting between even and odd positioned bits based on error status.

        Args:
            c (list[int]): Received encoded codeword to decode
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Decoded binary word with error correction applied and inversion reversed.
        """
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
