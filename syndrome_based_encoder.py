import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from typing import List, Tuple, Optional
import random
import syndrome_lut


def create_redundancy_matrix() -> np.ndarray:
    """Create and return the user-provided redundancy matrix H_V (6×13)"""
    return np.array([
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1],
        [0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        [0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1],
        [0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0]
    ])


def generate_random_mask(num_bits: int) -> np.ndarray:
    """Generate random binary mask avoiding all zeros"""
    while True:
        mask = np.random.randint(0, 2, num_bits)
        if np.any(mask):  # Ensure not all zeros
            return mask


def generate_HU_from_HV(H_V: np.ndarray, k: int = 32, rng_seed: Optional[int] = None) -> np.ndarray:
    """Build H_U as GF(2) linear combinations of H_V columns"""
    if rng_seed is not None:
        np.random.seed(rng_seed)
    
    r = H_V.shape[0]  # Number of rows (6)
    n_V = H_V.shape[1]  # Number of columns in H_V (13)
    
    H_U = np.zeros((r, k), dtype=int)
    
    for col in range(k):
        # Generate random mask for selecting H_V columns
        mask = generate_random_mask(n_V)
        
        # XOR the selected columns of H_V
        result = np.zeros(r, dtype=int)
        for i in range(n_V):
            if mask[i]:
                result = (result + H_V[:, i]) % 2
        
        H_U[:, col] = result
    
    return H_U


def syndrome_to_key(syndrome: np.ndarray) -> str:
    """Convert syndrome bit vector to string key for dictionary"""
    return ''.join(map(str, syndrome))


def key_to_syndrome(key: str) -> np.ndarray:
    """Convert string key back to syndrome bit vector"""
    return np.array([int(bit) for bit in key])


def precompute_min_v_for_all_s(H_V: np.ndarray) -> None:
    """Precompute minimum-weight v for each syndrome s = H_V * v^T and write to syndrome_lut.py"""
    n_V = H_V.shape[1]  # Number of columns in H_V (13)
    
    lookup = {}
    
    # Iterate all possible v masks (2^13 combinations)
    for i in range(1 << n_V):
        # Convert integer to binary mask
        v_bits = np.array([(i >> j) & 1 for j in range(n_V)])
        
        # Compute syndrome s = H_V * v^T
        s = (H_V @ v_bits) % 2
        
        # Calculate weight of v
        weight = np.sum(v_bits)
        
        # Convert syndrome to string key
        s_key = syndrome_to_key(s)
        
        # Store minimum-weight v for this syndrome (tie-break by smaller index)
        if s_key not in lookup or weight < lookup[s_key][1] or (weight == lookup[s_key][1] and i < int(''.join(map(str, lookup[s_key][0])), 2)):
            lookup[s_key] = (v_bits, weight)
    
    # Write lookup table to syndrome_lut.py
    with open('syndrome_lut.py', 'w') as f:
        f.write("# Syndrome Lookup Table\n")
        f.write("# Format: {syndrome_string: (v_bits_array, weight)}\n\n")
        f.write("import numpy as np\n\n")
        f.write("SYNDROME_LUT = {\n")
        
        for s_key, (v_bits, weight) in lookup.items():
            v_bits_str = f"np.array({v_bits.tolist()})"
            f.write(f"    '{s_key}': ({v_bits_str}, {weight}),\n")
        
        f.write("}\n\n")
        f.write("def get_min_v_for_syndrome(syndrome_key: str):\n")
        f.write("    \"\"\"Get minimum-weight v for given syndrome\"\"\"\n")
        f.write("    return SYNDROME_LUT.get(syndrome_key, (None, None))\n")
    
    # Reload the module to get the updated lookup table
    import importlib
    importlib.reload(syndrome_lut)


def syndrome_of_u(H_U: np.ndarray, u_bits: np.ndarray) -> np.ndarray:
    """Compute syndrome s = H_U * u^T"""
    return (H_U @ u_bits) % 2


def find_min_v_for_u(u_bits: np.ndarray, H_U: np.ndarray) -> Tuple[np.ndarray, int]:
    """Find minimum-weight v for given u using precomputed lookup from syndrome_lut.py"""
    # Compute syndrome s = H_U * u^T
    s = syndrome_of_u(H_U, u_bits)
    
    # Convert syndrome to key for lookup
    s_key = syndrome_to_key(s)
    
    # Look up minimum-weight v for this syndrome from syndrome_lut
    v_bits, weight = syndrome_lut.get_min_v_for_syndrome(s_key)
    
    return v_bits, weight


def construct_H_matrix(H_U: np.ndarray, H_V: np.ndarray) -> np.ndarray:
    """Construct complete H matrix by concatenating [H_U | H_V]"""
    return np.column_stack([H_U, H_V])


def display_H_matrix(H_matrix: np.ndarray) -> None:
    """Display the H matrix in a formatted way using pandas"""
    print("H Matrix:")
    print("=" * 80)
    
    H_df = pd.DataFrame(
        H_matrix,
        index=[f'Row {i+1}' for i in range(6)],
        columns=[f'Col {i+1}' for i in range(45)]
    )
    print(H_df)
    print(f"\nStructure: Info part (Col 1-32) | Redundancy part (Col 33-45)")


def test_random_info_words(H_U: np.ndarray,
                          num_tests: int = 500) -> List[int]:
    """Test random info words and return list of minimum weights"""
    print(f"\nTesting {num_tests} random info words with syndrome-based encoding...")
    
    results = []
    max_min_weight = 0
    
    for _ in range(num_tests):
        # Generate random info word u
        u_bits = np.random.randint(0, 2, 32)
        
        # Find minimum-weight v for this u
        v_bits, weight = find_min_v_for_u(u_bits, H_U)
        
        results.append(weight)
        max_min_weight = max(max_min_weight, weight)
    
    return results


def display_summary(results: List[int]) -> None:
    """Display summary statistics of the test results"""
    print(f"\nSummary:")
    print("=" * 30)
    print(f"Total info words tested: {len(results)}")
    print(f"Maximum parity weight needed: {max(results)}")


def main():
    """Main function to orchestrate the H matrix analysis"""
    # Step 1: Create redundancy matrix H_V
    H_V = create_redundancy_matrix()
    
    # Step 2: Generate H_U as GF(2) linear combinations of H_V
    H_U = generate_HU_from_HV(H_V, k=32, rng_seed=42)
    
    # Step 3: Precompute lookup table for minimum-weight v per syndrome and write to file
    precompute_min_v_for_all_s(H_V)
    
    # Step 4: Construct complete H matrix
    H = construct_H_matrix(H_U, H_V)
    
    # Step 5: Display the H matrix
    display_H_matrix(H)
    
    # Step 6: Test random info words
    results = test_random_info_words(H_U)

    # Step 7: Display summary
    display_summary(results)


if __name__ == "__main__":
    main()


