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
from core import simulator
from config.logging_config import configure_logging
from config.simulation_config import SIMULATION_PARAMS, SCHEMES, GENERATION_MODES


# Description: Controls the encoding process, testing both random and all possible
#              k-bit input words while tracking transition statistics
# Inputs:
#              None
# Outputs:
#              Logs max and average transitions for random words and all possible words

def controller():
    controller_logger = logging.getLogger("Controller")
    
    # Configuration parameters from config
    k: int = SIMULATION_PARAMS['INPUT_BITS']
    t: int = SIMULATION_PARAMS['NUM_RANDOM_WORDS']
    M: int = SIMULATION_PARAMS['DEFAULT_M']
    error_p: float = SIMULATION_PARAMS['ERROR_PROBABILITY']

    schemes = {
        '1': mbit_bi.MbitBI(),
        '2': dapbi.DAPBI(),
        '3': dap.DAP(),
        '4': hamming_x.HAMMINGX()
    }

    scheme_choice = input("Choose coding scheme (1 for M-BI, 2 for DAP-BI, 3 for DAP, 4 for HammingX): ")

    if scheme_choice not in SCHEMES:
        controller_logger.error("Invalid choice. Please select either 1, 2, 3, or 4.")
        return
    
    coding_scheme = schemes[scheme_choice]

    generator_choice = input("Choose simulation mode (1 for random words, 2 for all possible words, 3 for LFSR): ")

    if generator_choice not in GENERATION_MODES:
        controller_logger.error("Invalid choice. Please select either 1, 2, or 3.")
        return
    
    print()  
    if isinstance(coding_scheme, mbit_bi.MbitBI):
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}, M = {M}")
    else:
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}")

    simulator.simulate(coding_scheme, k, t, error_p, M=M, seed=_generate_seed(k) if generator_choice == '3' else None, mode=int(generator_choice))

    controller_logger.debug("Simulation ended")


def _generate_seed(k):
    # The seed is x^n + x^(n-1) + x^0

    if k < 2:
        raise ValueError("Seed length must be at least 2 bits")

    seed = [0] * k
    for pos in [0, 1, -1]:
        seed[pos] = 1

    return seed


if __name__ == '__main__': 
    configure_logging(console_level=logging.INFO)  
    controller()