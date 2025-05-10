"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import random


# Description: Introduces 
# Inputs:

# Outputs:

def error_generator(n, error_probability=0.1) -> list[int]:
    error_vector = [0] * n

    # Decide whether to introduce an error based on the probability
    if random.random() > error_probability:
        # No error introduced
        return error_vector

    # Generate a n-bit error vector with a single random bit set to 1
    random_index = random.randint(0, n - 1)
    error_vector[random_index] = 1

    return error_vector