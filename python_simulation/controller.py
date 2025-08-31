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
import time


def controller():
    """
    Implements: The main controller for the encoding simulation, testing various coding schemes
                with different word generation modes while tracking transition statistics.

    Args:
        None

    Returns:
        None: Logs simulation results and performance metrics to console and log file.
    """
    controller_logger = logging.getLogger("Controller")
    
    # Validate configuration parameters
    params = _validate_simulation_params()
    if params is None:
        return
    k, t, M, error_p = params

    scheme_choice = int(input(_get_scheme_prompt()))
    if scheme_choice not in SCHEMES:
        controller_logger.error("Invalid choice. Please select a valid scheme number from the list above.")
        return
    
    coding_scheme = SCHEMES[scheme_choice]
    
    # Verify syndrome-based encoder requires exactly 32 bits
    if scheme_choice == 8:  # Syndrome-based encoder
        if k != 32:
            controller_logger.error(f"Syndrome-based encoder requires exactly 32 bits, but {k} bits were configured.")
            controller_logger.error("Please update the INPUT_BITS value in simulation_config.py to 32.")
            return

    generator_choice = int(input(_get_mode_prompt()))
    if generator_choice not in SIMULATION_MODES:
        controller_logger.error("Invalid choice. Please select either 1, 2, or 3\n")
        return
    
    if generator_choice == 3:
        t = 2 ** k

    start = time.perf_counter()   
    max_transitions, avg_transitions = simulator.simulate(coding_scheme, k, t, error_p, M=M, mode=generator_choice)
    elapsed = time.perf_counter() - start

    print("\n============= SIMULATION RESULTS =============\n")

    print("Coding Method: ", coding_scheme.name)
    print("Parameters: ")
    print(f"    - Input word length (k): {k} bits")
    print(f"    - Data generation: {SIMULATION_MODES[generator_choice]}")
    print(f"    - Total words processes: {t}")
    print(f"    - Error probability: {error_p}")
    if scheme_choice == 1:  
        print(f"    - M = {M}")

    print("\nResults: ")

    print(f"    - Maximum transitions: {max_transitions}")
    print(f"    - Average transitions: {avg_transitions / t:.4f}")
    print(f"    - Area overhead: {coding_scheme.get_bus_size(k, M) - k} bits ({(coding_scheme.get_bus_size(k, M) - k) / k:.2%})")
    print(f"    - Simulation Duration: {elapsed:.4f} seconds\n")

    controller_logger.debug("Simulation ended")


def _get_scheme_prompt() -> str:
    """
    Implements: A user interface prompt for selecting encoding schemes, organized by research paper.

    Args:
        None

    Returns:
        str: Formatted prompt string displaying available coding schemes grouped by paper.
    """
    prompt = "\n========== ENCODING SCHEME SELECTION ==========\n\n"
    
    # Group schemes by paper
    paper1_schemes = {k:v for k,v in SCHEMES.items() if k < 4}
    paper2_schemes = {k:v for k,v in SCHEMES.items() if k >= 4}
    
    prompt += " [Paper 1] Memory Bus Encoding for Low Power: A Tutorial:\n"
    for num, scheme in paper1_schemes.items():
        prompt += f"    {num}. {scheme.name}\n"
    
    prompt += "\n [Paper 2] Coding for System-on-Chip Networks: A Unified Framework:\n"
    for num, scheme in paper2_schemes.items():
        prompt += f"    {num}. {scheme.name}\n"
    
    # Add syndrome-based schemes
    syndrome_schemes = {k:v for k,v in SCHEMES.items() if k >= 8}
    if syndrome_schemes:
        prompt += "\n [Syndrome-based Error Correction]:\n"
        for num, scheme in syndrome_schemes.items():
            prompt += f"    {num}. {scheme.name}\n"
    
    return prompt


def _get_mode_prompt() -> str:
    """
    Implements: A user interface prompt for selecting simulation mode for word generation.

    Args:
        None

    Returns:
        str: Formatted prompt string displaying available simulation modes.
    """
    prompt = "\n========== SIMULATION CONFIGURATION ==========\n\n"
    
    prompt += "Please select data simulation mode:\n"
    prompt += "    1. Random word sequence\n"
    prompt += "    2. Linear Feedback Shift Register (LFSR)\n"
    prompt += "    3. Exhaustive (all possible words)\n"
    
    return prompt


def _validate_simulation_params() -> tuple[int, int, int, float]:
    """
    Implements: Validation of all simulation parameters from configuration file,
                ensuring they fall within acceptable ranges and satisfy constraints.

    Args:
        None

    Returns:
        tuple[int, int, int, float]: Validated parameters (k, t, M, error_p) or None if validation fails.
    """
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
        if not (M <= k / 2):
            logging.error(f"Invalid M and k values: Require M <= k / 2, got M={M}, k={k}")
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