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
import numpy as np  
from .H_matrix import return_H_U, return_H_V
from .syndrome_lut import get_leader

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
    syndrome_prev = np.array([0, 0, 0, 0, 0, 0])
    H_U = return_H_U()
    H_V = return_H_V()
    H = np.column_stack([H_U, H_V])


    def get_bus_size(self, k, M=None) -> int:
        """
        Implements: Bus width calculation for syndrome-based encoder,
                    accounting for the additional redundancy bits.
        """
        n = 45 # 32 + 13
        return n


    def encode(self, u_bits: list, c_prev: list, M=None, mode=None) -> list:
        """Compute v using Δ-syndrome approach with previous state"""

        u_array = np.array(u_bits)
        v_prev = np.array(c_prev[32:])
        
        # Compute current syndrome s_curr = H_U @ u_bits
        s_curr = (self.H_U @ u_array) % 2
        
        # Compute delta syndrome: s_prev XOR s_curr
        delta_s = self.syndrome_prev ^ s_curr
        
        # Lookup delta_v = get_leader(delta_s)
        # Convert syndrome to tuple of int64 for lookup
        delta_s_tuple = tuple(np.int64(x) for x in delta_s)
        delta_v = get_leader(delta_s_tuple)
        if delta_v is None:
            logging.error(f"No coset leader found for syndrome {delta_s}")
            # Use zero vector as fallback
            delta_v = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        else:
            delta_v = np.array(delta_v)
        
        # Set v_curr = prev_v XOR delta_v
        v_curr = v_prev ^ delta_v

        # Only update syndrome state if not in exhaustive mode (mode 3)
        if mode != 3:
            self.syndrome_prev = s_curr

        c = np.concatenate((u_array, v_curr))
        logging.debug(f"Syndrome-based encoded word:            {c}")
        return c.tolist()
    

    def decode(self, c: list, M=None) -> list:
        """
        Implements: Syndrome-based decoder for Δ-syndrome encoding
                    with precomputed coset leaders.
        """
        c_array = np.array(c)
        s_curr = (self.H @ c_array) % 2

        if np.all(s_curr == 0):
            logging.debug(f"No error detected")
            return c[:32]
        else:
            # Error detected - find which column of H matches the syndrome
            # The syndrome corresponds to a single-bit error at the position
            # where the column index matches the bit position in c
            for col_idx in range(self.H.shape[1]):
                if np.array_equal(s_curr, self.H[:, col_idx]):
                    # Flip the bit at position col_idx
                    c_corrected = c.copy()
                    c_corrected[col_idx] = 1 - c_corrected[col_idx]
                    logging.debug(f"Error detected and corrected at bit position {col_idx}")
                    return c_corrected[:32]
            
            # If no matching column found, this is an uncorrectable error
            logging.warning(f"Uncorrectable error detected - syndrome {s_curr} not found in H matrix")
            return c[:32]  # Return original data without correction
