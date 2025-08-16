import numpy as np # type: ignore
import pandas as pd # type: ignore

# User-provided redundancy matrix (6×13)
R = np.array([
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
    [0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1],
    [0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0]
])

# Create 32 different binary vectors of length 6 that are not in R and not all zeros
all_6bit_vectors = []
for i in range(1, 2**6):  # Skip 0 (all zeros)
    vector = np.array([int(b) for b in format(i, '06b')])
    all_6bit_vectors.append(vector)

# Convert R matrix columns to list of vectors for comparison
R_vectors = [R[:, i] for i in range(13)]

# Filter out vectors that are in R matrix
available_vectors = []
for vector in all_6bit_vectors:
    if not any(np.array_equal(vector, r_vec) for r_vec in R_vectors):
        available_vectors.append(vector)

# Take the first 32 available vectors
if len(available_vectors) >= 32:
    info_vectors = np.column_stack(available_vectors[:32])
else:
    # Pad with some vectors if needed
    info_vectors = np.column_stack(available_vectors + available_vectors[:32-len(available_vectors)])

# Combine to form H matrix: [Info_part | R]
H = np.column_stack([info_vectors, R])

# Display H matrix using pandas
print("H Matrix (6×45):")
print("=" * 80)
H_df = pd.DataFrame(H, 
                   index=[f'Row {i+1}' for i in range(6)],
                   columns=[f'Col {i+1}' for i in range(45)])
print(H_df)
print(f"\nStructure: Info part (Col 1-32) | Redundancy part (Col 33-45)")

# Function to find minimum parity weight for a given info word
def find_min_parity_weight(info_word, H_matrix):
    """Find minimum parity weight for given info word"""
    H1 = H_matrix[:, :32]  # Info part
    H2 = H_matrix[:, 32:]  # Parity part
    
    min_weight = float('inf')
    
    # Try all possible parity combinations
    for i in range(2**13):
        parity_candidate = np.array([int(b) for b in format(i, '013b')])
        candidate_codeword = np.concatenate([info_word, parity_candidate])
        
        # Check if valid: H × C^T = 0
        if np.all(H_matrix @ candidate_codeword % 2 == 0):
            parity_weight = np.sum(parity_candidate)
            if parity_weight < min_weight:
                min_weight = parity_weight
    
    return min_weight

# Function to find minimum weight codeword for a given info word
def find_min_weight_codeword(info_word, H_matrix):
    """Find minimum weight codeword for given info word"""
    H1 = H_matrix[:, :32]  # Info part
    H2 = H_matrix[:, 32:]  # Parity part
    
    min_weight = float('inf')
    best_codeword = None
    
    # Try all possible parity combinations
    for i in range(2**13):
        parity_candidate = np.array([int(b) for b in format(i, '013b')])
        candidate_codeword = np.concatenate([info_word, parity_candidate])
        
        # Check if valid: H × C^T = 0
        if np.all(H_matrix @ candidate_codeword % 2 == 0):
            parity_weight = np.sum(parity_candidate)
            if parity_weight < min_weight:
                min_weight = parity_weight
                best_codeword = candidate_codeword.copy()
    
    return best_codeword, min_weight

# Test 500 random info words with sequential encoding
print(f"\nTesting 500 random info words with sequential encoding...")
print("=" * 60)

results = []
current_bus_state = np.zeros(45, dtype=int)  # Start with zero vector

for i in range(500):
    info_word = np.random.randint(0, 2, 32)
    
    # Find minimum weight codeword for this info word
    best_codeword, min_weight = find_min_weight_codeword(info_word, H)
    
    # Update bus state to the new codeword
    current_bus_state = best_codeword.copy()
    
    results.append(min_weight)

# Summary statistics
print(f"\nSummary:")
print("=" * 30)
print(f"Total info words tested: {len(results)}")
print(f"Maximum parity weight needed: {max(results)}")


