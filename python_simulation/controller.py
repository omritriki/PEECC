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
    
    # Configuration parameters from config
    k: int = SIMULATION_PARAMS['INPUT_BITS']['value']
    t: int = SIMULATION_PARAMS['NUM_RANDOM_WORDS']['value']
    M: int = SIMULATION_PARAMS['DEFAULT_M']['value']
    error_p: float = SIMULATION_PARAMS['ERROR_PROBABILITY']['value']

    scheme_choice = int(input(_get_scheme_prompt()))

    if scheme_choice not in SCHEMES:
        controller_logger.error("Invalid choice. Please select either 1, 2, 3, 4, 5 or 6.")
        return
    
    coding_scheme = SCHEMES[scheme_choice]

    generator_choice = int(input("Choose simulation mode (1 for random words, 2 for LFSR, 3 for all possible words): "))

    if generator_choice not in SIMULATION_MODES:
        controller_logger.error("Invalid choice. Please select either 1, 2, or 3.")
        return
    
    print()  

    if scheme_choice == 1:  # Changed from string to int comparison
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}, M = {M}")
    else:
        controller_logger.info(f"Simulating {coding_scheme.name} with Parameters: k = {k}")

    simulator.simulate(
        coding_scheme, 
        k, 
        t, 
        error_p, 
        M=M, 
        seed=_generate_seed(k) if generator_choice == 2 else None,  
        mode=int(generator_choice)
    )

    controller_logger.debug("Simulation ended")


def _get_scheme_prompt() -> str:
    prompt = "Choose coding scheme:\n\n"
    
    # Group schemes by paper
    paper1_schemes = {k:v for k,v in SCHEMES.items() if k < 4}
    paper2_schemes = {k:v for k,v in SCHEMES.items() if k >= 4}
    
    # Add Paper 2 schemes
    prompt += " Paper 1 - Memory Bus Encoding for Low Power: A Tutorial:\n"
    for num, scheme in paper1_schemes.items():
        prompt += f"    {num}. {scheme.name}\n"
    
    # Add Paper 1 schemes
    prompt += "\n Paper 2 - Coding for System-on-Chip Networks: A Unified Framework:\n"
    for num, scheme in paper2_schemes.items():
        prompt += f"    {num}. {scheme.name}\n"
    
    return prompt


# The seed is x^n + x^(n-1) + x^0
def _generate_seed(k) -> list[int]:
    if k < 2:
        raise ValueError("Seed length must be at least 2 bits")

    seed = [0] * k
    for pos in [0, 1, -1]:
        seed[pos] = 1

    return seed



if __name__ == '__main__': 
    configure_logging(console_level=logging.INFO)  
    controller()