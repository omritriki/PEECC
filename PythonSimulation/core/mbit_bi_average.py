"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from math import comb


# Description: Calculates the average number of bit transitions for M-bit Bus-Invert Code.
# Inputs:
#              k (int): Number of input bits.
#              M (int): Number of segments for bus inversion.
# Outputs:
#              float: The expected average number of bit transitions.

def mbit_bi_average(k, M):
    n = k + M

    expected_value = (n % M) * calc_bi_average(n // M + 1) + (M - n % M) * calc_bi_average(n // M)

    return expected_value


def calc_bi_average(n):
    if (n - 1) % 2 == 0:
        return calc_bi_average(n + 1) - 0.5
    if (n - 1) % 2 == 1:
        bi_average = (n / (2 ** (n + 1))) * (2 ** n - comb(n, n // 2))
        return bi_average
