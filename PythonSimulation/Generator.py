"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
from random import randint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Description: Generates a random n-bit binary number and returns it as a list of bits
# Inputs:
#              n (int): Number of bits in the generated binary number
# Outputs:
#              s (array): An array of n binary digits

def generate(n):
    if n <= 0:
        logging.warning(f"Invalid input: n={n}. Number of bits must be positive.")
        return []

    random_num = randint(0, (2 ** n) - 1)
    s = [int(bit) for bit in format(random_num, f'0{n}b')]  # Convert each bit to an integer

    logging.info(f"Generated {n}-bit binary number: {s}")
    return s
