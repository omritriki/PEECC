"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes import mbit_bi, dapbi, dap, hamming_x


SIMULATION_PARAMS = {
    'INPUT_BITS': 16,          
    'NUM_RANDOM_WORDS': 5000,  
    'DEFAULT_M': 1,            
    'ERROR_PROBABILITY': 0.5   
}

SCHEMES = {
    1: mbit_bi.MbitBI(),
    2: dapbi.DAPBI(),
    3: dap.DAP(),
    4: hamming_x.HAMMINGX()
}

SIMULATION_MODES = {
    1: "Simulating {t} random words",
    2: "Simulating {t} words using LFSR",
    3: "Simulating all possible words starting from 0"
}

