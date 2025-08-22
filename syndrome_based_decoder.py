import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from typing import List, Tuple, Optional, Dict
import syndrome_lut


def create_redundancy_matrix() -> np.ndarray:
    """Create and return the user-provided redundancy matrix H_V (6×13) with columns sorted by value"""
    # Columns are sorted by their 6-bit binary values (LSB first)
    # Column values: [2, 3, 15, 19, 20, 24, 25, 29, 35, 44, 48, 54, 62]
    return np.array([
        [0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1],
        [0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1],
        [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    ])


def generate_HU_from_HV(H_V: np.ndarray, k: int = 32, rng_seed: Optional[int] = None, sort_columns: bool = True) -> np.ndarray:
    """Build H_U as GF(2) linear combinations of H_V columns with UNIQUE columns.
    
    This function is identical to the one in the encoder to ensure consistency.
    """
    if rng_seed is not None:
        np.random.seed(rng_seed)
    
    r = H_V.shape[0]  # Number of rows (6)
    n_V = H_V.shape[1]  # Number of columns in H_V (13)
    
    # Collect unique columns
    unique_cols: List[np.ndarray] = []
    seen_keys = set()

    # Try random sampling first
    attempts = 0
    max_attempts = 20 * k  # generous cap
    while len(unique_cols) < k and attempts < max_attempts:
        attempts += 1
        # Generate random mask for selecting H_V columns
        mask = generate_random_mask(n_V)

        # XOR the selected columns of H_V
        result = np.zeros(r, dtype=int)
        for i in range(n_V):
            if mask[i]:
                result = (result + H_V[:, i]) % 2

        # Skip all-zero column
        if not np.any(result):
            continue

        key = syndrome_to_key(result)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_cols.append(result)

    # If random sampling didn't yield enough, exhaustively enumerate remaining
    if len(unique_cols) < k:
        for m in range(1 << n_V):
            v_bits = np.array([(m >> j) & 1 for j in range(n_V)])
            result = (H_V @ v_bits) % 2
            # Skip all-zero column
            if not np.any(result):
                continue
            key = syndrome_to_key(result)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            unique_cols.append(result)
            if len(unique_cols) == k:
                break

    # Final guard: if still not enough unique columns, raise an error
    if len(unique_cols) < k:
        raise ValueError(f"Could not generate {k} unique columns for H_U; only {len(unique_cols)} available.")

    # Stack into matrix (6 × k)
    H_U = np.stack(unique_cols, axis=1)

    if sort_columns:
        # Compute LSB-first 6-bit numeric value for each column and sort ascending
        col_values: List[Tuple[int, int]] = []
        for c in range(k):
            val = 0
            for r_idx in range(r):
                val |= (int(H_U[r_idx, c]) << r_idx)
            col_values.append((val, c))
        col_values.sort()
        sorted_indices = [c for _, c in col_values]
        H_U = H_U[:, sorted_indices]
    
    return H_U


def generate_random_mask(num_bits: int) -> np.ndarray:
    """Generate random binary mask avoiding all zeros"""
    while True:
        mask = np.random.randint(0, 2, num_bits)
        if np.any(mask):  # Ensure not all zeros
            return mask


def syndrome_to_key(syndrome: np.ndarray) -> str:
    """Convert syndrome bit vector to string key for dictionary"""
    return ''.join(map(str, syndrome))


def construct_H_matrix(H_U: np.ndarray, H_V: np.ndarray) -> np.ndarray:
    """Construct complete H matrix by concatenating [H_U | H_V]"""
    return np.column_stack([H_U, H_V])


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


def introduce_single_bit_error(codeword: np.ndarray, error_position: Optional[int] = None) -> np.ndarray:
    """
    Introduce a single bit error at the specified position or a random position.
    
    Args:
        codeword: The original codeword
        error_position: Position to flip (0-indexed). If None, random position is chosen.
    
    Returns:
        Codeword with a single bit error
    """
    corrupted = codeword.copy()
    
    if error_position is None:
        error_position = np.random.randint(0, len(codeword))
    
    corrupted[error_position] = 1 - corrupted[error_position]  # Flip the bit
    return corrupted


def test_single_bit_error_correction(H_U: np.ndarray, H_V: np.ndarray, num_tests: int = 100) -> Dict:
    """
    Test the decoder's ability to correct single bit errors.
    
    Args:
        H_U: Information part of H matrix
        H_V: Redundancy part of H matrix
        num_tests: Number of test cases
    
    Returns:
        Dictionary with test results
    """
    H = construct_H_matrix(H_U, H_V)
    
    print(f"Testing single bit error correction with {num_tests} random codewords...")
    
    successful_corrections = 0
    error_positions = []
    correction_results = []
    
    # Import the encoder to generate valid codewords
    import syndrome_based_encoder
    
    for test_idx in range(num_tests):
        # Generate random information word
        info_bits = np.random.randint(0, 2, 32)
        
        # Use the actual encoder to create a valid codeword
        # We'll simulate the encoding process to get a valid codeword
        # that satisfies H * codeword = 0
        
        # For a valid codeword, we need: H_U * u + H_V * v = 0
        # So: H_V * v = H_U * u (mod 2)
        # We can solve for v using the coset leaders
        
        # Compute syndrome of the info word
        info_syndrome = (H_U @ info_bits) % 2
        
        # Get the coset leader for this syndrome
        syndrome_key = syndrome_to_key(info_syndrome)
        v_bits = syndrome_lut.get_leader(syndrome_key)
        
        if v_bits is None:
            # This shouldn't happen with our H matrix, but just in case
            continue
        
        # Create the valid codeword: [u | v]
        valid_codeword = np.concatenate([info_bits, v_bits])
        
        # Verify this is a valid codeword (syndrome should be zero)
        verify_syndrome = compute_syndrome(H, valid_codeword)
        if not np.all(verify_syndrome == 0):
            print(f"Warning: Generated codeword is not valid, syndrome: {verify_syndrome}")
            continue
        
        # Introduce single bit error at random position
        error_pos = np.random.randint(0, 45)
        corrupted_codeword = introduce_single_bit_error(valid_codeword, error_pos)
        
        # Decode the corrupted codeword
        result = decode(corrupted_codeword, H, H_V)
        
        # Check if correction was successful
        if result["error_corrected"]:
            successful_corrections += 1
            error_positions.append(error_pos)
            
            # Verify that the corrected word matches the original
            if not np.array_equal(result["corrected_word"], valid_codeword):
                print(f"Warning: Correction failed to restore original codeword")
                print(f"Original: {valid_codeword}")
                print(f"Corrected: {result['corrected_word']}")
                print(f"Error position: {error_pos}")
                print(f"Syndrome: {result['syndrome']}")
        
        correction_results.append(result)
    
    success_rate = successful_corrections / num_tests
    
    return {
        "total_tests": num_tests,
        "successful_corrections": successful_corrections,
        "success_rate": success_rate,
        "error_positions": error_positions,
        "correction_results": correction_results
    }


def test_with_actual_encoder(H_U: np.ndarray, H_V: np.ndarray, num_tests: int = 50) -> Dict:
    """
    Test the decoder using the actual encoder to generate valid codewords.
    
    Args:
        H_U: Information part of H matrix
        H_V: Redundancy part of H matrix
        num_tests: Number of test cases
    
    Returns:
        Dictionary with test results
    """
    H = construct_H_matrix(H_U, H_V)
    
    print(f"Testing with actual encoder - {num_tests} random codewords...")
    
    successful_corrections = 0
    error_positions = []
    correction_results = []
    
    # Import the encoder
    import syndrome_based_encoder
    
    for test_idx in range(num_tests):
        # Generate random information word
        info_bits = np.random.randint(0, 2, 32)
        
        # Use the actual encoder to create a valid codeword
        encoder_result = syndrome_based_encoder.encode(info_bits, H_U)
        
        # Extract the codeword: [u | v]
        valid_codeword = np.concatenate([encoder_result["u"], encoder_result["v"]])
        
        # Verify this is a valid codeword (syndrome should be zero)
        verify_syndrome = compute_syndrome(H, valid_codeword)
        if not np.all(verify_syndrome == 0):
            print(f"Warning: Encoder produced invalid codeword, syndrome: {verify_syndrome}")
            continue
        
        # Introduce single bit error at random position
        error_pos = np.random.randint(0, 45)
        corrupted_codeword = introduce_single_bit_error(valid_codeword, error_pos)
        
        # Decode the corrupted codeword
        result = decode(corrupted_codeword, H, H_V)
        
        # Check if correction was successful
        if result["error_corrected"]:
            successful_corrections += 1
            error_positions.append(error_pos)
            
            # Verify that the corrected word matches the original
            if not np.array_equal(result["corrected_word"], valid_codeword):
                print(f"Warning: Correction failed to restore original codeword")
                print(f"Original: {valid_codeword}")
                print(f"Corrected: {result['corrected_word']}")
                print(f"Error position: {error_pos}")
                print(f"Syndrome: {result['syndrome']}")
        
        correction_results.append(result)
    
    success_rate = successful_corrections / num_tests
    
    return {
        "total_tests": num_tests,
        "successful_corrections": successful_corrections,
        "success_rate": success_rate,
        "error_positions": error_positions,
        "correction_results": correction_results
    }


def test_all_single_bit_error_positions(H_U: np.ndarray, H_V: np.ndarray) -> Dict:
    """
    Test the decoder by introducing single bit errors at every possible position.
    
    Args:
        H_U: Information part of H matrix
        H_V: Redundancy part of H matrix
    
    Returns:
        Dictionary with test results
    """
    H = construct_H_matrix(H_U, H_V)
    
    print(f"Testing all single bit error positions...")
    
    # Import the encoder
    import syndrome_based_encoder
    
    # Generate a single test codeword
    info_bits = np.random.randint(0, 2, 32)
    encoder_result = syndrome_based_encoder.encode(info_bits, H_U)
    valid_codeword = np.concatenate([encoder_result["u"], encoder_result["v"]])
    
    # Verify this is a valid codeword
    verify_syndrome = compute_syndrome(H, valid_codeword)
    if not np.all(verify_syndrome == 0):
        print(f"Warning: Encoder produced invalid codeword, syndrome: {verify_syndrome}")
        return {}
    
    successful_corrections = 0
    error_positions = []
    correction_results = []
    
    # Test every possible error position
    for error_pos in range(45):
        # Introduce single bit error at this position
        corrupted_codeword = introduce_single_bit_error(valid_codeword, error_pos)
        
        # Decode the corrupted codeword
        result = decode(corrupted_codeword, H, H_V)
        
        # Check if correction was successful
        if result["error_corrected"]:
            successful_corrections += 1
            error_positions.append(error_pos)
            
            # Verify that the corrected word is valid (syndrome = 0)
            corrected_syndrome = compute_syndrome(H, result["corrected_word"])
            if not np.all(corrected_syndrome == 0):
                print(f"Warning: Corrected word is not valid at position {error_pos}")
                print(f"Corrected syndrome: {corrected_syndrome}")
        
        correction_results.append(result)
    
    success_rate = successful_corrections / 45
    
    return {
        "total_tests": 45,
        "successful_corrections": successful_corrections,
        "success_rate": success_rate,
        "error_positions": error_positions,
        "correction_results": correction_results
    }


def display_decoder_results(results: Dict) -> None:
    """Display the results of the decoder tests"""
    print("\nDecoder Test Results:")
    print("=" * 50)
    print(f"Total tests: {results['total_tests']}")
    print(f"Successful corrections: {results['successful_corrections']}")
    print(f"Success rate: {results['success_rate']:.2%}")
    
    if results['successful_corrections'] > 0:
        print(f"Error positions corrected: {results['error_positions'][:10]}...")  # Show first 10
        if len(results['error_positions']) > 10:
            print(f"  (and {len(results['error_positions']) - 10} more)")


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
