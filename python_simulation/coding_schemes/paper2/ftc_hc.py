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
#
# Outputs:    


class FTC_HC(CodingScheme):
    name = "Forbidden Transition + Hamming"
    supports_errors = True  


    def get_bus_size(self, k, M=None) -> int:
        n = 2 * k + 1
        return n


    def encode(self, s_in, c_prev, M=None) -> list[int]:


        logging.debug(f"DAP encoded word:                       {c}")
        return c
    

    def decode(self, c, M=None) -> list[int]:


        logging.debug(f"DAP decoded word:                       {s_out}")
        return s_out
