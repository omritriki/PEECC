"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
import os


# Description: Configures logging for the simulation, including both file and console handlers
# Inputs:
#              console_level (int): The logging level for the console output (e.g., DEBUG, INFO, WARNING)
# Outputs:
#              Logs are written to "simulation_logs.log" and displayed in the console

def configure_logging(console_level=logging.WARNING):
    # Get the directory containing this module
    module_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(module_dir, "simulation_logs.log")

    # Remove any existing handlers to avoid duplicate logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create file handler for all logs (DEBUG and above)
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setLevel(logging.DEBUG)  
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Create console handler with user-specified level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)  
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s: %(message)s" 
    ))

    # Configure the root logger with both handlers
    logging.basicConfig(
        level=logging.DEBUG,  
        handlers=[file_handler, console_handler]
    )

    logging.debug("========= New Simulation Run Started =========")