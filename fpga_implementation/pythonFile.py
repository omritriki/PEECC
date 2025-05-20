import serial

k = 32  
M = 5 

num_registers = (k + M) // 2
register_size = 11
total_reg_bits = num_registers * register_size

# Read the data as before
p_ser = serial.Serial(port="COM5", baudrate=57600, bytesize=serial.EIGHTBITS,
                     parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=30, xonxoff=0, rtscts=0, dsrdtr=0)
conf_byte = "0000"
p_ser.write(bytes.fromhex(conf_byte))
read_data = p_ser.read(((11*((k+M)/2))+8-1)/8)

bit_string = ''.join(f'{byte:08b}' for byte in read_data)

# Remove MSB padding if present
padding = len(bit_string) - total_reg_bits
if padding > 0:
    bit_string = bit_string[padding:]

# Split into 11-bit registers
registers = [
    int(bit_string[i*register_size:(i+1)*register_size], 2)
    for i in range(num_registers)]

print(registers)
