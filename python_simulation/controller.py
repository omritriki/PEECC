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
from core import generator
from core import comparator
from core import transition_count
from core import mbit_bi_average
from core import error_generator
from logging_config import configure_logging


# Description: Controls the encoding process, testing both random and all possible
#              k-bit input words while tracking transition statistics
# Inputs:
#              None
# Outputs:
#              Logs max and average transitions for random words and all possible words

def controller():
    controller_logger = logging.getLogger("Controller")
    global encoder, decoder, coding_scheme

    k = 30
    t = 5000
    M = 1

    schemes = {
        '1': mbit_bi.MbitBI(),
        '2': dapbi.DAPBI(),
        '3': dap.DAP(),
        '4': hamming_x.HAMMINGX()
    }

    scheme_choice = input("Choose coding scheme (1 for M-BI, 2 for DAP-BI, 3 for DAP, 4 for HammingX): ")

    if scheme_choice not in schemes:
        controller_logger.error("Invalid choice. Please select either 1, 2, 3, or 4.")
        return
    
    coding_scheme = schemes[scheme_choice]
    encoder = coding_scheme.encode
    decoder = coding_scheme.decode
    n = coding_scheme.get_bus_size(k, M)

    generator_choice = input(f"Simulate {t} random words (1), Simulate all possible words starting from 0 (2), or Simulate using LFSR (3)? ")

    if generator_choice not in ['1', '2', '3']:
        controller_logger.error("Invalid choice. Please select either 1, 2, or 3.")
        return
    
    print()  
    if isinstance(coding_scheme, mbit_bi.MbitBI):
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}, M = {M}, n = {n}")
    else:
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}, n = {n}")

    simulate(k, t, n, M=M, seed=generate_seed(k) if generator_choice == '3' else None, mode=int(generator_choice))

    controller_logger.debug("Simulation ended")


def generate_seed(k):
    # The seed is x^n + x^(n-1) +x^0
    seed = [0] * k

    for i in [0, 1, -1]:
        seed[i] = 1

    return seed


def simulate(k, t, n, M = 0, seed = None, mode = 1):
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


if __name__ == '__main__': 
    configure_logging(console_level=logging.INFO)  
    controller()