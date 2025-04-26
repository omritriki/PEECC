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
def Comparator(info_word, output):
    # Input validation
    if not isinstance(info_word, list) or not isinstance(output, list):
        logging.error("Invalid input: Both info_word and output must be lists.")
        raise ValueError("Both info_word and output must be lists.")
    if len(info_word) != len(output):
        logging.error(f"Length mismatch: info_word length={len(info_word)}, output length={len(output)}")
        raise ValueError("info_word and output must have the same length.")

    logging.info(f"Comparing info_word={info_word} with output={output}")

    # Comparison logic
    for i in range(len(info_word)):
        if info_word[i] != output[i]:
            logging.info("Words do not match.")
            return False

    logging.info("Words match.")
    return True

