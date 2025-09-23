import os
from typing import Tuple, Dict
import matplotlib.pyplot as plt


# Directories
DEFAULT_TRACES_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/voltage_traces"
OUTPUT_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing/output"


def read_traces() -> Dict[int, Tuple[float, float]]:
    """
    If a overrides file exists in the traces directory, read it and return
    a map of M -> (MaxAbs_mV, AvgAbs_mV).
    """
    path = os.path.join(DEFAULT_TRACES_DIR, "full_traces.txt")
    traces: Dict[int, Tuple[float, float]] = {}
    with open(path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
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
        traces[m] = (mx, av)
    return traces


def main():

    m_values = [1, 2, 3, 4, 5, 7, 8, 15, 16]
    traces = read_traces()

    max_values: list[float] = []
    avg_values: list[float] = []

    for m in m_values:
        max_val, avg_val = traces[m]
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