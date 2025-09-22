import os
import matplotlib.pyplot as plt


BASE_DP_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing"
OUTPUT_DIR = f"{BASE_DP_DIR}/output"


def main():
    # Fixed M values and measured LUT counts (provided)
    m_values = [1, 2, 3, 4, 5, 7, 8, 15, 16]
    lut_counts = [1349, 1365, 1405, 1409, 1414, 1471, 1623, 1721, 1940]

    # Save to txt (CSV format)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, "lut_counts.txt")
    with open(save_path, "w") as f:
        f.write("M,LUTs\n")
        for M, cnt in zip(m_values, lut_counts):
            f.write(f"{M},{cnt}\n")

    # Plot LUT count vs M
    plt.figure(figsize=(8, 4))
    plt.plot(m_values, lut_counts, marker='o')
    plt.title("LUT Count vs M")
    plt.xlabel("M value")
    plt.ylabel("LUTs")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "lut_counts.jpg"), dpi=200, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    main()


