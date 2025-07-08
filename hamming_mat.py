import numpy as np
import random
from syndrome_to_flip import syndrome_to_flip

# Define positions for parity, data, and f-bits
PARITY_POS = [2**i - 1 for i in range(6)] # [0, 1, 3, 7, 15, 31]                  
DATA_POS = [i for i in range(63) if i not in PARITY_POS]   
# Choose 12 random positions for f- bits, that are not parity bits, and are in DATA_POS
# F_POS = DATA_POS[32:45]  # Example fixed positions for f-bits
F_POS = random.sample(DATA_POS, 9)
INFO_POS = [i for i in DATA_POS if i not in F_POS][:32]
PADDDED_POS = [i for i in DATA_POS if i not in F_POS and i not in INFO_POS]

# Derived constants
N_BITS = 63  # Total codeword length
M_BITS = 6  # Number of parity bits
K_BITS = 57  # Number of data bits
INFO_LEN = 32  # Number of info bits
F_LEN = len(F_POS)  # Number of f-bits


def print_codeword_layout():
    print("""\nCodeword Layout (1-indexed):""")
    for i in range(N_BITS):
        label = []
        if i in PARITY_POS: label.append('P')
        if i in DATA_POS: label.append('M')
        if i in F_POS: label.append('F')
        print(f"{i+1:2}: {''.join(label) or '-'}", end=' | ')
        if (i+1) % 10 == 0: print()
    print("\nP=parity, M=info, F=f-bit\n")
          

def build_matrices():
    """Build (G, H) for the systematic (63, 57) Hamming code with parity bits at positions 0,1,3,7,15,31."""
    m, n = M_BITS, N_BITS
    k = K_BITS

    # H matrix (6 × 63)
    H = np.zeros((m, n), dtype=int)
    for j in range(n):
        bits = format(j + 1, f'0{m}b')[::-1]  # binary of (j+1), LSB first
        H[:, j] = list(map(int, bits))

    # G matrix (57 × 63)
    P = H[:, DATA_POS]
    G = np.zeros((k, n), dtype=np.int8)
    G[:, DATA_POS] = np.eye(k, dtype=np.int8)
    G[:, PARITY_POS] = P.T

    return G, H


def encode_using_mat(info_bits, f_bits, G):
    """Encode information bits and f-bits using generator matrix G"""
    full_info_bits = np.concatenate((info_bits, f_bits))
    # pad full_info_bits to K_BITS with zeros  
    full_info_bits = np.concatenate((full_info_bits, np.zeros(K_BITS - len(full_info_bits), dtype=int)))
    codeword = np.matmul(full_info_bits, G) % 2
    return codeword


def syndrome_delta_m(info_prev, info_word):
    """Calculate syndrome caused by change in message bits"""
    syndrome = 0
    for i in range(INFO_LEN):
        if info_prev[i] != info_word[i]:
            pos = DATA_POS[i] + 1  # Convert to 1-indexed
            syndrome ^= pos
    return syndrome


def choose_f_part(c_prev, info_word):
    """Choose optimal f bits using pre-computed syndrome lookup table"""
    info_prev = c_prev[INFO_POS]
    f_prev = c_prev[F_POS].copy()
    
    s = syndrome_delta_m(info_prev, info_word)

    # Use the syndrome_to_flip LUT
    if s in syndrome_to_flip:
        flip_indices = syndrome_to_flip[s]
        for idx in flip_indices:
            if idx < len(f_prev):
                f_prev[idx] = 1 - f_prev[idx]
        return f_prev

    raise RuntimeError("No valid f found (should be impossible)")


def main():
    G, H = build_matrices()

    #print_codeword_layout()
    
    best_transition_overall = 0
    
    # Generate first codeword
    info_prev = np.zeros(INFO_LEN, dtype=int)
    f_prev = np.zeros(F_LEN, dtype=int)
    c_prev = encode_using_mat(info_prev, f_prev, G) 
    
    for iteration in range(1000):
        info_word = np.random.randint(0, 2, INFO_LEN)
        f = choose_f_part(c_prev, info_word)
        c = encode_using_mat(info_word, f, G)
        
        # Calculate transition count for redundant bits (f + parity)
        f_transition_count = sum(1 for pos in F_POS if c_prev[pos] != c[pos])
        p_transition_count = sum(1 for pos in PARITY_POS if c_prev[pos] != c[pos])
        curr_transition_count = f_transition_count + p_transition_count

        best_transition_overall = max(best_transition_overall, curr_transition_count)
        c_prev = c
    
    print(f"\nHighest transition count: {best_transition_overall}\n")


if __name__ == "__main__":    
    main()
