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
import Decoder
import Generator
import Comparator
import Transition_Count

# Configure logging for external modules (logs go to the file)
file_handler = logging.FileHandler("simulation_logs.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler]  # Logs from other modules go only to the file
)

# Configure a separate logger for the Controller (logs go to the terminal)
controller_logger = logging.getLogger("Controller")
controller_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

controller_logger.addHandler(console_handler)

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
    choice = input(f"Simulate {t} random words (1) or Simulate all possible words starting from 0 (2)? ")
    print()  
    controller_logger.info(f"Parameters: k = {k}, M = {M}, n = {n}")
    print()  

    if choice == '1':
        controller_logger.info(f"Simulating {t} random words")
        # Reset counters and bus
        c_prev = [0] * n
        Transition_Count.Transition_Count(c_prev, c_prev, RESET=True)

        # Simulate t random words
        for i in range(t):
            # Generate a random k-bit binary number
            s_in = Generator.generate(k, 1)

            # Apply M-bit bus inversion encoding
            c = Encoder.mBitBusInvert(s_in, c_prev, M)

            # Count transitions
            Transition_Count.Transition_Count(c, c_prev)

            # Encode the new codeword
            s_out = Decoder.Decoder(c, M)

            # Check if the new codeword is different from the previous one
            if not Comparator.Comparator(s_in, s_out):
                controller_logger.warning(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")
                print(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")
                break

            # Update the previous codeword
            c_prev = c

        max_transitions, avg_transitions = Transition_Count.Transition_Count(c_prev, c_prev)
        print()  
        controller_logger.info(f"Max transitions: {max_transitions}")
        controller_logger.info(f"Avg transitions: {avg_transitions / t}")
        print()  

    elif choice == '2':
        controller_logger.info("Simulating all possible words starting from 0")
        # Reset counters and bus
        c_prev = [0] * n
        Transition_Count.Transition_Count(c_prev, c_prev, RESET=True)

        # Simulate all possible words starting from 0
        for j in range((2 ** k) - 1):
            # Reset the bus for each new word
            c_prev = [0] * n

            # Generate the k-bit binary number from j
            s = Generator.generate(k, mode=2, i=j)

            # Apply M-bit bus inversion encoding
            c = Encoder.mBitBusInvert(s, c_prev, M)

            # Count transitions
            Transition_Count.Transition_Count(c, c_prev)

            # Encode the new codeword

        max_transitions, avg_transitions = Transition_Count.Transition_Count(c_prev, c_prev)
        print()  
        controller_logger.info(f"Max transitions: {max_transitions}")
        controller_logger.info(f"Avg transitions: {avg_transitions / ((2 ** k) - 1)}")
        print()  

    else:
        controller_logger.warning("Invalid choice. Please select either 1 or 2.")

    controller_logger.info("Simulation ended")
    print()


if __name__ == '__main__':
    Controller()
