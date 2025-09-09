import os
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt


# --- Hard-coded .mat file paths (edit these) ---
FILE_A = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/voltage_traces/traces_m1/m1_gen_enc.mat"
FILE_B = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/voltage_traces/traces_m1/m1_gen_enc_bus.mat"


def load_primary_array(path: str):
    data = sio.loadmat(path)
    arrays = [(k, v) for k, v in data.items() if not k.startswith("__") and isinstance(v, np.ndarray)]
    _, arr = max(arrays, key=lambda kv: kv[1].size)
    arr = np.asarray(arr)
    return arr


def validate_paths(paths):
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print("The following paths do not exist. Please edit FILE_A/FILE_B in this script:")
        for p in missing:
            print(" -", p)
        return False
    return True


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
    if not validate_paths([FILE_A, FILE_B]):
        return

    arr_a = load_primary_array(FILE_A)
    arr_b = load_primary_array(FILE_B)

    if arr_a is None or arr_b is None:
        return

    # Show original vectors first
    plot_two_vectors(arr_a, arr_b, f"Generator + Encoder", f"Generator + Encoder + Bus")

    try:
        c = compute_difference(arr_a, arr_b)
        plot_vector(c, "Bus Voltage Difference")
    except ValueError as e:
        print("Could not compute A - B:", e)


if __name__ == "__main__":
    main()