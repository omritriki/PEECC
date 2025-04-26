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


# Description: The Decoder extracts the original information word from the received bus word,
#              reversing the encoding process performed by the Encoder.
# Inputs:
#              c (array): Modified codeword after M-bit bus inversion
#
#
# Outputs:
#

def Decoder(c, M):
    k = len(c) - M
    # n = len(c)
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








    return 0
