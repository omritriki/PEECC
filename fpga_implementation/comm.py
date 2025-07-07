import serial

k = 32
M = 5

num_registers = (k + M) // 2
register_size = 11
total_reg_bits = num_registers * register_size

# Read the data as before
p_ser = serial.Serial(port="COM5", baudrate=57600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, #type: ignore
                      stopbits=serial.STOPBITS_ONE, timeout=30, xonxoff=0, rtscts=0, dsrdtr=0) #type: ignore
conf_byte = "0000"
p_ser.write(bytes.fromhex(conf_byte))
read_data = p_ser.read(int((total_reg_bits + 8 - 1) / 8)) #type: ignore 25
hex_data = [hex(x) for x in read_data]
print(hex_data)
#print(read_data)
#convert hex_data to a binary string
bit_string = ''.join(format(x, '08b') for x in read_data)

# Remove MSB padding if present
padding = len(bit_string) - total_reg_bits
#if padding > 0:
#    bit_string = bit_string[padding:]
print(bit_string)
print(len(bit_string))
# Split into 11-bit registers in binary format
registers = [bit_string[i:i + register_size] for i in range(0, len(bit_string), register_size)]
print(registers)
