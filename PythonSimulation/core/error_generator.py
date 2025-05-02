"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import random


# Description: Introduces an error into a given binary vector based on a specified error probability
#              If an error is introduced, a single random bit in the vector is flipped
# Inputs:
#              input_vector (list[int]): The binary vector to which the error may be applied
#              error_probability (float): The probability of introducing an error (default is 0.1)
# Outputs:
#              output_vector (list[int]): The binary vector after applying the error (if any)

def error_generator(input_vector, error_probability=0.1):
    n = len(input_vector)

    # Decide whether to introduce an error based on the probability
    if random.random() > error_probability:
        # No error introduced, return the input vector as is
        return input_vector

    # Generate a n-bit error vector with a single random bit set to 1
    error_vector = [0] * n
    random_index = random.randint(0, n - 1)
    error_vector[random_index] = 1

    # Perform XOR operation between input vector and error vector
    output_vector = [input_bit ^ error_bit for input_bit, error_bit in zip(input_vector, error_vector)]

    return output_vector