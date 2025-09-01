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
from coding_schemes.paper1 import mbit_bi
from core import generator, comparator, transition_count, error_generator
from config.simulation_config import SIMULATION_MODES


def simulate(coding_scheme, k, t, error_probability, M = 0, mode = 1):
    """
    Implements: The main simulation loop that encodes, transmits, and decodes words
                while tracking transition statistics and error correction performance.

    Args:
        coding_scheme: The coding scheme object to test (MbitBI, DAPBI, etc.)
        k (int): Number of input bits per word
        t (int): Number of test words to process
        error_probability (float): Probability of introducing bit errors during transmission
        M (int): Number of segments for M-bit schemes (default: 0)
        mode (int): Word generation mode (1=random, 2=LFSR, 3=exhaustive)

    Returns:
        tuple[int, int, bool]: Maximum transitions, total average transitions, and success status (True if all words processed successfully, False if encoding/decoding mismatch occurred).
    """
    simulator_logger = logging.getLogger("Simulator")
    encoder = coding_scheme.encode
    decoder = coding_scheme.decode
    n = coding_scheme.get_bus_size(k, M)

    match = True
    
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
       
        c = encoder(s_in, c_prev, M, mode)
        transition_count.transition_count(c, c_prev)

        # Generate error
        error = error_generator.generate_error(n, error_probability)
        c_with_error = coding_scheme.apply_error(c, error)

        s_out = decoder(c_with_error, M)

        # Compare input and output words
        match = comparator.comparator(s_in, s_out)
        if not match:
            break

        # Update the previous codeword
        c_prev = c

    # Get transition counts
    max_transitions, avg_transitions = transition_count.transition_count(c_prev, c_prev)
    
    # Log the result of the simulation ##### These need to be in the controller
    if match:
        # Show expected average transitions only for Mbit-BI coding scheme
        if isinstance(coding_scheme, mbit_bi.MbitBI): 
            simulator_logger.info(f"Expected Avg transitions: {coding_scheme.calculate_expected_average(k, M)}\n")
        return max_transitions, avg_transitions, True
    
    # Return transition counts with failure status if there's a mismatch
    simulator_logger.error("Simulation failed due to encoding/decoding mismatch")
    return max_transitions, avg_transitions, False
    