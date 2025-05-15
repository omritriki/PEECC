"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
from typing import List
from coding_schemes import mbit_bi
from core import generator, comparator, transition_count, error_generator
from config.simulation_config import SIMULATION_MODES


def simulate(coding_scheme, k, t, error_probability, M = 0, mode = 1):
    simulator_logger = logging.getLogger("Simulator")
    encoder = coding_scheme.encode
    decoder = coding_scheme.decode
    n = coding_scheme.get_bus_size(k, M)

    valid = _validate_input(k, M, n, mode)
    if not valid:
        simulator_logger.error("Invalid input parameters. Exiting simulation.")
        return
    
    # Use mode description from config
    mode_description = SIMULATION_MODES[mode].format(t=t)
    simulator_logger.debug(mode_description)
    
    # Initalize the bus, reset the counters
    c_prev = [0] * n  
    transition_count.transition_count(c_prev, c_prev, RESET=True)  

    num_words = t if mode in [1, 2] else (2 ** k)  
    for i in range(num_words):
        if mode == 3:  
            c_prev = [0] * n

        s_in = generator.generate(k, mode=mode, i=i)
       
        c = encoder(s_in, c_prev, M)
        transition_count.transition_count(c, c_prev)

        # Generate error
        error = error_generator.error_generator(n, error_probability)
        c_with_error = coding_scheme.apply_error(c, error)

        s_out = decoder(c_with_error, M)

        # Compare input and output words

        # move the log to the comparator################
        if not comparator.comparator(s_in, s_out):
            simulator_logger.warning(
                f"Encoding/decoding mismatch at word {i + 1}:\n"
                f"                      Input:                                          {s_in}\n"
                f"                      Output:                                         {s_out}"
            )
            break

        # Update the previous codeword
        c_prev = c

    # Log transition statistics
    max_transitions, avg_transitions = transition_count.transition_count(c_prev, c_prev)
    simulator_logger.info(f"Max transitions: {max_transitions}")
    simulator_logger.info(f"Avg transitions: {avg_transitions / num_words:.4f}")
    
    # Show expected average transitions only for Mbit-BI coding scheme
    if isinstance(coding_scheme, mbit_bi.MbitBI): 
        simulator_logger.info(f"Expected Avg transitions: {coding_scheme.calculate_expected_average(k, M)}")
    print()
    

def _validate_input(k, M, n, mode) -> bool:
    controller_logger = logging.getLogger("Controller")

    if M > (k/2):
        controller_logger.error(f"Invalid input: M={M}. M must be less than or equal to k/2")
        return False
    
    ######### This is already checked in the controller
    if mode > 3 or mode < 1:
        controller_logger.error(f"Invalid input: mode={mode}. Mode must be 1, 2, or 3")
        return False
    
    return True