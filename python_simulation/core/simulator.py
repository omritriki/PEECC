"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
from coding_schemes import mbit_bi, dapbi, dap, hamming_x
from core import generator, comparator, transition_count, error_generator


def simulate(encoder, decoder, coding_scheme, k, t, n, M = 0, seed = None, mode = 1):
    controller_logger = logging.getLogger("Controller")
    
    valid = validate_input(k, M, n, mode)
    if not valid:
        controller_logger.error("Invalid input parameters. Exiting simulation.")
        return
    
    modes = {1: f"Simulating {t} random words",
                2: "Simulating all possible words starting from 0",
                3: f"Simulating {t} words using LFSR"}
    
    controller_logger.debug(modes[mode])
    
    # Initalize the bus, reset the counters
    c_prev = [0] * n  
    transition_count.transition_count(c_prev, c_prev, RESET=True)  

    for i in range(t if mode == 1 or mode == 3 else (2 ** k)):
        # Generate input word based on the mode
        if mode == 1:
            s_in = generator.generate(k, mode=1)  
        elif mode == 2:
            c_prev = [0] * n  
            s_in = generator.generate(k, mode=2, i=i)  
        elif mode == 3:
            s_in = generator.generate(k, mode=3, seed=seed) 
            seed = s_in  

        c = encoder(s_in, c_prev, M)
        transition_count.transition_count(c, c_prev)

        # Generate error
        error_probability = 0
        c_tilde = error_generator.error_generator(c, error_probability)

        s_out = decoder(c_tilde, M)

        # Compare input and output words
        if not comparator.comparator(s_in, s_out):
            controller_logger.warning(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")

            # Remove before deployment
            print(f"Mismatch between input and output for word {i + 1}: {s_in} != {s_out}")
            break

        # Update the previous codeword
        c_prev = c

    # Log transition statistics
    max_transitions, avg_transitions = transition_count.transition_count(c_prev, c_prev)
    controller_logger.info(f"Max transitions: {max_transitions}")
    controller_logger.info(f"Avg transitions: {avg_transitions / (t if mode == 1 or mode == 3 else (2 ** k))}")
    
    # Show expected average transitions only for Mbit-BI coding scheme
    if isinstance(coding_scheme, mbit_bi.MbitBI):
        controller_logger.info(f"Expected Avg transitions: {coding_scheme.calculate_expected_average(k, M)}")
    print()


def validate_input(k, M, n, mode):
    controller_logger = logging.getLogger("Controller")

    if M > (k/2):
        controller_logger.error(f"Invalid input: M={M}. M must be less than or equal to k/2.")
        return False
    if mode > 3 or mode < 1:
        controller_logger.error(f"Invalid input: mode={mode}. Mode must be 1, 2, or 3.")
        return False
    
    return True