import logging

def configure_logging(console_level=logging.WARNING):
    """
    Configure logging with separate file and console handlers.
    
    Args:
        console_level: Minimum log level to display in console. Lower levels go to file only.
    """
    
    # Remove any existing handlers to avoid duplicate logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create file handler for all logs (DEBUG and above)
    file_handler = logging.FileHandler("simulation_logs.log", mode='w')
    file_handler.setLevel(logging.DEBUG)  # Capture all logs in file
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Create console handler with user-specified level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)  # Only show logs at or above this level
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s: %(message)s"  # Simplified format for console
    ))

    # Configure the root logger with both handlers
    logging.basicConfig(
        level=logging.DEBUG,  # Root level must be DEBUG to capture all logs
        handlers=[file_handler, console_handler]
    )

    logging.debug("===== New Simulation Run Started =====")