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

    # Pretty header
    header = f"{'M':>3} | {'Max Bus Voltage [mV]':>12} | {'Max Bus Voltage per Wire [mV]':>14}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    per_wire_values = []

    for M in M_values:
        file_a = f"{BASE_DIR}/m{M}_traces/m{M}_gen_enc.mat"
        file_b = f"{BASE_DIR}/m{M}_traces/m{M}_gen_enc_bus.mat"

        gen_enc = load_primary_array(file_a)
        gen_enc_bus = load_primary_array(file_b)

        c = compute_difference(gen_enc, gen_enc_bus)
        max_diff = np.max(c)
        per_wire = max_diff / (32 + M)
        print(f"{M:>3} | {max_diff:12.2f}         |    {per_wire:14.2f}")
        per_wire_values.append(per_wire)

    # Plot max voltage per wire
    plt.figure(figsize=(8, 4))
    plt.plot(M_values, per_wire_values, marker='o')
    plt.title("Max Bus Voltage per Wire")
    plt.xlabel("M value")
    plt.ylabel("Max per wire [mV]")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, "max_per_wire.jpg")
    plt.savefig(save_path, format="jpeg", dpi=200, bbox_inches="tight")
    # plt.show()


if __name__ == "__main__":
    main()