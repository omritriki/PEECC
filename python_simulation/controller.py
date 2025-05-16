"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
from core import simulator
from config.logging_config import configure_logging
from config.simulation_config import SIMULATION_PARAMS, SCHEMES, SIMULATION_MODES


# Description: Controls the encoding process, testing both random and all possible
#              k-bit input words while tracking transition statistics
# Inputs:
#              None
# Outputs:
#              Logs max and average transitions for random words and all possible words

def controller():
    controller_logger = logging.getLogger("Controller")
    
    # Validate configuration parameters
    params = _validate_simulation_params()
    if params is None:
        return
    k, t, M, error_p = params

    scheme_choice = int(input(_get_scheme_prompt()))
    if scheme_choice not in SCHEMES:
        controller_logger.error("Invalid choice. Please select either 1, 2, 3, 4, 5 or 6.")
        return
    
    coding_scheme = SCHEMES[scheme_choice]

    generator_choice = int(input("Choose simulation mode (1 for random words, 2 for LFSR, 3 for all possible words): \n"))
    if generator_choice not in SIMULATION_MODES:
        controller_logger.error("Invalid choice. Please select either 1, 2, or 3\n")
        return
    
    if scheme_choice == 1:  
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}, M = {M}")
    else:
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}")

    simulator.simulate(coding_scheme, k, t, error_p, M=M, mode=generator_choice)

    controller_logger.debug("Simulation ended")


def _get_scheme_prompt() -> str:
    prompt = "Choose coding scheme:\n\n"
    
    # Group schemes by paper
    paper1_schemes = {k:v for k,v in SCHEMES.items() if k < 4}
    paper2_schemes = {k:v for k,v in SCHEMES.items() if k >= 4}
    
    prompt += " Paper 1 - Memory Bus Encoding for Low Power: A Tutorial:\n"
    for num, scheme in paper1_schemes.items():
        prompt += f"    {num}. {scheme.name}\n"
    
    prompt += "\n Paper 2 - Coding for System-on-Chip Networks: A Unified Framework:\n"
    for num, scheme in paper2_schemes.items():
        prompt += f"    {num}. {scheme.name}\n"
    
    return prompt

def _validate_simulation_params() -> tuple[int, int, int, float]:
    try:
        # Validate input bits (k)
        k = SIMULATION_PARAMS['INPUT_BITS']['value']
        k_range = SIMULATION_PARAMS['INPUT_BITS']['range']
        if not (k_range[0] <= k <= k_range[1]):
            logging.error(f"Invalid input bits in config: {k}. Must be between {k_range[0]} and {k_range[1]}")
            return None

        # Validate number of test vectors (t)
        t = SIMULATION_PARAMS['NUM_RANDOM_WORDS']['value']
        t_range = SIMULATION_PARAMS['NUM_RANDOM_WORDS']['range']
        if not (t_range[0] <= t <= t_range[1]):
            logging.error(f"Invalid test vectors in config: {t}. Must be between {t_range[0]} and {t_range[1]}")
            return None

        # Validate M parameter
        M = SIMULATION_PARAMS['DEFAULT_M']['value']
        M_range = SIMULATION_PARAMS['DEFAULT_M']['range']
        if not (M_range[0] <= M <= M_range[1]):
            logging.error(f"Invalid M value in config: {M}. Must be between {M_range[0]} and {M_range[1]}")
            return None
        if not (M < k / 2):
            logging.error(f"Invalid M and k values: Require M < k / 2, got M={M}, k={k}")
            return None

        # Validate error probability
        error_p = SIMULATION_PARAMS['ERROR_PROBABILITY']['value']
        error_range = SIMULATION_PARAMS['ERROR_PROBABILITY']['range']
        if not (error_range[0] <= error_p <= error_range[1]):
            logging.error(f"Invalid error probability in config: {error_p}. Must be between {error_range[0]} and {error_range[1]}")
            return None

        return k, t, M, error_p
    except KeyError as e:
        logging.error(f"Missing parameter in config file: {e}")
        return None


if __name__ == '__main__': 
    configure_logging(console_level=logging.INFO)  
    controller()