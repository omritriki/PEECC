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


# Description: Generates a k-bit binary number based on the specified mode.
#              Mode 1 generates a random binary number.
#              Mode 2 generates a binary number using an LFSR with the given seed.
#              Mode 3 generates a binary number from the integer i. 
# Inputs:
#              k (int): Number of bits in the generated binary number.
#              mode (int): Mode of generation (1=random, 2=LFSR, 3=from integer).
#              i (int): Integer to convert to binary (used in mode 3).
#              seed (list[int]): Seed for LFSR (used in mode 2).
# Outputs:
#              s (list[int]): A list of k binary digits.

def generate(k, mode = 1, i = 0, seed = 0) -> list[int]:
    if k <= 0:
        logging.error(f"Invalid input: n={k}. Number of bits must be positive")
        return []

    if mode == 1:
        # Generate a random n-bit binary number
        random_num = randint(0, (2 ** k) - 1)
        s = [int(bit) for bit in format(random_num, f'0{k}b')]  

    elif mode == 2:
        # Generate an LFSR with the given polynomial ###### not SEED!!!

        # Old LFSR code
        new_bit = seed[0] ^ seed[1]  
        lfsr_out = seed[1:]  
        s = lfsr_out + [new_bit]  

        # New LFSR code
        #s = lfsr.lfsr(k)

    elif mode == 3:
        # Generate i as a k-bit binary number
        s = [int(bit) for bit in format(i, f'0{k}b')]

    logging.debug(f"Generated a {k}-bit word:                {s}")
    return s
