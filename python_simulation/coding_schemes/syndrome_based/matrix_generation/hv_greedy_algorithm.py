import numpy as np
from itertools import product
import random

# Matrix dimensions
M = 6  # number of rows (syndrome length)
K = 6  # information portion columns
R = 7  # redundancy portion columns
N = K + R  # total columns
TARGET_RANK = 6

def is_linearly_independent(matrix, new_column):
    """
    Check if adding new_column to matrix maintains linear independence
    """
    if matrix.size == 0:
        return True
    
    # Create augmented matrix
    augmented = np.column_stack([matrix, new_column])
    return np.linalg.matrix_rank(augmented) == matrix.shape[1] + 1

def can_express_as_sum_of_at_most_2(target_vector, matrix):
    """
    Check if target_vector can be expressed as sum of at most 2 vectors from matrix columns
    In GF(2), this means: v = u1 + u2 or v = u1 or v = 0
    """
    # Check if target_vector is zero vector
    if np.all(target_vector == 0):
        return True
    
    # Check if target_vector is equal to any single column
    for i in range(matrix.shape[1]):
        if np.array_equal(target_vector, matrix[:, i]):
            return True
    
    # Check if target_vector is sum of any two columns
    for i in range(matrix.shape[1]):
        for j in range(i + 1, matrix.shape[1]):
            sum_vectors = (matrix[:, i] + matrix[:, j]) % 2
            if np.array_equal(target_vector, sum_vectors):
                return True
    
    return False

def check_all_vectors_expressible(matrix):
    """
    Check if all 2^6 = 64 possible 6-vectors can be expressed as sum of at most 2 vectors from matrix
    Note: Zero vector doesn't need to be expressible as it's naturally available (sum of 0 vectors)
    """
    for vector in product([0, 1], repeat=6):
        target_vector = np.array(vector)
        # Skip zero vector - it doesn't need to be expressible
        if np.all(target_vector == 0):
            continue
        if not can_express_as_sum_of_at_most_2(target_vector, matrix):
            return False, target_vector
    return True, None

def find_missing_vectors(matrix):
    """
    Find vectors that cannot be expressed as sum of at most 2 vectors from matrix
    Note: Zero vector doesn't need to be expressible as it's naturally available (sum of 0 vectors)
    """
    missing = []
    for vector in product([0, 1], repeat=6):
        target_vector = np.array(vector)
        # Skip zero vector - it doesn't need to be expressible
        if np.all(target_vector == 0):
            continue
        if not can_express_as_sum_of_at_most_2(target_vector, matrix):
            missing.append(target_vector)
    return missing

