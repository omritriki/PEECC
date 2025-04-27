import logging
import os

def configure_logging():
    """Configure logging with file reset at the beginning of each run."""
    # Create a new file handler that overwrites the existing log file
    file_handler = logging.FileHandler("simulation_logs.log", mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Remove any existing handlers to avoid duplicate logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure the root logger with the new handler
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler]  # Logs go only to the file
    )

    logging.info("=== New Simulation Run Started ===")