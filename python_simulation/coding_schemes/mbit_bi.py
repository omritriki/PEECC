"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.base_coding_scheme import CodingScheme
from math import comb
import logging


# Description: M-bit Bus Invert (MbitBI) scheme that divides input into M segments
#             and selectively inverts segments to reduce transitions.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word
#             M: int - Number of segments for bus inversion
#
# Outputs:    list[int] - Encoded/decoded word
#             encode(): Original bits with inversion flags
#             decode(): Original word recovered using inversion flags

class MbitBI(CodingScheme):
    name = "M-bit Bus-Invert"


    def get_bus_size(self, k, M) -> int:
        n = k + M
        return n


    def encode(self, s, c_prev, M) -> list[int]:
        n = len(s) + M
        segments = [n // M] * (n % M) + [n // M - 1] * (M - n % M)

        c = []

        start_s = 0
        start_c = 0
        for seg_len in segments:
            # Extract matching segments from s and c_prev
            seg_s = s[start_s:start_s + seg_len]
            seg_c = c_prev[start_c:start_c + seg_len + 1]

            # Call Check_Invert and append the modified segment to output
            new_segment = self._check_invert(seg_s, seg_c)
            c.extend(new_segment)

            # Move start index for s and c
            start_s += seg_len
            start_c += seg_len + 1

        logging.debug(f"M-bit BI encoded word:                  {c}")
        return c


    def decode(self, c, M) -> list[int]:
        k = len(c) - M
        segments = [k // M + 1] * (k % M) + [k // M] * (M - k % M)
        s = []
        
        start_c = 0

        for seg_len in segments:
            # Extract matching segments from s and c_prev
            seg_c = c[start_c:start_c + seg_len + 1]

            # Invert the segment based on the last bit of seg_c
            new_segment = seg_c[:seg_len] if seg_c[-1] == 0 else [1 - bit for bit in seg_c[:seg_len]]
            s.extend(new_segment)

            # Move start index for c
            start_c += seg_len + 1

        logging.debug(f"M-bit BI encoded word:                  {s}")
        return s


    def _check_invert(self, s, c_prev):
        A = len(s)

        curr_transitions = sum(1 for i in range(A) if s[i] != c_prev[i])

        if curr_transitions > A // 2 or (curr_transitions == A // 2 and c_prev[-1] == 1):
            # Invert the segment
            s = [bit ^ 1 for bit in s]  
            s.append(1)  
        else:
            s.append(0)  
        return s
    
    
    def calculate_expected_average(self, k, M):
        def calc_segment_average(n):
            if (n - 1) % 2 == 0:
                return calc_segment_average(n + 1) - 0.5
            if (n - 1) % 2 == 1:
                return (n / (2 ** (n + 1))) * (2 ** n - comb(n, n // 2))
        
        n = k + M
        expected_value = (n % M) * calc_segment_average(n // M + 1) + \
                        (M - n % M) * calc_segment_average(n // M)
        
        return round(expected_value, 4)