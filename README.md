# Power Efficient Error Correction Encoding for On-Chip Interconnection Links

## Overview
This project focuses on developing and analyzing power-efficient error correction techniques for reliable data transfer over on-chip interconnection links. The key objective is to minimize dynamic power consumption while ensuring data integrity. The project implements various encoding and decoding schemes, including M-bit Bus Invert (MbitBI) and Duplicate-Add Parity Bus Invert (DAPBI).

## Project Structure

| File | Purpose |
|------|--------|
| **coding_schemes/mbit_bi.py** | Implements the M-bit Bus Invert (MbitBI) encoding and decoding scheme to minimize transitions. |
| **coding_schemes/dapbi.py** | Implements the Duplicate-Add Parity Bus Invert (DAPBI) encoding and decoding scheme for error detection and transition minimization. |
| **core/Generator.py** | Provides the `generate` function to create test data or input patterns in various modes (random, integer-based, or LFSR). |
| **core/Transition_Count.py** | Contains the `transition_count` function to calculate bit transitions, helping evaluate dynamic power consumption. |
| **core/error_generator.py** | Introduces errors into binary vectors based on a specified error probability for testing purposes. |
| **core/mbit_bi_average.py** | Calculates the average number of bit transitions for M-bit Bus Invert encoding. |
| **Controller.py** | Manages the simulation flow, allowing users to test encoding schemes with random words, all possible words, or LFSR-generated words. |
| **Comparator.py** | Compares input and output data streams to verify correctness. |
| **logging_config.py** | Configures logging for the simulation, including file and console handlers. |

## Installation

1. Clone the repository:

```bash
git clone https://github.com/omritriki/PEECC.git
cd PEECC
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The project is modular, and each Python file can be used independently or as part of a simulation setup. The main entry point is `controller.py`, which allows users to run simulations with different encoding schemes.

### Running the Controller
```bash
python controller.py
```

### Example Usage
```python
from coding_schemes.mbit_bi import MbitBI
from coding_schemes.dapbi import DAPBI

# Example: Using MbitBI encoding
mbit_bi = MbitBI()
encoded = mbit_bi.encode(input_sequence, previous_sequence, M=4)
decoded = mbit_bi.decode(encoded, M=4)

# Example: Using DAPBI encoding
dapbi = DAPBI()
encoded = dapbi.encode(input_sequence, previous_sequence)
decoded = dapbi.decode(encoded)
```

## Key Features
- **Encoding Schemes:**
  - **M-bit Bus Invert (MbitBI):** Reduces transitions by segmenting the input and inverting segments when necessary.
  - **Duplicate-Add Parity Bus Invert (DAPBI):** Minimizes transitions and adds error detection using parity and inversion bits.
- **Error Injection:** Simulates errors in encoded data for testing decoder robustness.
- **Power Monitoring:** Transition counter evaluates the system's power profile.
- **Modular Design:** Separate modules for encoding, decoding, controlling, and testing.

## Authors
Shlomit Lenefsky & Omri Triki  
June 2025
