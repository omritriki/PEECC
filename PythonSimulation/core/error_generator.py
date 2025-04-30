import random


def error_generator(input_vector):
    n = len(input_vector)

    # Generate a n-bit error vector with a single random bit set to 1
    error_vector = [0] * n
    random_index = random.randint(0, n - 1)
    error_vector[random_index] = 1

    # Perform XOR operation between input vector and error vector
    output_vector = [input_bit ^ error_bit for input_bit, error_bit in zip(input_vector, error_vector)]

    return output_vector