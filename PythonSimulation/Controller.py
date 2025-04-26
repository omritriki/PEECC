"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
import Encoder
import Generator
import Transition_Count

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Description: Controls the encoding process, testing both random and all possible
#              k-bit input words while tracking transition statistics
# Inputs:
#              None
# Outputs:
#              Logs max and average transitions for random words and all possible words

def Controller():
    k = 16
    t = 5000
    M = 3
    n = k + M

    # Ask the user for their choice
    choice = input("Simulate t random words (1) or Simulate all possible words starting from 0 (2)? ")

    if choice == '1':
        logging.info("Simulating t random words")
        # Reset counters and bus
        c_prev = [0] * n
        Transition_Count.Transition_Count(c_prev, c_prev, RESET=True)

        # Simulate t random words
        for i in range(t):
            s = Generator.generate(k)
            c = Encoder.mBitBusInvert(s, c_prev, M)
            Transition_Count.Transition_Count(c, c_prev)
            c_prev = c

        max_transitions, avg_transitions = Transition_Count.Transition_Count(c_prev, c_prev)
        logging.info(f"Max transitions: {max_transitions}")
        logging.info(f"Avg transitions: {avg_transitions / t}")

    elif choice == '2':
        logging.info("Simulating all possible words starting from 0")
        # Reset counters and bus
        c_prev = [0] * n
        Transition_Count.Transition_Count(c_prev, c_prev, RESET=True)

        # Simulate all possible words starting from 0
        for j in range((2 ** k) - 1):
            c_prev = [0] * n
            s = [int(bit) for bit in format(j, f'0{k}b')]
            c = Encoder.mBitBusInvert(s, c_prev, M)
            Transition_Count.Transition_Count(c, c_prev)

        max_transitions, avg_transitions = Transition_Count.Transition_Count(c_prev, c_prev)
        logging.info(f"Max transitions: {max_transitions}")
        logging.info(f"Avg transitions: {avg_transitions / ((2 ** k) - 1)}")

    else:
        logging.warning("Invalid choice. Please select either 1 or 2.")


if __name__ == '__main__':
    Controller()
