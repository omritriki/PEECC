"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import random


def generate_error(n, error_probability=0.1) -> list[int]:
    """
    Implements: Probabilistic single-bit error injection for simulating transmission errors
                in communication channels to test error detection and correction capabilities.

    Args:
        n (int): Length of the error vector to generate
        error_probability (float): Probability of introducing a single bit error (default: 0.1)

    Returns:
        list[int]: An n-bit error vector where all bits are 0 if no error occurs,
                   or a single bit is set to 1 at a random position if error occurs.
    """
    error_vector = [0] * n

    # Decide whether to introduce an error based on the probability
    if random.random() > error_probability:
        # No error introduced
        return error_vector

    # Generate a n-bit error vector with a single random bit set to 1
    random_index = random.randint(0, n - 1)
    error_vector[random_index] = 1

    return error_vector