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


# Description: Transition-based encoding where each bit represents a change (1) or 
#             no change (0) from previous state.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word
#             M: Optional[int] - Not used
#
# Outputs:    list[int] - Encoded/decoded k-bit word

class Transition_Signaling(CodingScheme):
    name = "Transition Signaling"
    supports_errors = False
    

    def get_bus_size(self, k, M=None) -> int:
        return k


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        # Initialize with zeros on first decode
        if self.s_prev is None:
            self.s_prev = [0] * len(s_in)  

        s_copy = s_in[:] 

        # c = s_in ^ c_prev
        c = [int(s_copy[i]) ^ int(self.s_prev[i]) for i in range(len(s_copy))]

        logging.debug(f"Transtion Signaling encoded word:       {c}")
        return c
    

    def decode(self, c, M=None) -> list[int]:
        # Initialize with zeros on first decode
        if self.s_prev is None:
            self.s_prev = [0] * len(c)  
            
        # s_out = c ^ s_prev
        s_out = [int(c[i]) ^ int(self.s_prev[i]) for i in range(len(c))]
        
        # Store current output as previous for next decode
        self.s_prev = s_out[:]
        
        logging.debug(f"Transition Signaling decoded word:      {s_out}")
        return s_out
