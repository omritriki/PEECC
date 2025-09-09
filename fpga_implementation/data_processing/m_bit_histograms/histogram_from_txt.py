import re
import argparse
import matplotlib.pyplot as plt


def parse_register_file(path: str):
    xs = []
    ys = []
    with open(path, "r") as f:
        for line in f:
            m = re.search(r"register\s+(\d+):\s+(-?\d+)", line)
            if m:
                idx = int(m.group(1))
                val = int(m.group(2))
                xs.append(idx)
                ys.append(val)
    # Sort by index
    pairs = sorted(zip(xs, ys), key=lambda p: p[0])
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    return xs, ys


def main():
    parser = argparse.ArgumentParser(description="Plot M-bit histogram from decimal register counts text file")
    parser.add_argument("file", type=str, help="Path to registers text file (e.g., m2_registers.txt)")
    args = parser.parse_args()

    xs, ys = parse_register_file(args.file)

    if not xs:
        print("No register lines found. Expected lines like: 'register    10:   65'")
        return

    # Compact consecutive zero-valued bins into grouped labels
    plot_indices = []
    plot_values = []
    plot_labels = []

    i = 0
    n = len(xs)
    while i < n:
        if ys[i] == 0:
            start = xs[i]
            j = i
            while j + 1 < n and ys[j + 1] == 0 and xs[j + 1] == xs[j] + 1:
                j += 1
            end = xs[j]
            label = f"{start}" if start == end else f"{start}\N{EN DASH}{end}"
            plot_indices.append(len(plot_indices))
            plot_values.append(0)
            plot_labels.append(label)
            i = j + 1
        else:
            plot_indices.append(len(plot_indices))
            plot_values.append(ys[i])
            plot_labels.append(str(xs[i]))
            i += 1

    # Print compact table to console
    width = max(len(lbl) for lbl in plot_labels)
    for lbl, val in zip(plot_labels, plot_values):
        print(f"{lbl.rjust(width)} : {val}")

    # Plot
    plt.figure(figsize=(max(8, 0.5 * len(plot_labels)), 4))
    plt.bar(plot_indices, plot_values, width=0.8, color="#4e79a7")
    plt.xlabel("Number of bit flips (grouped)")
    plt.ylabel("Occurrences (decimal)")
    plt.title("M-Bit Bus Invert Bit-flip histogram")
    plt.xticks(plot_indices, plot_labels, rotation=0)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()


