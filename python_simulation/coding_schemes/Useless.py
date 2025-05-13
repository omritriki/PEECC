
def binary_subtraction(bin1, bin2):
    num1 = int(bin1, 2)
    num2 = int(bin2, 2)

    result = num1 - num2

    return bin(result)[2:]


def offsetCode(n, t):

    for _ in range(t):
        next_word = Binary_Generator.binary_string_generator(n)

        offset_code = ''.join(
            str((int(next_word[i]) - int(curr_bus[i])) % 2)
            for i in range(n)
        )

        curr_transitions = sum(
            1 for i in range(n) if offset_code[i] != curr_bus[i]
        )

        curr_bus = offset_code


def t0Code(n, t):
    # S = 2  # Pre-defined value

    for _ in range(t):
        INC = random_uniform_binary_choice()

        if INC == 1:
            continue

        # Calculate the number of transitions
        curr_transitions = sum(1 for i in range(n) if next_word[i] != curr_bus[i])

        # Update the bus
        curr_bus = next_word


def t0XORCode(n, t):

    S = 2  # Pre-defined value

    for _ in range(t):
        curr_transitions = 0


        c = ''
        for i in range(n):
            s_prev_plus_S = (int(curr_bus[i]) + S) % 2  # Add S and take modulo 2 for binary operation
            c += str(int(c_prev[i]) ^ int(s[i]) ^ s_prev_plus_S)

        for i in range(n):
            if c[i] != c_prev[i]:
                curr_transitions += 1

        max_transitions = max(max_transitions, curr_transitions)

        avg_transitions += curr_transitions

        c_prev = curr_bus
        curr_bus = c


def offsetXORCode(n, t):
    s_prev = '0' * n
    c_prev = '0' * n
    offset_xor = '0' * n

    for _ in range(t):
        curr_transitions = 0
        s = Binary_Generator.binary_string_generator(n)

        sub = binary_subtraction(s, s_prev)

        for i in range(n):
            offset_xor[i] = str(int(c_prev[i]) ^ int(sub[i]))

        for i in range(n):
            if offset_xor[i] != c[i]:
                curr_transitions += 1

        s_prev = s
        c_prev = c
        c = offset_xor