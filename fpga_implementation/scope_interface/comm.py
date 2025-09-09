from asyncio import wait

import numpy as np
import serial
import time

k = 32
M = 5

"""num_registers = (k + M) // 2
register_size = 11
total_reg_bits = num_registers * register_size
total_bytes_num = (total_reg_bits + 8 - 1) // 8

def read_128bit_word(ser):
    Read 16 bytes (128 bits) from UART and return as an integer.
    word_bytes = ser.read(4)  # read exactly 16 bytes
    print(f"word_bytes: {word_bytes}")
    len_read = len(word_bytes)
    #if len_read != total_bytes_num:
    #    raise IOError(f"Expected 25 bytes, got {len_read} bytes")
    result = int.from_bytes(word_bytes, byteorder='big')  # MSB first
    return result
"""


def main():
    p_ser = serial.Serial(port="COM5", baudrate=57600, bytesize=serial.EIGHTBITS,
                          parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=30, xonxoff=0, rtscts=0,
                          dsrdtr=0)

    conf_byte = bytes([0x00] * 2)  # Configuration byte to read the PUF
    for i in range(4):
        print(f"------iteration {i + 1}--------")
        p_ser.write(conf_byte)
        word_bytes = p_ser.read(4)
        print(f"Raw bytes: {[hex(b) for b in word_bytes]}")
        received_word = int.from_bytes(word_bytes, byteorder='big')  # MSB first
        reg_num = (received_word >> 22) & 0x1F  # Extract 5-bit reg_num
        sum_value = received_word & 0x3FFFFF  # Extract 22-bit sum_value

        print(f"reg_num: {reg_num}")
        print(f"sum_value: {sum_value}")
        print(f"Full binary: {bin(received_word)[2:].zfill(32)}")
        time.sleep(1)
    p_ser.close()


"""
read_data = p_ser.read(int((total_reg_bits + 8 - 1) / 8)) #type: ignore 25
print(f"read data : {read_data}")
bit_string = ''.join(f'{byte:08b}' for byte in read_data)
print(f"bit_string : {bit_string}")
#
#print(read_data)
#bit_string = ''.join(f'{byte:08b}' for byte in read_data)

# Remove MSB padding if present
#padding = len(bit_string) - total_reg_bits
#if padding > 0:
#    bit_string = bit_string[padding:]
#print(bit_string)
#print(len(bit_string))
# Split into 11-bit registers in binary format
#registers = [bit_string[i:i + register_size] for i in range(0, len(bit_string), register_size)]
#print(registers)

#generate a list of binary strings representing numbers from 1 to 20
"""
if __name__ == "__main__":
    main()