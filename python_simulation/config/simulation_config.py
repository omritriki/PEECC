"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes import mbit_bi, dapbi, dap, hamming_x, transition_signaling, offset


SIMULATION_PARAMS = {
    'INPUT_BITS': {
        'value': 32,
        'range': (4, 32),
        'description': 'Number of input bits (k). Must be at least 4 for error correction.'
    },
    'NUM_RANDOM_WORDS': {
        'value': 9000,
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

SCHEMES = {
    1: mbit_bi.MbitBI(),
    2: dapbi.DAPBI(),
    3: dap.DAP(),
    4: hamming_x.HammingX(),
    5: transition_signaling.Transition_Signaling(),
    6: offset.Offset()
}

SIMULATION_MODES = {
    1: "Simulating {t} random words",
    2: "Simulating {t} words using LFSR",
    3: "Simulating all possible words starting from 0"
}

