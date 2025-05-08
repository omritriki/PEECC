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


class HAMMINGX(CodingScheme):
    name = "HammingX"
    supports_errors = True

    def get_bus_size(self, k, M=None):
        r = 1
        while (1 << r) < (k + r + 1):
            r += 1
        n = k + 2 * r - 1
        return n

    def encode(self, s_in, c_prev, M=None):
        
        # Calculate number of parity bits needed (2^r ≥ m + r + 1)
        s_copy = s_in[:]  # Copy the input to avoid modifying it
        k = len(s_in)
        r = 1
        while (1 << r) < (k + r + 1):
            r += 1
        
        parity_bits = {}
        
        # Calculate each parity bit
        for i in range(r):
            position = 1 << i  
            parity = 0
            
            # Check each bit position in the final codeword
            for j in range(1, k + r + 1):
                # If this bit position should be checked by current parity bit
                if j & position:
                    # Map the position in complete codeword to original data position
                    data_index = j
                    # Subtract number of parity bits before this position
                    for w in range(r):
                        if j > (1 << w):
                            data_index -= 1
                    # If within data range, XOR with the data bit
                    if data_index <= k:
                        parity ^= s_copy[data_index - 1]
            
            parity_bits[position] = parity

        # Create the final codeword   
        c = s_copy
        for i in parity_bits:
            c.append(parity_bits[i])  # Append parity bits to the end of the data bits
            c.append(0)

        logging.debug(f"HammingX encoded word:                  {c[:-1]}")

        return c[:-1]
    

    def decode(self, c, M=None):
        # Calculate number of parity bits from received codeword
        n = len(c)
        r = 1
        m = n
        while (1 << r) < (m + r + 1):
            r += 1
        
        # Extract data and parity bits
        data_bits = c[:-2*r + 1]  # Original data is at the start
        received_parity = {}
        
        # Get received parity bits (they come in pairs with zeros between them)
        parity_index = len(data_bits)
        for i in range(r):
            received_parity[1 << i] = c[parity_index]
            parity_index += 2
        
        # Recalculate parity bits from received data
        calculated_parity = {}
        for i in range(r):
            position = 1 << i
            parity = 0
            for j in range(1, len(data_bits) + r + 1):
                if j & position:
                    data_index = j
                    for k in range(r):
                        if j > (1 << k):
                            data_index -= 1
                    if data_index <= len(data_bits):
                        parity ^= data_bits[data_index - 1]
            calculated_parity[position] = parity
        
        # Check for errors by comparing received and calculated parity
        error_position = 0
        for pos in received_parity:
            if received_parity[pos] != calculated_parity[pos]:
                error_position += pos
        
        # If error detected, correct it
        if error_position > 0 and error_position <= len(data_bits):
            logging.debug(f"ERROR DETECTED: position {error_position}")
            data_bits[error_position - 1] ^= 1 
        
        logging.debug(f"HammingX decoded word:                  {c[:-1]}")

        return data_bits
