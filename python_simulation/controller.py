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
from core import generator, comparator, transition_count, error_generator, simulator
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

    k = 32
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

    generator_choice = input("Choose simulation mode (1 for random words, 2 for all possible words, 3 for LFSR): ")

    if generator_choice not in ['1', '2', '3']:
        controller_logger.error("Invalid choice. Please select either 1, 2, or 3.")
        return
    
    print()  
    if isinstance(coding_scheme, mbit_bi.MbitBI):
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}, M = {M}, n = {n}")
    else:
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}, n = {n}")

    simulator.simulate(encoder, decoder, coding_scheme, k, t, n, M=M, seed=generate_seed(k) if generator_choice == '3' else None, mode=int(generator_choice))

    controller_logger.debug("Simulation ended")


def generate_seed(k):
    # The seed is x^n + x^(n-1) +x^0
    seed = [0] * k

    for i in [0, 1, -1]:
        seed[i] = 1

    return seed


if __name__ == '__main__': 
    configure_logging(console_level=logging.INFO)  
    controller()