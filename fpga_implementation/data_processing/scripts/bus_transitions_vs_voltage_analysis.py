import os
from typing import Dict, Tuple
import matplotlib.pyplot as plt


BASE_DP_DIR = "/Users/omritriki/Programming/PEECC/fpga_implementation/data_processing"
HIST_SUMMARY = f"{BASE_DP_DIR}/m_bit_histograms/output/summary_transitions.txt"
VOLT_SUMMARY = f"{BASE_DP_DIR}/voltage_traces/output/max_and_avg_c_vs_m.txt"
COMBINED_OUT_DIR = f"{BASE_DP_DIR}/output"


def read_csv_as_map(path: str) -> Tuple[str, Dict[int, Tuple[str, ...]]]:
    """
    Reads a small CSV (comma-separated) file into a map keyed by integer M.
    Returns (header, map[M] = tuple(columns_after_M)).
    Assumes first column name is 'M'.
    """
    rows: Dict[int, Tuple[str, ...]] = {}
    header = ""
    if not os.path.exists(path):
        return header, rows
    with open(path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
        return header, rows
    header = lines[0]
    for ln in lines[1:]:
        parts = [p.strip() for p in ln.split(",")]
        if not parts:
            continue
        try:
            m_val = int(parts[0])
        except ValueError:
            continue
        rows[m_val] = tuple(parts[1:])
    return rows


def main():
    # Load histogram summary: M,Average Bit Transitions,Max Transitions
    # hist_map = read_csv_as_map(HIST_SUMMARY)

    # Load voltage summary: M,MaxC_mV,AvgC_0_to_127000_mV
    volt_map = read_csv_as_map(VOLT_SUMMARY)

    # Merge by M (intersection ensures all 4 values exist)
    # common_ms = sorted(set(hist_map.keys()) & set(volt_map.keys()))
    common_ms = sorted(volt_map.keys())  # Only use voltage data

    os.makedirs(COMBINED_OUT_DIR, exist_ok=True)

    # Build series for plotting
    Ms = common_ms
    # avg_transitions = [float(hist_map[m][0]) for m in Ms]
    # max_transitions = [float(hist_map[m][1]) for m in Ms]
    max_voltage = [float(volt_map[m][0]) for m in Ms]
    avg_consumption = [float(volt_map[m][1]) for m in Ms]

    # Normalize each series to [0, 1] for comparable scales
    def normalize(series):
        mx = max(series) if series else 0.0
        return [ (v / mx) if mx > 0 else 0.0 for v in series ]

    # max_transitions_n = normalize(max_transitions)
    # avg_transitions_n = normalize(avg_transitions)
    max_voltage_n = normalize(max_voltage)
    avg_consumption_n = normalize(avg_consumption)

    # Plot normalized series
    plt.figure(figsize=(10, 5))
    # plt.plot(Ms, max_transitions_n, marker='o', label='Max Transitions')
    # plt.plot(Ms, avg_transitions_n, marker='o', label='Avg Transitions')
    plt.plot(Ms, max_voltage_n, marker='o', label='Max Voltage [mV]')
    plt.plot(Ms, avg_consumption_n, marker='o', label='Avg Voltage [mV]')
    plt.xlabel('M value')
    plt.ylabel('Normalized Value')
    plt.title('Voltage vs M (Normalized)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.ylim(0.8, 1.1)
    # Save and show
    plt.savefig(os.path.join(COMBINED_OUT_DIR, 'voltage_plot_normalized.jpg'), dpi=200, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    main()


