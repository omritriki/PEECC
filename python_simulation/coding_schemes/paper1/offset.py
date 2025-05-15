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


# Description: Implements Offset encoding that transmits differences between consecutive
#             words using two's complement arithmetic. Reduces transitions for sequential
#             data by sending only changes between words.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word (not used in this scheme)
#             M: Optional[int] - Not used in this scheme
#
# Outputs:    list[int] - Encoded/decoded k-bit word where:
#             encode(): c = s - s_prev (in two's complement)
#             decode(): s = c + s_prev (in two's complement)

class Offset(CodingScheme):
    name = "Offset"
    supports_errors = False
    

    def get_bus_size(self, k, M=None) -> int:
        return k


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        # Initialize with zeros on first decode
        if self.s_prev is None:
            self.s_prev = [0] * len(s_in)  

        # Convert binary lists to integers for two's complement arithmetic
        s_curr = int(''.join(map(str, s_in)), 2)
        s_previous = int(''.join(map(str, self.s_prev)), 2)
        
        # Calculate difference in two's complement
        diff = (s_curr - s_previous) % (2 ** len(s_in))
        
        # Convert back to binary list
        c = [int(x) for x in format(diff, f'0{len(s_in)}b')]

        logging.debug(f"Offset encoded word:                    {c}")

        return c
    

    def decode(self, c, M=None) -> list[int]:
        # Initialize with zeros on first decode
        if self.s_prev is None:
            self.s_prev = [0] * len(c)  
            
         # Convert binary lists to integers for two's complement arithmetic
        c_curr = int(''.join(map(str, c)), 2)
        s_previous = int(''.join(map(str, self.s_prev)), 2)
        
        # Calculate sum in two's complement
        s_out_int = (c_curr + s_previous) % (2 ** len(c))
        
        # Convert back to binary list
        s_out = [int(x) for x in format(s_out_int, f'0{len(c)}b')]
        
        # Store current output as previous for next decode
        self.s_prev = s_out[:]
        
        logging.debug(f"Offset decoded word:                    {s_out}")

        return s_out
