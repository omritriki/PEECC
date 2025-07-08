import numpy as np
import random
import pandas as pd
from syndrome_to_flip import syndrome_to_flip


PARITY_POS = [2**i - 1 for i in range(6)] # [0, 1, 3, 7, 15, 31]
DATA_POS = [i for i in range(63) if i not in PARITY_POS] # 
F_POS = [i for i in range(38, 51)] # [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
COL2IDX = {col: idx for idx, col in enumerate(F_POS)}


def print_codeword_layout():
    print("""\nCodeword Layout (1-indexed):""")
    for i in range(63):
        label = []
        if i in PARITY_POS: label.append('P')
        if i in DATA_POS: label.append('M')
        if i in F_POS: label.append('F')
        print(f"{i+1:2}: {''.join(label) or '-'}", end=' | ')
        if (i+1) % 10 == 0: print()
    print("\nP=parity, M=info, F=f-bit\n")
          

def build_matrices():
    """
    Build (G, H) for the systematic (63, 57) Hamming code
    with parity-bit positions 0,1,3,7,15,31 (0-based).

    Returns
    -------
    G : ndarray shape (57, 63)  – generator matrix  [ I | P ]
    H : ndarray shape ( 6, 63)  – parity-check matrix
    """
    m, n = 6, 63            # 2^m – 1 = 63  →  m = 6 parity bits
    k = n - m               # 57 information bits

    parity_pos = [2**i - 1 for i in range(m)]          # 0,1,3,7,15,31
    data_pos   = [i for i in range(n) if i not in parity_pos]

    # ---------- H (6 × 63) -------------------------------------------------
    H = np.zeros((m, n), dtype=int)

    for j in range(n):                      # j = 0..62
        bits = format(j + 1, f'0{m}b')[::-1]  # binary of (j+1), LSB first
        H[:, j] = list(map(int, bits))

    # ---------- G (57 × 63) ------------------------------------------------
    # H[:, parity_pos] is the 6×6 identity → no GF(2) inversion needed
    P = H[:, data_pos]                                 # 6 × 57
    G = np.zeros((k, n), dtype=np.int8)
    G[:, data_pos]   = np.eye(k, dtype=np.int8)        # systematic part
    G[:, parity_pos] = P.T                             # parity part

    return G, H


def encode_using_mat(info_bits, f_bits, G):
    """Encode information bits and f-bits using generator matrix G"""
    full_info_bits = np.concatenate((info_bits, f_bits))
    # pad full_info_bits to 57 bits with zeros  
    full_info_bits = np.concatenate((full_info_bits, np.zeros(57 - len(full_info_bits), dtype=int)))
    # Ensure binary operation with mod 2
    codeword = np.matmul(full_info_bits, G) % 2  # shape: (63,)

    return codeword


def compute_parity_bits(H: np.ndarray, codeword: list) -> list:
    """
    Computes the parity bits for a partial Hamming codeword using the H matrix.
    
    Args:
        H: parity-check matrix (shape: r × n), as a NumPy array of 0/1
        codeword: list of length n; known bits are '0' or '1', unknown parity bits are None
    
    Returns:
        A new list with parity bits filled in so that H · c^T == 0 (mod 2)
    """
    n = len(codeword)
    r = H.shape[0]
    codeword_filled = codeword.copy()
    
    for parity_index in range(n):
        if codeword[parity_index] is None:
            # Solve for this parity bit: position i (0-based)
            # We'll use the i-th column of H to find which rows depend on it
            affected_rows = np.where(H[:, parity_index] == 1)[0]
            parity_value = 0

            for row in affected_rows:
                row_sum = 0
                for col in range(n):
                    if col == parity_index:
                        continue  # we are solving for this one
                    if codeword[col] is None:
                        continue  # unknown, skip
                    row_sum ^= H[row, col] * int(codeword[col])
                # For this row, parity_index's value must make the total sum 0
                parity_value = row_sum  # The value this bit must take
                break  # All rows will agree on the same value in a correct H
            codeword_filled[parity_index] = str(parity_value)

    return codeword_filled


def syndrome_delta_m(info_prev, info_word):
    """Calculate syndrome caused by change in message bits"""
    syndrome = 0
    for i in range(32):
        if info_prev[i] != info_word[i]:
            # Find the position of this message bit in the codeword
            pos = DATA_POS[i] + 1  # Convert to 1-indexed for syndrome calculation
            syndrome ^= pos
    return syndrome


def choose_f_part(c_prev, info_word):
    """Choose optimal f bits using pre-computed syndrome lookup table"""
    # Extract info_prev and f_prev from codeword
    info_prev = np.array([c_prev[DATA_POS[i]] for i in range(32)])
    f_prev = np.array([c_prev[F_POS[i]] for i in range(13)])
    
    # Calculate syndrome from info word change
    s = syndrome_delta_m(info_prev, info_word)

    # Use the syndrome_to_flip lookup table
    if s in syndrome_to_flip:
        flip_indices = syndrome_to_flip[s]
        for idx in flip_indices:
            if idx < len(f_prev):
                f_prev[idx] = 1 - f_prev[idx]
        return f_prev
    
    # Fallback logic if syndrome not in lookup table
    if bin(s).count('1') <= 2:
        return f_prev

    # 2. single-flip scan (13 candidates)
    for i, col in enumerate(F_POS):
        if 1 + bin(s ^ col).count('1') <= 2:
            f_prev[i] = 1 - f_prev[i]
            return f_prev

    # 3. guaranteed 2-flip construction (exactly 1 candidate)
    for i, col_i in enumerate(F_POS):
        col_j = s ^ col_i
        j = COL2IDX.get(col_j)
        if j is not None and j != i:
            for k in (i, j):
                f_prev[k] = 1 - f_prev[k]
            return f_prev

    raise RuntimeError("No valid f₂ found (should be impossible)")


def main():
    # Build matrices
    G, H = build_matrices()

    #print_codeword_layout()
    
    best_transition_overall = 0
    
    # Generate first codeword
    info_prev = np.zeros(32, dtype=int)
    f_prev = np.zeros(13, dtype=int)
    c_prev = encode_using_mat(info_prev, f_prev, G) 
    
    for iteration in range(1000):  # Reduced for testing
        # Generate new info word
        info_word = np.random.randint(0, 2, 32)
        
        # Choose optimal f bits
        f = choose_f_part(c_prev, info_word)
        
        # Encode new codeword using H matrix method
        c = encode_using_mat(info_word, f, G)
        
        # Calculate transition count for redundant bits (f + parity)
        f_transition_count = sum(1 for pos in F_POS if c_prev[pos] != c[pos])
        p_transition_count = sum(1 for pos in PARITY_POS if c_prev[pos] != c[pos])
        curr_transition_count = f_transition_count + p_transition_count

        # Update best
        best_transition_overall = max(best_transition_overall, curr_transition_count)
        c_prev = c
    
    print(f"\nHighest transition count: {best_transition_overall}\n")


if __name__ == "__main__":    
    main()
