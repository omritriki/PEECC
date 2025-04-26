"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Description: Checks if the input to the encoder is the same as the output of the decoder
# Inputs:
#              info_word (array): Initial information word (length - k)
#              output (array): Decoded word (length - k)
# Outputs:
#              isEqual (bool): True only if info_word == output
def Comparator(s_in, s_out):
    
    # Input validation
    if not isinstance(s_in, list) or not isinstance(s_out, list):
        logging.error("Invalid input: Both info_word and output must be lists.")
        raise ValueError("Both info_word and output must be lists.")
    if len(s_in) != len(s_out):
        logging.error(f"Length mismatch: info_word length={len(s_in)}, output length={len(s_out)}")
        raise ValueError("info_word and output must have the same length.")

    logging.info(f"Comparing info_word={s_in} with output={s_out}")

    # Comparison logic
    if s_in != s_out:
        logging.info("Words do not match.")
        return False

    logging.info("Words match.")
    return True

