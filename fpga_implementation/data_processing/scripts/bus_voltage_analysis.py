import os
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt

# Base directory for traces
BASE_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/voltage_traces"
OUTPUT_DIR = f"{BASE_DIR}/output"


def load_primary_array(path: str):
    data = sio.loadmat(path)
    arrays = [(k, v) for k, v in data.items() if not k.startswith("__") and isinstance(v, np.ndarray)]
    _, arr = max(arrays, key=lambda kv: kv[1].size)
    arr = np.asarray(arr)
    return arr


def compute_difference(arr_a: np.ndarray, arr_b: np.ndarray) -> np.ndarray:
    return arr_a - arr_b


def plot_vector(vec: np.ndarray, title: str):
    plt.figure(figsize=(10, 4))
    plt.plot(vec.ravel())
    plt.title(title)
    plt.xlabel("Sample index")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()


def plot_two_vectors(vec1: np.ndarray, vec2: np.ndarray, title1: str, title2: str):
    plt.figure(figsize=(12, 6))
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(vec1.ravel())
    ax1.set_title(title1)
    ax1.set_xlabel("Sample index")
    ax1.set_ylabel("Amplitude")
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(vec2.ravel())
    ax2.set_title(title2)
    ax2.set_xlabel("Sample index")
    ax2.set_ylabel("Amplitude")
    plt.tight_layout()
    plt.show()


def main():
    M_values = [1, 2, 3, 4, 5, 7, 8, 15, 16]

    END_IDX = 2500000  # average c over samples [0:END_IDX)
    max_values = []
    avg_window_values = []

    for M in M_values:
        file_a = f"{BASE_DIR}/m{M}_traces/m{M}_gen_enc.mat"
        file_b = f"{BASE_DIR}/m{M}_traces/m{M}_gen_enc_bus.mat"

        gen_enc = load_primary_array(file_a)
        gen_enc_bus = load_primary_array(file_b)

        c = compute_difference(gen_enc, gen_enc_bus)
        max_diff = np.max(c)
        max_values.append(max_diff)
        # Average over [0:END_IDX)
        c_flat = c.ravel()
        avg_window = float(np.mean(c_flat[:min(len(c_flat), END_IDX)]))
        avg_window_values.append(avg_window)
        # (no plotting)

    # Write summary file only (no prints, no plots)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, "max_and_avg_c_vs_m.txt")
    lines = ["M,MaxC_mV,AvgC_0_to_127000_mV"]
    for M, mx, av in zip(M_values, max_values, avg_window_values):
        lines.append(f"{M},{mx:.2f},{av:.2f}")
    with open(save_path, "w") as f:
        f.write("\n".join(lines))
    # No plotting or printing


if __name__ == "__main__":
    main()