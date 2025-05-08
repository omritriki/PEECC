"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

# Simulation parameters
SIMULATION_PARAMS = {
    'INPUT_BITS': 16,          # k: Number of input bits
    'NUM_RANDOM_WORDS': 5000,  # t: Number of random words to simulate
    'DEFAULT_M': 1,            # M: Default number of segments
    'ERROR_PROBABILITY': 0.0   # Default error probability
}

# Coding schemes configuration
SCHEMES = {
    '1': ('M-BI', 'M-bit Bus Invert encoding'),
    '2': ('DAP-BI', 'Duplicate-Add Parity Bus Invert encoding'),
    '3': ('DAP', 'Duplicate-Add Parity encoding'),
    '4': ('HammingX', 'Extended Hamming code')
}

# Generation modes
GENERATION_MODES = {
    '1': 'Random words',
    '2': 'All possible words',
    '3': 'LFSR sequence'
}