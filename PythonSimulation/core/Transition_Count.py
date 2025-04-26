"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from logging_config import configure_logging
import logging

# Configure logging
configure_logging()

# Global variables
avg_transitions = 0
max_transitions = -1


# Description:  Counts bit transitions between the current codeword c and previous codeword c_prev,
#               updating global max and average transition counts
# Inputs:
#               c (array): Current codeword (bits)
#               c_prev (array): Previous codeword (bits)
#               RESET (bool): Resets counters if True
# Outputs:
#               max_transitions (int): Highest recorded transitions
#               avg_transitions (int): Cumulative transition count

def Transition_Count(c=0, c_prev=0, RESET=False):
    global avg_transitions
    global max_transitions
    curr_transitions = 0

    if RESET:
        avg_transitions = 0
        max_transitions = -1
        logging.info("Transition counters have been reset.")

    try:
        # Count transitions
        for i in range(len(c)):
            if c[i] != c_prev[i]:
                curr_transitions += 1
            c_prev[i] = c[i]

        # Update global average and max transition counts
        avg_transitions += curr_transitions
        if curr_transitions > max_transitions:
            max_transitions = curr_transitions

        logging.debug(f"Current transitions: {curr_transitions}")
        logging.info(f"Updated max transitions: {max_transitions}")
        logging.info(f"Updated average transitions: {avg_transitions}")

    except IndexError as e:
        logging.error("Index out of range while processing transitions.", exc_info=True)
    except Exception as e:
        logging.critical("Unexpected error occurred.", exc_info=True)

    return max_transitions, avg_transitions
