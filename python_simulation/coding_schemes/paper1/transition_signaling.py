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


class Transition_Signaling(CodingScheme):
    """
    Implements: Transition-based encoding scheme where each transmitted bit represents
                a change (1) or no change (0) from the previous bus state.

    Args:
        None (inherits from CodingScheme base class)

    Returns:
        None (class definition)
    """
    name = "Transition Signaling"
    supports_errors = False
    

    def get_bus_size(self, k, M=None) -> int:
        """
        Implements: Bus width calculation for Transition Signaling scheme, which maintains
                    the same width as input since transitions are encoded directly.

        Args:
            k (int): Number of input data bits
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            int: Bus width equal to input width (k bits).
        """
        return k


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        """
        Implements: Transition Signaling encoding algorithm that generates codewords
                    representing changes between current and previous input words using XOR.

        Args:
            s_in (list[int]): Current input binary word to encode
            c_prev (list[int]): Previous encoded codeword (unused in this scheme)
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Encoded transition word where 1=change, 0=no change from previous.
        """
        # Initialize with zeros on first decode
        if self.s_prev is None:
            self.s_prev = [0] * len(s_in)  

        s_copy = s_in[:] 

        # c = s_in ^ c_prev
        c = [int(s_copy[i]) ^ int(self.s_prev[i]) for i in range(len(s_copy))]

        logging.debug(f"Transtion Signaling encoded word:       {c}")
        return c
    

    def decode(self, c, M=None) -> list[int]:
        """
        Implements: Transition Signaling decoding algorithm that reconstructs original words
                    by XORing received transitions with previous decoded words.

        Args:
            c (list[int]): Received encoded transition word to decode
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Decoded original word reconstructed from transition information.
        """
        # Initialize with zeros on first decode
        if self.s_prev is None:
            self.s_prev = [0] * len(c)  
            
        # s_out = c ^ s_prev
        s_out = [int(c[i]) ^ int(self.s_prev[i]) for i in range(len(c))]
        
        # Store current output as previous for next decode
        self.s_prev = s_out[:]
        
        logging.debug(f"Transition Signaling decoded word:      {s_out}")
        return s_out
