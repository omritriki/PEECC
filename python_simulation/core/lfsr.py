"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from random import randint
import logging


# Description: Linear Feedback Shift Register implementation that generates k-bit words
#             using k parallel LFSRs with the same polynomial but different random seeds.
#             Each LFSR maintains its state between calls and uses polynomial feedback
#             to generate the next bit. The k-bit word is formed by taking one bit from
#             each LFSR.
#
# Inputs:     k: int - Number of bits to generate (number of parallel LFSRs)
#             polynomial: int - Feedback polynomial in binary form (default: x^13 + x^4 + x^3 + x + 1)
#                             represented as 0b10000000011011
#
# Outputs:    list[int] - Generated k-bit word, where each bit comes from a different LFSR
#                        Returns empty list if input validation fails

def lfsr(k, polynomial = 0b10000000011011) -> list[int]:

    # Get polynomial positions (where bits are 1)
    pol_positions = [i for i in range(14) if polynomial & (1 << i)]

    # Initialize or get LFSR states
    if not hasattr(lfsr, 'registers'):
        lfsr.registers = [[randint(0, 1) for _ in range(14)] for _ in range(k)]
        for i in range(k):
            # Ensure the LFSR is not initialized to zero
            while sum(lfsr.registers[i]) == 0:
                lfsr.registers[i] = [randint(0, 1) for _ in range(14)]
        logging.debug(f"Initialized {k} LFSRs with random seeds")

    # Update each LFSR
    for i in range(k):
        # Calculate new bit using polynomial feedback
        new_bit = 0
        for pos in pol_positions:
            new_bit ^= lfsr.registers[i][pos]
        # Shift left and append new bit
        lfsr.registers[i] = lfsr.registers[i][1:] + [new_bit]
    
    # Take last bit from each LFSR to form k-bit word
    s = [register[-1] for register in lfsr.registers]

    logging.debug(f"Generated a {k}-bit word:                {s}")
    return s
