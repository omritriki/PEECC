import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from typing import List, Tuple, Optional, Dict
import python_simulation.coding_schemes.syndrome_based.syndrome_lut as syndrome_lut


def compute_syndrome(H: np.ndarray, received_word: np.ndarray) -> np.ndarray:
    """Compute syndrome s = H * received_word^T"""
    return (H @ received_word) % 2


def decode(received_word: np.ndarray, H: np.ndarray, H_V: np.ndarray) -> Dict:
    """
    Decode a received word and correct single bit errors.
    
    Args:
        received_word: The received codeword (45 bits: 32 info + 13 redundancy)
        H: Complete H matrix [H_U | H_V]
        H_V: Redundancy matrix H_V
    
    Returns:
        Dictionary containing:
        - corrected_word: The corrected codeword
        - decoded_info: The decoded information bits (first 32 bits)
        - syndrome: The computed syndrome
        - error_detected: Boolean indicating if an error was detected
        - error_corrected: Boolean indicating if an error was corrected
        - error_position: Position of the corrected bit (-1 if no error)
    """
    # Compute syndrome
    syndrome = compute_syndrome(H, received_word)
    
    # Check if syndrome is zero (no error)
    if np.all(syndrome == 0):
        return {
            "corrected_word": received_word.copy(),
            "decoded_info": received_word[:32].copy(),
            "syndrome": syndrome,
            "error_detected": False,
            "error_corrected": False,
            "error_position": -1
        }
    
    # Error detected - try to correct using coset leaders
    syndrome_key = syndrome_to_key(syndrome)
    coset_leader_v = syndrome_lut.get_leader(syndrome_key)
    
    if coset_leader_v is None:
        # Syndrome not found in lookup table - uncorrectable error
        return {
            "corrected_word": received_word.copy(),
            "decoded_info": received_word[:32].copy(),
            "syndrome": syndrome,
            "error_detected": True,
            "error_corrected": False,
            "error_position": -1
        }
    
    # The coset leader is only for the v part (13 bits)
    # We need to create a full 45-bit error pattern
    # For single bit errors, we can try all possible positions
    # and see which one gives us the correct syndrome
    
    # Try single bit errors at each position
    for pos in range(45):
        # Create error pattern with single bit at position pos
        error_pattern = np.zeros(45, dtype=int)
        error_pattern[pos] = 1
        
        # Check if this error pattern produces the observed syndrome
        test_syndrome = compute_syndrome(H, error_pattern)
        if np.array_equal(test_syndrome, syndrome):
            # Found the correct error pattern
            corrected_word = received_word ^ error_pattern
            
            return {
                "corrected_word": corrected_word,
                "decoded_info": corrected_word[:32].copy(),
                "syndrome": syndrome,
                "error_detected": True,
                "error_corrected": True,
                "error_position": pos
            }
    
    # If we get here, we couldn't find a single bit error that matches
    # This could be a multiple bit error or uncorrectable error
    return {
        "corrected_word": received_word.copy(),
        "decoded_info": received_word[:32].copy(),
        "syndrome": syndrome,
        "error_detected": True,
        "error_corrected": False,
        "error_position": -1
    }



def main():
    """Main function to test the syndrome-based decoder"""
    # Step 1: Create redundancy matrix H_V (same as encoder)
    H_V = create_redundancy_matrix()
    
    # Step 2: Generate H_U (same as encoder)
    H_U = generate_HU_from_HV(H_V, k=32, rng_seed=42)
    
    # Step 3: Construct complete H matrix
    H = construct_H_matrix(H_U, H_V)
    
    print("Syndrome-Based Decoder")
    print("=" * 50)
    print(f"H matrix dimensions: {H.shape}")
    print(f"H_U dimensions: {H_U.shape}")
    print(f"H_V dimensions: {H_V.shape}")
    
    # Step 4: Test single bit error correction with actual encoder
    print("\n" + "="*60)
    results1 = test_with_actual_encoder(H_U, H_V, num_tests=20)
    display_decoder_results(results1)
    
    # Step 5: Test all single bit error positions
    print("\n" + "="*60)
    results2 = test_all_single_bit_error_positions(H_U, H_V)
    display_decoder_results(results2)


if __name__ == "__main__":
    main()
