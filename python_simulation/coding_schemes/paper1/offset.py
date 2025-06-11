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


class Offset(CodingScheme):
    """
    Implements: Offset encoding scheme that transmits differences between consecutive words
                using two's complement arithmetic to reduce transitions for sequential data patterns.

    Args:
        None (inherits from CodingScheme base class)

    Returns:
        None (class definition)
    """
    name = "Offset"
    supports_errors = False
    

    def get_bus_size(self, k, M=None) -> int:
        """
        Implements: Bus width calculation for Offset scheme, which maintains the same width
                    as the input since only differences are transmitted.

        Args:
            k (int): Number of input data bits
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            int: Bus width equal to input width (k bits).
        """
        return k


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        """
        Implements: Offset encoding algorithm that calculates the difference between current
                    and previous words using two's complement arithmetic.

        Args:
            s_in (list[int]): Current input binary word to encode
            c_prev (list[int]): Previous encoded codeword (unused in this scheme)
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Encoded difference word (s_current - s_previous) in two's complement.
        """
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
        """
        Implements: Offset decoding algorithm that reconstructs original words by adding
                    received differences to previous words using two's complement arithmetic.

        Args:
            c (list[int]): Received encoded difference word to decode
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Decoded original word (c_current + s_previous) in two's complement.
        """
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