def generate_extra_vectors(seed=None):
    """
    Greedily generate 7 extra vectors to add to the 6x6 identity matrix
    Goal: Every 6-vector should be expressible as sum of at most 2 vectors from the final matrix
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Start with identity matrix
    identity_matrix = np.eye(M, dtype=int)
    current_matrix = identity_matrix.copy()
    
    extra_vectors = []
    
    vec_idx = 0
    max_vectors = 7  # We need exactly 7 extra vectors
    while vec_idx < max_vectors:  # We need exactly 7 extra vectors        
        # Find missing vectors
        missing_vectors = find_missing_vectors(current_matrix)
        
        if len(missing_vectors) == 0:
            break
        
        best_vector = None
        best_improvement = 0
        
        # Try to find a vector that helps express the missing vectors
        # First, try adding missing vectors directly
        for missing_vec in missing_vectors:
            candidate = missing_vec.copy()
            if (not np.all(candidate == 0) and  # Don't add zero vector
                not any(np.array_equal(candidate, current_matrix[:, i]) for i in range(current_matrix.shape[1]))):
                temp_matrix = np.column_stack([current_matrix, candidate])
                expressible_count = 0
                for vector in product([0, 1], repeat=6):
                    target_vector = np.array(vector)
                    if can_express_as_sum_of_at_most_2(target_vector, temp_matrix):
                        expressible_count += 1
                
                if expressible_count > best_improvement:
                    best_improvement = expressible_count
                    best_vector = candidate.copy()
                    if expressible_count == 63:  # All non-zero vectors expressible
                        break
        
        # If no direct missing vector works, try combinations
        if best_vector is None:
            for missing_vec in missing_vectors:
                for existing_idx in range(current_matrix.shape[1]):
                    # Try adding missing_vec + existing_vector
                    candidate = (missing_vec + current_matrix[:, existing_idx]) % 2
                    if (not np.all(candidate == 0) and  # Don't add zero vector
                        not any(np.array_equal(candidate, current_matrix[:, i]) for i in range(current_matrix.shape[1]))):
                        temp_matrix = np.column_stack([current_matrix, candidate])
                        expressible_count = 0
                        for vector in product([0, 1], repeat=6):
                            target_vector = np.array(vector)
                            if can_express_as_sum_of_at_most_2(target_vector, temp_matrix):
                                expressible_count += 1
                        
                        if expressible_count > best_improvement:
                            best_improvement = expressible_count
                            best_vector = candidate.copy()
                            if expressible_count == 63:  # All non-zero vectors expressible
                                break
                if best_vector is not None and best_improvement == 63:
                    break
        
        # If no good vector found from missing vectors, try to find vectors that help with specific missing vectors
        if best_vector is None:
            print(f"  Trying to find vectors that help with specific missing vectors...")
            for missing_vec in missing_vectors:
                # Try all possible combinations of existing vectors + missing_vec
                for i in range(current_matrix.shape[1]):
                    for j in range(i + 1, current_matrix.shape[1]):
                        # Try adding missing_vec + existing_vector_i + existing_vector_j
                        candidate = (missing_vec + current_matrix[:, i] + current_matrix[:, j]) % 2
                        if (not np.all(candidate == 0) and  # Don't add zero vector
                            not any(np.array_equal(candidate, current_matrix[:, k]) for k in range(current_matrix.shape[1]))):
                            temp_matrix = np.column_stack([current_matrix, candidate])
                            expressible_count = 0
                            for vector in product([0, 1], repeat=6):
                                target_vector = np.array(vector)
                                if can_express_as_sum_of_at_most_2(target_vector, temp_matrix):
                                    expressible_count += 1
                            
                            if expressible_count > best_improvement:
                                best_improvement = expressible_count
                                best_vector = candidate.copy()
                                if expressible_count == 63:
                                    break
                    if best_vector is not None and best_improvement == 63:
                        break
                if best_vector is not None and best_improvement == 63:
                    break
            
            # If still no good vector, try random vectors
            if best_vector is None:
                print(f"  Trying random vectors...")
                for _ in range(10000):  # More attempts for the harder constraint
                    candidate = np.random.randint(0, 2, M)
                    if (not np.all(candidate == 0) and  # Don't add zero vector
                        not any(np.array_equal(candidate, current_matrix[:, i]) for i in range(current_matrix.shape[1]))):
                        temp_matrix = np.column_stack([current_matrix, candidate])
                        expressible_count = 0
                        for vector in product([0, 1], repeat=6):
                            target_vector = np.array(vector)
                            if can_express_as_sum_of_at_most_2(target_vector, temp_matrix):
                                expressible_count += 1
                        
                        if expressible_count > best_improvement:
                            best_improvement = expressible_count
                            best_vector = candidate.copy()
                            if expressible_count == 63:  # All non-zero vectors expressible
                                break
        
        if best_vector is not None:
            extra_vectors.append(best_vector)
            current_matrix = np.column_stack([current_matrix, best_vector])
            print(f"  Added vector {vec_idx + 1}: {best_vector}, now {best_improvement}/63 non-zero vectors expressible")
            vec_idx += 1
        else:
            print(f"  Failed to find suitable vector {vec_idx + 1}")
            break
    
    return np.array(extra_vectors).T if extra_vectors else np.zeros((M, 0), dtype=int)

def generate_hv_matrix(seed=None):
    """
    Main greedy algorithm to generate Hv matrix
    Structure: Hv = [I_6 | H_extra] where I_6 is identity matrix and H_extra is 6x7
    """
    print("Starting with 6x6 identity matrix...")
    identity_matrix = np.eye(M, dtype=int)
    
    print("Generating 7 extra vectors...")
    H_extra = generate_extra_vectors(seed)
    
    # Combine to form Hv
    Hv = np.column_stack([identity_matrix, H_extra])
    
    return Hv, identity_matrix, H_extra

def validate_matrix(Hv, identity_matrix, H_extra):
    """
    Validate that the generated matrix satisfies all required properties
    """
    print("\nValidating matrix properties...")
    
    # Check dimensions
    assert Hv.shape[0] == M, f"Wrong Hv rows: {Hv.shape[0]}, expected {M}"
    assert identity_matrix.shape == (M, K), f"Wrong identity matrix dimensions: {identity_matrix.shape}"
    # H_extra should have exactly 7 columns
    assert H_extra.shape == (M, 7), f"Wrong H_extra dimensions: {H_extra.shape}, expected ({M}, 7)"
    
    # Check that first part is identity matrix
    assert np.array_equal(identity_matrix, np.eye(M, dtype=int)), "First part is not identity matrix"
    
    # Check full rank
    rank = np.linalg.matrix_rank(Hv)
    assert rank == TARGET_RANK, f"Wrong rank: {rank}, expected {TARGET_RANK}"
    
    # Check main requirement: every non-zero 6-vector expressible as sum of at most 2 vectors
    all_expressible, counterexample = check_all_vectors_expressible(Hv)
    if not all_expressible:
        print(f"✗ Vector {counterexample} cannot be expressed as sum of at most 2 vectors")
        return False
    
    print("✓ All properties validated successfully!")
    return True

def print_matrix_info(Hv, identity_matrix, H_extra):
    """
    Print detailed information about the generated matrix
    """
    print("\n" + "="*50)
    print("GENERATED Hv MATRIX")
    print("="*50)
    
    print(f"\nHv matrix ({Hv.shape[0]}x{Hv.shape[1]}):")
    print(Hv)
    
    print(f"- Rank of Hv: {np.linalg.matrix_rank(Hv)}")
    print(f"- Null space dimension: {Hv.shape[1] - np.linalg.matrix_rank(Hv)}")
    print(f"- Syndrome space size: 2^{np.linalg.matrix_rank(Hv)} = {2**np.linalg.matrix_rank(Hv)}")
    print(f"- All 63 non-zero 6-vectors expressible as sum of ≤2 vectors: ✓")


def generate_hv_matrix_entry_point(seed=None, verbose=True):
    """
    Entry point function for Hv matrix generation.
    
    Args:
        seed (int, optional): Random seed for reproducibility
        verbose (bool): Whether to print progress information
        
    Returns:
        tuple: (Hv, identity_matrix, H_extra) if successful, None if failed
    """
    if verbose:
        print("Greedy Algorithm for Hv Matrix Generation")
        print("="*50)
        print("Goal: Generate Hv = [I_6 | H_extra] where every 6-vector is expressible")
        print("as sum of at most 2 vectors from Hv")
        print("="*50)
    
    try:
        # Generate matrix
        Hv, identity_matrix, H_extra = generate_hv_matrix(seed=seed)
        
        # Validate
        if validate_matrix(Hv, identity_matrix, H_extra):
            if verbose:
                print_matrix_info(Hv, identity_matrix, H_extra)
            return Hv, identity_matrix, H_extra
        else:
            if verbose:
                print("Matrix validation failed!")
            return None
            
    except Exception as e:
        if verbose:
            print(f"Error generating Hv matrix: {e}")
        return None
    