"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

import logging
from coding_schemes.base_coding_scheme import CodingScheme
import numpy as np  # type: ignore
from typing import List, Tuple
import syndrome_lut 
from H_matrix import return_H_U


class SyndromeBasedEncoder(CodingScheme):
    """
    Implements: Syndrome-based encoder for Δ-syndrome encoding
                with precomputed coset leaders.

    Args:
        None (inherits from CodingScheme base class)

    Returns:
        None (class definition)
    """
    name = "Syndrome-based Encoder"
    supports_errors = True

    # Global variable for the class
    syndrome_prev = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    H_U = return_H_U()


    def get_bus_size(self, k, M=None) -> int:
        """
        Implements: Bus width calculation for syndrome-based encoder,
                    accounting for the additional redundancy bits.
        """
        n = 45 # 32 + 13
        return n


    def encode(self, u_bits: np.ndarray, c_prev: np.ndarray, M=None) -> Tuple[np.ndarray, np.ndarray]:
        """Compute v using Δ-syndrome approach with previous state"""

        v_prev = c_prev[32:]
        # Compute current syndrome s_curr = H_U @ u_bits
        s_curr = (self.H_U @ u_bits) % 2
        
        # Compute delta syndrome: s_prev XOR s_curr
        delta_s = self.syndrome_prev ^ s_curr
        
        # Lookup delta_v = get_leader(delta_s)
        delta_v = syndrome_lut.get_leader(tuple(delta_s))
        
        # Set v_curr = prev_v XOR delta_v
        v_curr = v_prev ^ delta_v

        self.syndrome_prev = s_curr

        c = np.concatenate((u_bits, v_curr))
        logging.debug(f"Syndrome-based encoded word: {c}")
        return c


