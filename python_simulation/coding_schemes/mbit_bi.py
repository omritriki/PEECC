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


class MbitBI(CodingScheme):
    """
    Implements: M-bit Bus Invert coding scheme that divides input words into M segments
                and selectively inverts segments to minimize bus transitions and reduce power consumption.

    Args:
        None (inherits from CodingScheme base class)

    Returns:
        None (class definition)
    """
    name = "M-bit Bus-Invert"


    def get_bus_size(self, k, M) -> int:
        """
        Implements: Bus width calculation for M-bit Bus Invert scheme, accounting for
                    original data bits plus inversion control bits.

        Args:
            k (int): Number of input data bits
            M (int): Number of segments for bus inversion

        Returns:
            int: Total bus width required (k + M bits).
        """
        n = k + M
        return n


    def encode(self, s, c_prev, M) -> list[int]:
        """
        Implements: M-bit Bus Invert encoding algorithm that segments input words and
                    selectively inverts segments to minimize transitions from previous codeword.

        Args:
            s (list[int]): Input binary word to encode
            c_prev (list[int]): Previous encoded codeword for transition comparison
            M (int): Number of segments for bus inversion

        Returns:
            list[int]: Encoded codeword with original data and inversion control bits.
        """
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
        """
        Implements: M-bit Bus Invert decoding algorithm that reconstructs original words
                    by checking inversion flags and selectively inverting segments.

        Args:
            c (list[int]): Received encoded codeword to decode
            M (int): Number of segments used in encoding

        Returns:
            list[int]: Decoded binary word matching the original input.
        """
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
        """
        Implements: Segment inversion decision logic that compares transition count with
                    and without inversion to minimize power consumption.

        Args:
            s (list[int]): Current segment to analyze
            c_prev (list[int]): Previous segment for transition comparison

        Returns:
            list[int]: Segment with inversion flag appended (1=inverted, 0=not inverted).
        """
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
        """
        Implements: Theoretical calculation of expected average transitions for M-bit Bus Invert
                    scheme using combinatorial analysis and probability theory.

        Args:
            k (int): Number of input data bits
            M (int): Number of segments for bus inversion

        Returns:
            float: Expected average number of transitions per codeword transmission.
        """
        def calc_segment_average(n):
            if (n - 1) % 2 == 0:
                return calc_segment_average(n + 1) - 0.5
            if (n - 1) % 2 == 1:
                return (n / (2 ** (n + 1))) * (2 ** n - comb(n, n // 2))
        
        n = k + M
        expected_value = (n % M) * calc_segment_average(n // M + 1) + \
                        (M - n % M) * calc_segment_average(n // M)
        
        return round(expected_value, 4)