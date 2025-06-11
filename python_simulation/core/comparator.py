"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging


def comparator(s_in, s_out) -> bool:
    """
    Implements: Validation of encoding/decoding fidelity by comparing the original input
                word with the decoded output word to detect any data corruption.

    Args:
        s_in (list[int]): Original input word before encoding
        s_out (list[int]): Decoded output word after transmission and decoding

    Returns:
        bool: True if words match exactly, False if any bit differs indicating error.
    """
    
    # Input validation
    if not isinstance(s_in, list) or not isinstance(s_out, list):
        logging.error("Invalid input: Both info_word and output must be lists")
        raise ValueError("Both info_word and output must be lists")
    if len(s_in) != len(s_out):
        logging.error(f"Length mismatch: s_in length={len(s_in)}, s_out length={len(s_out)}")
        raise ValueError("info_word and output must have the same length")

    # Comparison logic
    if s_in != s_out:
        logging.warning("Words do not match\n"
                f"          Input:                                          {s_in}\n"
                f"          Output:                                         {s_out}\n"
            )
        return False

    logging.debug("Input and output words match")
    return True

