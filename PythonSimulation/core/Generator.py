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

def generate(k, mode = 1, i = 0):
    if k <= 0:
        logging.warning(f"Invalid input: n={k}. Number of bits must be positive.")
        return []

    if mode == 1:
        # Generate a random n-bit binary number
        logging.info(f"Generating a random {k}-bit binary number.")
        random_num = randint(0, (2 ** k) - 1)
        s = [int(bit) for bit in format(random_num, f'0{k}b')]  # Convert each bit to an integer

    elif mode == 2:
        # Generate i as a k-bit binary number
        logging.info(f"Generating a {k}-bit binary number from i={i}.")
        s = [int(bit) for bit in format(i, f'0{k}b')]

        

    logging.info(f"Generated {k}-bit binary number: {s}")
    return s
