# Power Efficient Error Correction Encoding for On-Chip Interconnection Links

## Overview
This project implements and analyzes power-efficient error correction techniques for reliable data transfer over on-chip interconnection links. The key objective is to minimize dynamic power consumption while ensuring data integrity through various encoding schemes including M-bit Bus Invert (MbitBI), Duplicate-Add Parity Bus Invert (DAPBI), Duplicate-Add Parity (DAP), and Extended Hamming Code (HammingX).

## Project Structure

```
python_simulation/
├── config/
│   ├── __init__.py
│   ├── logging_config.py
│   └── simulation_config.py
├── core/
│   ├── __init__.py
│   ├── generator.py
│   ├── simulator.py
│   ├── transition_count.py
│   ├── error_generator.py
│   ├── comparator.py
│   └── mbit_bi_average.py
├── coding_schemes/
│   ├── __init__.py
│   ├── base_coding_scheme.py
│   ├── mbit_bi.py
│   ├── dapbi.py
│   ├── dap.py
│   └── hamming_x.py
└── controller.py
```

### Key Components
| Component | Description |
|-----------|-------------|
| **config/** | Configuration files for simulation parameters and logging |
| **core/** | Core simulation functionality and utilities |
| **coding_schemes/** | Implementation of various encoding/decoding schemes |
| **controller.py** | Main entry point for running simulations |

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

Run the simulation controller:
```bash
python python_simulation/controller.py
```

The controller will prompt for:
1. Coding scheme selection (M-BI, DAP-BI, DAP, or HammingX)
2. Simulation mode (Random words, LFSR sequence, or All possible words)

### Supported Coding Schemes
- **M-bit Bus Invert (M-BI)**: Reduces transitions through segmented bus inversion
- **Duplicate-Add Parity Bus Invert (DAP-BI)**: Combines duplication and bus inversion
- **Duplicate-Add Parity (DAP)**: Basic error detection through duplication
- **Extended Hamming (HammingX)**: Single error correction capability

### Simulation Modes
1. Random Words: Generates random test vectors
2. LFSR: Uses Linear Feedback Shift Register for sequence generation
3. All Possible Words: Tests every possible input combination

### Error Handling
- Configurable error injection for supported schemes
- Error detection and correction capabilities vary by scheme
- Automatic validation of encoding/decoding correctness

## Key Features
- Modular design with clear separation of concerns
- Configurable simulation parameters
- Comprehensive logging and statistics
- Multiple generation modes for thorough testing
- Support for various encoding schemes with different error handling capabilities

## Authors
Shlomit Lenefsky & Omri Triki  
June 2025
