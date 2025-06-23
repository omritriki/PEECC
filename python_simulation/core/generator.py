"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from random import randint
from core import lfsr
import logging


def generate(k, mode = 1, i = 0) -> list[int]:
    """
    Implements: Binary word generation using multiple methods: random generation,
                LFSR-based pseudo-random sequences, or exhaustive enumeration.

    Args:
        k (int): Number of bits in the generated binary word
        mode (int): Generation mode (1=random, 2=LFSR, 3=exhaustive enumeration)
        i (int): Integer value to convert to binary (used in mode 3)

    Returns:
        list[int]: A k-bit binary word as a list of integers (0s and 1s).
    """

    if mode == 1:
        # Generate a random n-bit binary number
        random_num = randint(0, (2 ** k) - 1)
        s = [int(bit) for bit in format(random_num, f'0{k}b')]  

    elif mode == 2:
        # Generate an LFSR with the given polynomial ###### not SEED!!!

        # Old LFSR code
        #new_bit = seed[0] ^ seed[1]  
        #lfsr_out = seed[1:]  
        #s = lfsr_out + [new_bit]  

        # New LFSR code
        s = lfsr.lfsr(k)

    elif mode == 3:
        # Generate i as a k-bit binary number
        s = [int(bit) for bit in format(i, f'0{k}b')]

    logging.debug(f"Generated a {k}-bit word:                {s}")
    return s
