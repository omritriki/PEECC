import re
import matplotlib.pyplot as plt

raw = """
register           0: 04d
register           1: 000
register           2: 000
register           3: 000
register           4: 02f
register           5: 08a
register           6: 033
register           7: 01b
register           8: 035
register           9: 020
register          10: 00d
register          11: 054
register          12: 020
register          13: 074
register          14: 117
register          15: 093
register          16: 3b8
register          17: 000
"""

# Parse "register <idx>: <hexval>"
pairs = []
for m in re.finditer(r"register\s+(\d+):\s*([0-9a-fA-F]+)", raw):
    idx = int(m.group(1))
    count_dec = int(m.group(2), 16)  # hex → decimal
    pairs.append((idx, count_dec))

pairs.sort(key=lambda x: x[0])

# Optional: print the decimal values
for idx, c in pairs:
    print(f"register {idx:>2}: {c} (decimal)")

# Bar chart: x = bit flips (register index), y = count (decimal)
xs = [i for i, _ in pairs]
ys = [c for _, c in pairs]

plt.figure(figsize=(8, 4))
plt.bar(xs, ys, width=0.8, color="#4e79a7")
plt.xlabel("Number of bit flips")
plt.ylabel("Occurrences (decimal)")
plt.title("M-Bit Bus Invert Bit-flip histogram (M=5)")
plt.xticks(xs)
plt.tight_layout()
plt.show()