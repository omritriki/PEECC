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
from core import mbit_bi_average
from core import error_generator
from logging_config import configure_logging
import argparse

# Description: Controls the encoding process, testing both random and all possible
#              k-bit input words while tracking transition statistics
# Inputs:
#              None
# Outputs:
#              Logs max and average transitions for random words and all possible words

def controller():
    k = 16
    t = 1000
    M = 3

    controller_logger = logging.getLogger("Controller")

    coding_scheme = mbit_bi.MbitBI()
    n = k + M
    # coding_scheme = dapbi.DAPBI()
    # n = 2 * k + 3

    global encoder, decoder
    encoder = coding_scheme.encode
    decoder = coding_scheme.decode

    # Ask the user for their choice
    choice = input(f"Simulate {t} random words (1), Simulate all possible words starting from 0 (2), or Simulate using LFSR (3)? ")
    print()  
    controller_logger.info(f"Parameters: k = {k}, M = {M}, n = {n}")

    if choice == '1':
        controller_logger.debug(f"Simulating {t} random words")
        simulate(k, t, M, n, mode=1)

    elif choice == '2':
        controller_logger.debug("Simulating all possible words starting from 0")
        simulate(k, t, M, n, mode=2)

    elif choice == '3':
        controller_logger.debug("Simulating using LFSR")
        seed = generate_seed(k)
        simulate(k, t, M, n, mode=3, seed=seed)

    else:
        controller_logger.warning("Invalid choice. Please select either 1, 2, or 3.")

    controller_logger.debug("Simulation ended")


def generate_seed(k):
    # The seed is x^n + x^(n-1) +x^0
    seed = [0] * k

    for i in [0, 1, -1]:
        seed[i] = 1

    return seed


def simulate(k, t, M, n, mode, seed=None):
    controller_logger = logging.getLogger("Controller")
    
    valid = validate_input(k, M, n, mode)
    if not valid:
        controller_logger.error("Invalid input parameters. Exiting simulation.")
        return
    
    c_prev = [0] * n  # Initialize the bus
    transition_count.transition_count(c_prev, c_prev, RESET=True)  # Reset counters

    for i in range(t if mode == 1 or mode == 3 else (2 ** k)):
        # Generate input word based on the mode
        if mode == 1:
            s_in = generator.generate(k, mode=1)  # Random generation
        elif mode == 2:
            c_prev = [0] * n  # Initialize the bus
            s_in = generator.generate(k, mode=2, i=i)  # All possible words
        elif mode == 3:
            s_in = generator.generate(k, mode=3, seed=seed)  # LFSR
            seed = s_in  # Update the seed for the next iteration

        c = encoder(s_in, c_prev, M)

        # Count transitions
        transition_count.transition_count(c, c_prev)
        # Generate error
        error_probability = 0.5
        c_tilde = error_generator.error_generator(c, error_probability)
        controller_logger.debug(f"codeword:            {c}")
        controller_logger.debug(f"Codeword with error: {c_tilde}")
        # Decode the codeword
        s_out = decoder(c, M)

        # Compare input and output words
        if not comparator.comparator(s_in, s_out):
            controller_logger.warning(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")
            break

        # Update the previous codeword
        c_prev = c


    # Log transition statistics
    max_transitions, avg_transitions = transition_count.transition_count(c_prev, c_prev)
    controller_logger.info(f"Max transitions: {max_transitions}")
    controller_logger.info(f"Avg transitions: {avg_transitions / (t if mode == 1 or mode == 3 else (2 ** k))}")
    controller_logger.info(f"Expected Avg transitions: {mbit_bi_average.mbit_bi_average(k, M)}")

    print()


def validate_input(k, M, n, mode):
    controller_logger = logging.getLogger("Controller")
    # input validation
    if M > (k/2):
        controller_logger.error(f"Invalid input: M={M}. M must be less than or equal to k/2.")
        return False
    if mode > 3 or mode < 1:
        controller_logger.error(f"Invalid input: mode={mode}. Mode must be 1, 2, or 3.")
        return
    return True


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the simulation controller.")
    parser.add_argument(
        "-loglevel", 
        type=int, 
        choices=[1, 2, 3, 4, 5],
        default=2,  # Default to INFO
        help="Log level: 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL"
    )
    return parser.parse_args()


def map_log_level(level_number):
    level_map = {
        1: logging.DEBUG,
        2: logging.INFO,
        3: logging.WARNING,
        4: logging.ERROR,
        5: logging.CRITICAL,
    }
    return level_map.get(level_number, logging.INFO)


if __name__ == '__main__': 
    args = parse_arguments()
    console_level = map_log_level(args.loglevel)
    configure_logging(console_level=console_level)  
    controller()