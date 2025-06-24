import random

def hamming_parity_bits_at_end(info_word):
    """
    Generate Hamming code with parity bits at the end.
    info_word: string of '0's and '1's, e.g., '1011'
    Returns: info_word + parity bits
    """
    m = len(info_word)
    
    # Find number of parity bits needed
    r = 0
    while (2 ** r) < (m + r + 1):
        r += 1

    # Calculate parity bits as if they were at power-of-two positions
    n = m + r
    hamming = ['0'] * n

    # Place info bits (not at positions that are powers of 2)
    j = 0
    for i in range(1, n + 1):
        if not (i & (i - 1)) == 0:  # Not a power of 2
            hamming[i - 1] = info_word[j]
            j += 1

    # Calculate parity bits
    parity_bits = []
    for i in range(r):
        parity_pos = 2 ** i
        parity = 0
        for j in range(1, n + 1):
            if j & parity_pos and j != parity_pos:
                parity ^= int(hamming[j - 1])
        parity_bits.append(str(parity))

    # Return info_word + parity bits at the end
    return info_word + ''.join(parity_bits)


def main():
    best_transition_overall = 0  # worst case

    f_length = 13

    # Generate first codeword
    full_info1 = ''.join(random.choice('01') for _ in range(32+f_length))
    code_word1 = hamming_parity_bits_at_end(full_info1)

    for _ in range(50):
        if ( _ % 10 ) == 0:
            print(f"Iteration {_}")
        
        # Generate second info word
        info_word2 = ''.join(random.choice('01') for _ in range(32))
        
        # Find optimal flexible part for second codeword
        best_transition_count = 64  # worst case
        cnt_2 = 0
        # Try all possible f_length-bit combinations 
        for i in range(2**f_length):
            f_part2 = format(i, f'0{f_length}b')
            full_info2 = info_word2 + f_part2
            code_word2 = hamming_parity_bits_at_end(full_info2)
            
            # Calculate transition count only for redundant bits (f_part + hamming bits)
            redundant_bits1 = code_word1[32:]
            redundant_bits2 = code_word2[32:]
            transition_count = sum(1 for a, b in zip(redundant_bits1, redundant_bits2) if a != b)
            
            # Keep track of minimum transitions for current codeword
            best_transition_count = min(best_transition_count, transition_count)

            if transition_count == 2:
                cnt_2 += 1
                print("--------------------------------------------------")
                print(f"Codeword 1: {code_word1[0:32]} | {code_word1[32:45]} | {code_word1[45:]}")
                print(f"Codeword 2: {code_word2[0:32]} | {code_word2[32:45]} | {code_word2[45:]}")
                #print(f"Info word1: {full_info1[0:32]} | {full_info1[32:]}")
                #print(f"Info word2: {full_info2[0:32]} | {full_info2[32:]}")
        if cnt_2 > 0:
            print(f"cnt_2: {cnt_2}")

        # Keep track of worst case transition count
        best_transition_overall = max(best_transition_overall, best_transition_count)
        code_word1 = code_word2
    

    print(f"\nLowest transition count: {best_transition_overall}\n")


if __name__ == "__main__":
    main()




