# Power Efficient Error Correction Encoding for On-Chip Interconnection Links

## Overview
This project implements and analyzes power-efficient error correction techniques for reliable data transfer over on-chip interconnection links. The key objective is to minimize dynamic power consumption while ensuring data integrity through various encoding schemes from two seminal papers in the field.

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
│   └── lfsr.py
├── coding_schemes/
│   ├── __init__.py
│   ├── base_coding_scheme.py
│   ├── paper1/
│   │   ├── __init__.py
│   │   ├── transition_signaling.py
│   │   └── offset.py
│   └── paper2/
│       ├── __init__.py
│       ├── mbit_bi.py
│       ├── dapbi.py
│       ├── dap.py
│       └── hamming_x.py
└── controller.py
```

### Key Components
| Component | Description |
|-----------|-------------|
| **config/** | Configuration files for simulation parameters and logging |
| **core/** | Core simulation functionality and utilities |
| **coding_schemes/paper1/** | Schemes from Cheng & Pedram's tutorial paper |
| **coding_schemes/paper2/** | Schemes from Sridhara & Shanbhag's unified framework |
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
1. Coding scheme selection
2. Simulation mode (Random words, LFSR sequence, or All possible words)

### Supported Coding Schemes

#### Paper 1: Memory Bus Encoding Tutorial
- **Transition Signaling**: Data encoding using signal transitions
- **Offset Encoding**: Reduces dynamic range using arithmetic differences

#### Paper 2: System-on-Chip Networks Framework
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

## Implementation Papers

### Paper 1
- Title: Memory Bus Encoding for Low Power: A Tutorial
- Authors: W.C. Cheng, M. Pedram
- Publication: Proceedings of the IEEE 2001 2nd International Symposium on Quality Electronic Design

### Paper 2
- Title: Coding for System-on-Chip Networks: A Unified Framework
- Authors: S.R. Sridhara, N.R. Shanbhag
- Publication: Proceedings of the 41st Annual Design Automation Conference (DAC '04)

## Authors
Shlomit Lenefsky & Omri Triki  
June 2025
