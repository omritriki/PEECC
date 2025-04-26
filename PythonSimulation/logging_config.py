import logging

# Configure logging
def configure_logging():
    file_handler = logging.FileHandler("simulation_logs.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler]  # Logs go only to the file
    )