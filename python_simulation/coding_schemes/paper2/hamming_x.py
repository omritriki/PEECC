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
import math


# Description: Extended Hamming code implementation with added shielding bits.
#             Supports single error correction through parity bits. Adds extra
#             shielding zeros between parity bits for transition reduction.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word (not used)
#             M: Optional[int] - Not used
#
# Outputs:    list[int] - Encoded/decoded word where:
#             encode(): [data_bits, parity_bits with shielding]
#             decode(): Corrects single bit errors using parity check matrix

class HammingX(CodingScheme):
    name = "HammingX"
    supports_errors = True
    r = None

    def get_bus_size(self, k, M=None) -> int:
        self.r = math.ceil(math.log2(k))  
        n = k + 2 * self.r - 1
        return n

    def encode(self, s_in, c_prev, M=None) -> list[int]:
        
        s_copy = s_in[:]  
        k = len(s_in)
        
        parity_bits = {}
        
        # Calculate each parity bit
        for i in range(self.r):
            position = 1 << i  
            parity = 0
            
            for j in range(1,         n = k + 2 * self.r - 1
):
                # If this bit position should be checked by current parity bit
                if j & position:
                    # Map the position in complete codeword to original data position
                    data_index = j
                    # Subtract number of parity bits before this position
                    for w in range(self.r):
                        if j > (1 << w):
                            data_index -= 1
                    # If within data range, XOR with the data bit
                    if data_index <= k:
                        parity ^= s_copy[data_index - 1]
            
            parity_bits[position] = parity

        # Create the final codeword   
        c = s_copy
        for i in parity_bits:
            c.append(parity_bits[i])  
            c.append(0)

        logging.debug(f"HammingX encoded word:                  {c[:-1]}")

        return c[:-1]
    

    def decode(self, c, M=None):
        # Calculate number of parity bits from received codeword
        n = len(c)
        m = n
        
        # Extract data and parity bits
        data_bits = c[:-2*self.r + 1] 
        received_parity = {}
        
        # Get received parity bits (they come in pairs with zeros between them)
        parity_index = len(data_bits)
        for i in range(self.r):
            received_parity[1 << i] = c[parity_index]
            parity_index += 2
        
        # Recalculate parity bits from received data
        calculated_parity = {}
        for i in range(self.r):
            position = 1 << i
            parity = 0
            for j in range(1, len(data_bits) + self.r + 1):
                if j & position:
                    data_index = j
                    for k in range(self.r):
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
