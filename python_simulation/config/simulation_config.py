"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.paper1 import transition_signaling, offset, offset_xor, mbit_bi
from coding_schemes.paper2 import dapbi, dap, hamming_x
from coding_schemes.syndrome_based import syndrome_based_encoder


SIMULATION_PARAMS = {
    'INPUT_BITS': {
        'value': 32,
        'range': (4, 32),
        'description': 'Number of input bits (k). Must be at least 4 for error correction.'
    },
    'NUM_RANDOM_WORDS': {
        'value': 5000,
        'range': (100, 10000),
        'description': 'Number of random test vectors. Higher values give better statistical results.'
    },
    'DEFAULT_M': {
        'value': 1,
        'range': (1, 16),
        'description': 'Number of segments for M-bit Bus Invert encoding.'
    },
    'ERROR_PROBABILITY': {
        'value': 0.5,
        'range': (0.0, 1.0),
        'description': 'Probability of bit errors in transmission.'
    }
}

# Schemes from Paper 1: "Memory Bus Encoding for Low Power: A Tutorial"
PAPER1_SCHEMES = {
    1: transition_signaling.Transition_Signaling(),
    2: offset.Offset(),
    3: offset_xor.Offset_XOR(),
    4: mbit_bi.MbitBI()
}

# Schemes from Paper 2: "Coding for System-on-Chip Networks: A Unified Framework"
PAPER2_SCHEMES = {
    5: dapbi.DAPBI(),
    6: dap.DAP(),
    7: hamming_x.HammingX()
}

# Syndrome-based Error Correction Scheme
SYNDROME_SCHEMES = {
    8: syndrome_based_encoder.SyndromeBasedEncoder()
}

# Combined schemes dictionary
SCHEMES = {**PAPER1_SCHEMES, **PAPER2_SCHEMES, **SYNDROME_SCHEMES}

SIMULATION_MODES = {
    1: "Random word sequence",
    2: "Linear Feedback Shift Register (LFSR)",
    3: "Exhaustive (all possible words)"
}

