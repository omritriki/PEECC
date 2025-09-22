import os
import re
import matplotlib.pyplot as plt

# Base directory and M values (aligned with traces_analysis.py)
BASE_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/m_bit_histograms/register_values"
# Output directory for saved histogram images
OUTPUT_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/m_bit_histograms/output"
M_VALUES = [1, 2, 3, 4, 5, 7, 8, 15, 16]

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


def plot_histogram(xs, ys, M):
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

    # Plot
    plt.figure(figsize=(max(8, 0.5 * len(plot_labels)), 4))
    plt.bar(plot_indices, plot_values, width=0.8, color="#4e79a7")
    plt.xlabel("Number of bit flips")
    plt.ylabel("Occurrences")
    plt.title("M-Bit Bus Invert Bit-flip Histogram (M={})".format(M))
    plt.xticks(plot_indices, plot_labels, rotation=0)
    plt.tight_layout()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, f"histogram_m{M}.jpg")
    plt.savefig(save_path, format="jpeg", dpi=200, bbox_inches="tight")
    plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary_lines = []
    summary_path = os.path.join(OUTPUT_DIR, "summary_transitions.txt")
    # Prepare header
    summary_lines.append("M,Average Bit Transitions,Max Transitions")
    for M in M_VALUES:
        path = f"{BASE_DIR}/m{M}_registers.txt"
        xs, ys = parse_register_file(path)
        plot_histogram(xs, ys, M)
        total = sum(ys) if ys else 0
        weighted = sum(i * c for i, c in zip(xs, ys)) if ys else 0
        avg = (weighted / total) if total > 0 else 0.0
        max_transitions = max((i for i, c in zip(xs, ys) if c > 0), default=0)
        summary_lines.append(f"{M},{avg:.2f},{max_transitions}")

    # Write summary file
    with open(summary_path, "w") as f:
        f.write("\n".join(summary_lines))


if __name__ == "__main__":
    main()


