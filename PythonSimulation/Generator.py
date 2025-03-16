"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import random


# Description: Generates a random n-bit binary number and returns it as a list of bits
# Inputs:
#              n (int): Number of bits in the generated binary number
# Outputs:
#              s (array): An array of n binary digits

def generate(n):
    random_num = random.randint(0, (2 ** n) - 1)
    s = [int(bit) for bit in format(random_num, f'0{n}b')]  # Convert each bit to an integer
    return s
