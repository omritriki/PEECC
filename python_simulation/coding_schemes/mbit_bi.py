"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.base_coding_scheme import CodingScheme
import logging


# Description: Implements the M-bit Bus Invert (MbitBI) encoding and decoding scheme.
#              The encoding process divides the input binary sequence into segments of length M,
#              compares the number of transitions in each segment to half its length, and inverts
#              the segment if doing so reduces the number of transitions. The decoding process
#              reverses this operation to recover the original binary sequence.
# Inputs:
#              s (list[int]): The input binary sequence to be encoded.
#              c_prev (list[int]): The previous encoded sequence for transition comparison.
#              M (int): The number of segments for bus inversion.
# Outputs:
#              encode(): The encoded binary sequence with minimized transitions.
#              decode(): The decoded binary sequence, recovering the original input.

class MbitBI(CodingScheme):
    name = "M-bit Bus-Invert"

    def get_bus_size(self, k, M):
        n = k + M
        return n

    def encode(self, s, c_prev, M):
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
            new_segment = self.check_invert(seg_s, seg_c)
            c.extend(new_segment)

            # Move start index for s and c
            start_s += seg_len
            start_c += seg_len + 1

        logging.debug(f"M-bit BI encoded word:                  {c}")

        return c


    def decode(self, c, M):
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


    def check_invert(self, s, c_prev):
        A = len(s)

        curr_transitions = sum(1 for i in range(A) if s[i] != c_prev[i])

        if curr_transitions > A // 2 or (curr_transitions == A // 2 and c_prev[-1] == 1):
            # Invert the segment
            s = [bit ^ 1 for bit in s]  
            s.append(1)  
        else:
            s.append(0)  
        return s