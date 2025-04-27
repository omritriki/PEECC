"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
from coding_schemes import mbit_bi, dapbi
from core import generator
from core import comparator
from core import transition_count

# Description: Controls the encoding process, testing both random and all possible
#              k-bit input words while tracking transition statistics
# Inputs:
#              None
# Outputs:
#              Logs max and average transitions for random words and all possible words

def controller():
    k = 32
    t = 50000
    M = 5
    n = k + M

    controller_logger = logging.getLogger("Controller")

    coding_scheme = mbit_bi.MbitBI()

    encoder = coding_scheme.encode
    decoder = coding_scheme.decode

    # Ask the user for their choice
    choice = input(f"Simulate {t} random words (1) or Simulate all possible words starting from 0 (2)? ")
    print()  
    controller_logger.info(f"Parameters: k = {k}, M = {M}, n = {n}")
    print()  

    if choice == '1':
        controller_logger.info(f"Simulating {t} random words")
        # Reset counters and bus
        c_prev = [0] * n
        transition_count.transition_count(c_prev, c_prev, RESET=True)

        # Simulate t random words
        for i in range(t):
            # Generate a random k-bit binary number
            s_in = generator.generate(k, 1)

            # Apply M-bit bus inversion encoding
            c = encoder(s_in, c_prev, M)

            # Count transitions
            transition_count.transition_count(c, c_prev)

            # Encode the new codeword
            s_out = decoder(c, M)

            # Check if the new codeword is different from the previous one
            if not comparator.comparator(s_in, s_out):
                controller_logger.warning(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")
                break

            # Update the previous codeword
            c_prev = c

        max_transitions, avg_transitions = transition_count.transition_count(c_prev, c_prev)
        print()  
        controller_logger.info(f"Max transitions: {max_transitions}")
        controller_logger.info(f"Avg transitions: {avg_transitions / t}")
        print()  

    elif choice == '2':
        controller_logger.info("Simulating all possible words starting from 0")
        # Reset counters and bus
        c_prev = [0] * n
        transition_count.transition_count(c_prev, c_prev, RESET=True)

        # Simulate all possible words starting from 0
        for j in range((2 ** k) - 1):
            # Generate the k-bit binary number from j
            s_in = generator.generate(k, mode=2, i=j)

            # Apply M-bit bus inversion encoding
            c = encoder(s_in, c_prev, M)

            # Count transitions
            transition_count.transition_count(c, c_prev)

            # Encode the new codeword
            s_out = decoder(c, M)

            # Check if the new codeword is different from the previous one
            if not comparator.comparator(s_in, s_out):
                controller_logger.warning(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")
                break
            
            # Update the previous codeword
            c_prev = [0] * n


        max_transitions, avg_transitions = transition_count.transition_count(c_prev, c_prev)
        print()  
        controller_logger.info(f"Max transitions: {max_transitions}")
        controller_logger.info(f"Avg transitions: {avg_transitions / ((2 ** k) - 1)}")
        print()  

    elif choice == '3':
        controller_logger.info("Simulating all possible words starting from 0")
        # Reset counters and bus
        c_prev = [0] * n
        transition_count.transition_count(c_prev, c_prev, RESET=True)

        seed = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

        for j in range(t):
            # print(f"seed: {seed}")
            # Generate the k-bit binary number from j
            s_in = generator.generate(k, mode=3, i=j, seed=seed)
            seed = s_in

            # Apply M-bit bus inversion encoding
            c = encoder(s_in, c_prev, M)

            # Count transitions
            transition_count.transition_count(c, c_prev)

            # Encode the new codeword
            s_out = decoder(c, M)

            # Check if the new codeword is different from the previous one
            if not comparator.comparator(s_in, s_out):
                controller_logger.warning(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")
                break
            
            # Update the previous codeword
            c_prev = c


        max_transitions, avg_transitions = transition_count.transition_count(c_prev, c_prev)
        print()  
        controller_logger.info(f"Max transitions: {max_transitions}")
        print(f"Max transitions: {max_transitions}")
        controller_logger.info(f"Avg transitions: {avg_transitions / t}")
        print(f"Avg transitions: {avg_transitions / t}")
        print()  

    else:
        controller_logger.warning("Invalid choice. Please select either 1 or 2.")

    controller_logger.info("Simulation ended")
    print()

def setup_file_logging():
    """Configure logging for external modules (logs go to the file)."""
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

def setup_controller_logging():
    """Configure a separate logger for the Controller (logs go to the terminal)."""
    controller_logger = logging.getLogger("Controller")
    controller_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    controller_logger.addHandler(console_handler)
    return controller_logger


if __name__ == '__main__':
    controller()
