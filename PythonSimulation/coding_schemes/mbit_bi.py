"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.base_coding_scheme import CodingScheme
from logging_config import configure_logging
import logging

# Configure logging
configure_logging()


class MbitBI(CodingScheme):
    name = "M-bit Bus Invert"

    def encode(self, s, c_prev, M):
        logging.info(f"Starting M-bit bus inversion with M={M}, s={s}, c_prev={c_prev}")
        n = len(s) + M
        segments = [n // M] * (n % M) + [n // M - 1] * (M - n % M)

        c = []

        start_s = 0
        start_c = 0
        for seg_len in segments:
            # Extract matching segments from s and c_prev
            seg_s = s[start_s:start_s + seg_len]
            seg_c = c_prev[start_c:start_c + seg_len + 1]

            logging.debug(f"Processing segment: seg_s={seg_s}, seg_c={seg_c}")

            # Call Check_Invert and append the modified segment to output
            new_segment = self.check_invert(seg_s, seg_c)
            c.extend(new_segment)

            logging.debug(f"New segment after inversion: {new_segment}")

            # Move start index for s and c
            start_s += seg_len
            start_c += seg_len + 1

        logging.info(f"Completed M-bit bus inversion. Resulting codeword: {c}")
        return c


    def decode(self, c, M):
        k = len(c) - M
        segments = [k // M + 1] * (k % M) + [k // M] * (M - k % M)
        s = []
        
        start_c = 0

        for seg_len in segments:
            # Extract matching segments from s and c_prev
            seg_c = c[start_c:start_c + seg_len + 1]

            logging.debug(f"Processing segment: seg_c = {seg_c}")

            # Invert the segment based on the last bit of seg_c
            new_segment = seg_c[:seg_len] if seg_c[-1] == 0 else [1 - bit for bit in seg_c[:seg_len]]
            s.extend(new_segment)

            logging.debug(f"New segment after inversion: {new_segment}")

            # Move start index for c
            start_c += seg_len + 1

        logging.info(f"Completed M-bit bus inversion. Resulting codeword: {c}")

        return s


    def check_invert(self, s, c_prev):
        logging.debug(f"Checking inversion for segment: s={s}, c_prev={c_prev}")
        A = len(s)

        curr_transitions = sum(1 for i in range(A) if s[i] != c_prev[i])

        logging.debug(f"Current transitions: {curr_transitions}, Threshold: {A // 2}")

        if curr_transitions > A // 2 or (curr_transitions == A // 2 and c_prev[-1] == 1):
            # Invert the segment
            s = [bit ^ 1 for bit in s]  # Flip all bits using list comprehension
            s.append(1)  # Set INV bit to 1
            logging.info(f"Segment inverted: {s}")
        else:
            s.append(0)  # Set INV bit to 0 (if no inversion)
            logging.info(f"Segment not inverted: {s}")

        return s