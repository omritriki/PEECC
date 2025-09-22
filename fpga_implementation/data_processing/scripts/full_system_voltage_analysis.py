import os
from typing import Tuple, Dict
import numpy as np
import matplotlib.pyplot as plt


# Directories
DEFAULT_TRACES_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/voltage_traces"
OUTPUT_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/output"


def compute_metrics_full(_: np.ndarray) -> Tuple[float, float]:
    # Unused in override-only mode. Kept to avoid broader refactors.
    return 0.0, 0.0


def try_read_overrides() -> Dict[int, Tuple[float, float]]:
    """
    If a overrides file exists in the traces directory, read it and return
    a map of M -> (MaxAbs_mV, AvgAbs_mV).
    """
    path = os.path.join(DEFAULT_TRACES_DIR, "full_overrides.txt")
    overrides: Dict[int, Tuple[float, float]] = {}
    if not os.path.exists(path):
        return overrides
    with open(path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
        return overrides
    # Skip header if present
    start_idx = 1 if lines[0].split(",")[0].lower() in {"m", "m_value"} else 0
    for ln in lines[start_idx:]:
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) < 3:
            continue
        try:
            m = int(parts[0])
            mx = float(parts[1])
            av = float(parts[2])
        except ValueError:
            continue
        overrides[m] = (mx, av)
    return overrides


def main():

    m_values = [1, 2, 3, 4, 5, 7, 8, 15, 16]
    overrides = try_read_overrides()
    if not overrides:
        raise FileNotFoundError(f"Overrides file not found or empty at {os.path.join(DEFAULT_TRACES_DIR, 'full_overrides.txt')}")

    max_values: list[float] = []
    avg_values: list[float] = []

    for m in m_values:
        if m in overrides:
            max_val, avg_val = overrides[m]
        else:
            # If an M is missing in overrides, default to zeros
            max_val, avg_val = 0.0, 0.0
        max_values.append(max_val)
        avg_values.append(avg_val)

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Normalize series to [0, 1]
    def normalize(series: list[float]) -> list[float]:
        mx = max(series) if series else 0.0
        return [(v / mx) if mx > 0 else 0.0 for v in series]

    max_values_n = normalize(max_values)
    avg_values_n = normalize(avg_values)

    # Plot normalized Max and Avg vs M
    plt.figure(figsize=(10, 5))
    plt.plot(m_values, max_values_n, marker='o', label='Max Voltage')
    plt.plot(m_values, avg_values_n, marker='o', label='Avg Voltage')
    plt.xlabel('M value')
    plt.ylabel('Voltage Value')
    plt.title('Full System Voltage vs M')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, 'full_voltage_vs_m.jpg')
    plt.savefig(plot_path, dpi=200, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    main()


