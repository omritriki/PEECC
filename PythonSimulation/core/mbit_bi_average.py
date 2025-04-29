import numpy as np
from math import comb

def mbit_bi_average(k, M):
    n = k + M

    # Use numpy for efficient calculations
    expected_value = (n % M) * calc_bi_average(n // M + 1) + (M - n % M) * calc_bi_average(n // M)

    return expected_value


def calc_bi_average(n):
    if (n - 1) % 2 == 0:
        return calc_bi_average(n + 1) - 0.5
    if (n - 1) % 2 == 1:
        # Use numpy for precise calculations
        bi_average = (n / (2 ** (n + 1))) * (2 ** n - comb(n, n // 2))
        return bi_average
