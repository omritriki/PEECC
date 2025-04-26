"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging

# Configure logging to write to the log file
file_handler = logging.FileHandler("simulation_logs.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler]  # Logs go only to the file
)


# Description: Applies M-bit bus inversion encoding to the input sequence s,
#              dividing it into M segments and updating based on previous codeword c_prev
# Inputs:
#              s (array): New information word (length - k)
#              c_prev (array): Previous codeword (length - n)
#              M (int): Number of segments for bus inversion
# Outputs:
#              c (array): Modified codeword after M-bit bus inversion

def mBitBusInvert(s, c_prev, M):
    logging.info(f"Starting M-bit bus inversion with M={M}, s={s}, c_prev={c_prev}")
    n = len(s)
    segments = [n // M + 1] * (n % M) + [n // M] * (M - n % M)

    c = []

    start_s = 0
    start_c = 0
    for seg_len in segments:
        # Extract matching segments from s and c_prev
        seg_s = s[start_s:start_s + seg_len]
        seg_c = c_prev[start_c:start_c + seg_len + 1]

        logging.debug(f"Processing segment: seg_s={seg_s}, seg_c={seg_c}")

        # Call Check_Invert and append the modified segment to output
        new_segment = Check_Invert(seg_s, seg_c)
        c.extend(new_segment)

        logging.debug(f"New segment after inversion: {new_segment}")

        # Move start index for s and c
        start_s += seg_len
        start_c += seg_len + 1

    logging.info(f"Completed M-bit bus inversion. Resulting codeword: {c}")
    return c


# Description: Determines whether to invert the segment s based on
#              transition count compared to the previous codeword c_prev.
#              If inverted, an INV bit (1) is appended; otherwise, 0 is appended
# Inputs:
#              s (array): Current segment of the codeword
#              c_prev (array): Previous segment including the last INV bit
# Outputs:
#              s (array): Modified segment, potentially inverted, with an appended INV bit

def Check_Invert(s, c_prev):
    logging.debug(f"Checking inversion for segment: s={s}, c_prev={c_prev}")
    A = len(s)
    curr_transitions = 0

    for i in range(A):
        if s[i] != c_prev[i]:
            curr_transitions += 1

    logging.debug(f"Current transitions: {curr_transitions}, Threshold: {A // 2}")

    if curr_transitions > A // 2 or (curr_transitions == A // 2 and c_prev[-1] == 1):
        # Invert the segment
        for i in range(A):
            s[i] = 1 if s[i] == 0 else 0
        s.append(1)  # Set INV bit to 1
        logging.info(f"Segment inverted: {s}")
    else:
        s.append(0)  # Set INV bit to 0 (if no inversion)
        logging.info(f"Segment not inverted: {s}")

    return s
