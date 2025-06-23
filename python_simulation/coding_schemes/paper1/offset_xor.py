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


class Offset_XOR(CodingScheme):
    """
    Implements: Hybrid encoding scheme that combines offset coding with XOR operations
                to reduce transitions by using differences between consecutive words XORed with previous codewords.

    Args:
        None (inherits from CodingScheme base class)

    Returns:
        None (class definition)
    """
    name = "Offset-XOR"
    supports_errors = False
    

    def get_bus_size(self, k, M=None) -> int:
        """
        Implements: Bus width calculation for Offset-XOR scheme, which maintains the same
                    width as input since encoded differences preserve the original bit count.

        Args:
            k (int): Number of input data bits
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            int: Bus width equal to input width (k bits).
        """
        return k 


    def encode(self, s_in, c_prev, M=None) -> list[int]:
        """
        Implements: Offset-XOR encoding algorithm that calculates differences between consecutive
                    words and XORs the result with the previous codeword for transition reduction.

        Args:
            s_in (list[int]): Current input binary word to encode
            c_prev (list[int]): Previous encoded codeword for XOR operation
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Encoded word as c_prev XOR (s_current - s_previous).
        """
        if self.s_prev is None:
            self.s_prev = [0] * len(s_in)  

        # c = c_prev xor (s - s_prev)

        self.c_prev = c_prev[:]
        
        s_previous = int(''.join(map(str, self.s_prev)), 2)
        s_new = int(''.join(map(str, s_in)), 2)
        
        sub = (s_new - s_previous) % (2 ** len(s_in))
        
        offset_binary = [int(x) for x in format(sub, f'0{len(s_in)}b')]
        
        c = [a ^ b for a, b in zip(c_prev, offset_binary)]

        logging.debug(f"Offset-XOR encoded word:                {c}")

        return c
    

    def decode(self, c, M=None) -> list[int]:
        """
        Implements: Offset-XOR decoding algorithm that reconstructs original words by XORing
                    received codewords with previous codewords and adding to previous decoded words.

        Args:
            c (list[int]): Received encoded codeword to decode
            M (int): Unused parameter for compatibility (default: None)

        Returns:
            list[int]: Decoded original word as (c_prev XOR c) + s_previous.
        """
        if self.s_prev is None:
            self.s_prev = [0] * len(c)  
            
        # s = (c_prev xor c) + s_prev

        xor_result = [a ^ b for a, b in zip(c, self.c_prev)]
        s_prev_int = int(''.join(map(str, self.s_prev)), 2)
        xor_result_int = int(''.join(map(str, xor_result)), 2)
        s_out_int = (s_prev_int + xor_result_int) % (2 ** len(c))
        
        s = [int(x) for x in format(s_out_int, f'0{len(c)}b')]
        
        self.s_prev = s[:]
        
        logging.debug(f"Offset-XOR decoded word:                {s}")

        return s
