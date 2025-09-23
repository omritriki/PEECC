# Power Efficient Error Correction Encoding for On-Chip Interconnection Links

## Overview
This project implements and analyzes power-efficient error correction techniques for reliable data transfer over on-chip interconnection links. The **main focus** is on **Power Efficient SEC**, a novel approach that minimizes dynamic power consumption while providing robust error correction capabilities. The system also includes various encoding schemes from two seminal papers in the field for comparative analysis.

## Project Structure

```
PEECC/
├── python_simulation/           # Software simulation and analysis
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logging_config.py
│   │   └── simulation_config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   ├── simulator.py
│   │   ├── transition_count.py
│   │   ├── error_generator.py
│   │   ├── comparator.py
│   │   └── lfsr.py
│   ├── coding_schemes/
│   │   ├── __init__.py
│   │   ├── base_coding_scheme.py
│   │   ├── paper1/
│   │   │   ├── __init__.py
│   │   │   ├── transition_signaling.py
│   │   │   ├── offset.py
│   │   │   ├── offset_xor.py
│   │   │   └── mbit_bi.py
│   │   ├── paper2/
│   │   │   ├── __init__.py
│   │   │   ├── dapbi.py
│   │   │   ├── dap.py
│   │   │   └── hamming_x.py
│   │   └── syndrome_based/          # MAIN PROJECT FOCUS
│   │       ├── __init__.py
│   │       ├── H_matrix.py          
│   │       ├── syndrome_based_encoder.py  
│   │       ├── syndrome_lut.py      
│   │       ├── syndrome_encoder_summary.txt  
│   │       └── matrix_generation/  
│   │           ├── main.py          
│   │           ├── hv_greedy_algorithm.py  
│   │           ├── hu_generator.py  
│   │           ├── generate_lut.py  
│   │           └── output/         
│   │               ├── generated_H_matrix.py  
│   │               └── generated_syndrome_lut.py  
│   └── controller.py
└── fpga_implementation/         # Hardware implementation and analysis
    ├── datapath.v              
    ├── fsm_controller.v        
    ├── top_module.v            
    ├── top_wrappers.v          
    ├── top_wrapper_tb.v        
    ├── m_bit_coding.v          
    ├── uart_files/             # UART interface modules
    │   ├── uart_interface.vhd
    │   ├── uart2BusTop_pkg.vhd
    │   ├── uartRx.vhd
    │   ├── uartTx.vhd
    │   └── uartTop.vhd
    ├── scope_interface/        # Oscilloscope data acquisition tools
    ├── data_processing/        # Post-processing and analysis tools
    │   ├── voltage_traces/     # Manual values + raw traces
    │   │   ├── full_traces.txt # Editable Max/Avg per M used for plotting
    │   │   └── output/         # Generated plots (JPG)
    │   └── m_bit_histograms/   
    │       ├── register_values/
    │       └── output/         
    └── syndrome_based_coding/  # Power Efficient SEC hardware modules
        ├── syndrome_based_coding.v  
        ├── new_datapath.v
        ├── new_datapath_tb.v
        ├── h_matrix.vh
        └── coset_leader_lut.vh
```

### Key Components

#### Python Simulation
| Component | Description |
|-----------|-------------|
| **config/** | Configuration files for simulation parameters and logging |
| **core/** | Core simulation functionality and utilities |
| **coding_schemes/paper1/** | Schemes from Cheng & Pedram's tutorial paper |
| **coding_schemes/paper2/** | Schemes from Sridhara & Shanbhag's unified framework |
| **coding_schemes/syndrome_based/** | **MAIN PROJECT: Power Efficient SEC** |
| **controller.py** | Main entry point for running simulations |

#### FPGA Implementation
| Component | Description |
|-----------|-------------|
| **datapath.v** | Main data-path pipeline implementing encoder/decoder flow |
| **fsm_controller.v** | Finite state machine controlling pipeline enables and UART handshakes |
| **top_module.v** | Top-level SoC integration of FSM, data-path, and UART interface |
| **top_wrappers.v** | Board-level wrapper with PLL for system clocks and UART IO |
| **top_wrapper_tb.v** | UART-driven testbench for hardware validation |
| **m_bit_coding.v** | M-bit Bus Invert (M-BI) encoding modules |
| **uart_files/** | UART interface modules for PC communication |
| **scope_interface/** | Oscilloscope data acquisition and measurement tools |
| **data_processing/** | Post-processing tools for voltage traces and histogram analysis |
| **syndrome_based_coding/** | Power Efficient SEC hardware modules |

## Main Project: Power Efficient SEC

### Overview
The **Power Efficient SEC** is the primary contribution of this project. It implements a novel approach that combines error correction with power efficiency through intelligent redundancy encoding.

### Key Features
- **6×45 Parity Check Matrix**: H = [H_U | H_V] where H_U is 6×32 (information) and H_V is 6×13 (redundancy)
- **Automated Matrix Generation**: Complete H_V and H_U matrix generation using greedy algorithms
- **Automatic LUT Generation**: Coset leaders lookup table generated automatically for any H_V matrix
- **Minimum Transition Encoding**: Optimizes bus switching activity while maintaining error correction
- **O(1) Lookup Complexity**: Efficient encoding through precomputed coset leaders
- **32-bit Information Words**: Designed specifically for 32-bit data with 13-bit redundancy
- **Drop-in Replacement**: Generated matrices work seamlessly with existing code

### Mathematical Foundation
- **H_V Matrix Structure**: [I_6 | H_extra] where I_6 is 6×6 identity matrix and H_extra contains 7 additional vectors
- **Greedy Algorithm**: H_extra vectors chosen to ensure every 6-vector expressible as sum of at most 2 vectors
- **Column-Space Relation**: Every column of H_U lies in the span of H_V columns
- **Multiplicity**: Each syndrome corresponds to 128 valid redundancy vectors (2^7)
- **Full Rank**: H matrix has rank 6, ensuring all parity-check equations are linearly independent
- **Coset Leaders**: Minimum-weight redundancy vectors for each possible syndrome

### Encoding Process
1. **Information Processing**: 32-bit input word u
2. **Syndrome Computation**: s = H_U @ u^T (6-bit syndrome)
3. **Delta-Syndrome Flow**: For minimum transitions, compute Δs = s_prev ⊕ s_curr
4. **Coset Leader Lookup**: Find minimum-weight v such that H_V @ v^T = Δs
5. **Redundancy Generation**: v_curr = v_prev ⊕ Δv

### Performance Characteristics
- **Maximum Transition Cost**: 2 bits
- **Average Transition Cost**: ~1.78 bits
- **Error Correction**: Single-bit error detection and correction
- **Area Overhead**: 13 bits (40.6% for 32-bit data)

### Matrix Generation
Generate matrices and LUT with a single command:
```bash
cd python_simulation/coding_schemes/syndrome_based/matrix_generation
python main.py
```

### Usage
```python
# Option 1: Use original hard-coded matrices
from coding_schemes.syndrome_based.H_matrix import return_H_V, return_H_U

# Option 2: Use generated matrices (drop-in replacement)
from coding_schemes.syndrome_based.matrix_generation.output.generated_H_matrix import return_H_V, return_H_U

# Use with encoder
from coding_schemes.syndrome_based.syndrome_based_encoder import SyndromeBasedEncoder
encoder = SyndromeBasedEncoder()  # Automatically generates LUT if needed

# Encode 32-bit information word
u_bits = [0, 1, 0, 1, ...]  # 32 bits
c_prev = [0] * 45  # Previous codeword
encoded = encoder.encode(u_bits, c_prev)  # 45-bit codeword
```

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

### Software Simulation
Run the simulation controller:
```bash
python python_simulation/controller.py
```

The controller will prompt for:
1. Coding scheme selection (including the main syndrome-based encoder)
2. Simulation mode (Random words, LFSR sequence, or All possible words)

### Hardware Implementation
The FPGA implementation provides a complete hardware validation platform:

#### Synthesis and Implementation
1. **Top-level Module**: `top_wrappers.v` - Board-level wrapper with PLL
2. **Core Logic**: `top_module.v` - SoC integration of FSM, data-path, and UART
3. **Data Path**: `datapath.v` - Main pipeline implementing encoder/decoder flow
4. **Control**: `fsm_controller.v` - State machine for pipeline orchestration

#### Testing and Validation
1. **Testbench**: `top_wrapper_tb.v` - UART-driven validation
2. **UART Interface**: Complete PC communication stack
3. **Scope Interface**: Oscilloscope data acquisition tools
4. **Data Processing**: Post-processing for voltage traces and histograms

#### Hardware Features
- **32-bit data width** with configurable M-bit segmentation
- **UART communication** for PC control and data logging
- **Transition counting** with histogram accumulation
- **Real-time power measurement** via oscilloscope interface
- **Configurable encoding schemes** via UART commands

### Data Processing and Analysis

#### Voltage Plot (manual overrides workflow)
- **Script**: `fpga_implementation/data_processing/scripts/full_system_voltage_analysis.py`
- **Function**: Reads `full_traces.txt`, normalizes each series independently, and saves a plot of Max/Avg vs M.
- **Output**: `fpga_implementation/data_processing/output/full_voltage_vs_m.jpg`
- **Run**:
  ```bash
  python -u fpga_implementation/data_processing/scripts/full_system_voltage_analysis.py
  ```

#### M-bit Histogram Generation
- **Script**: `fpga_implementation/data_processing/m_bit_histograms/histogram_from_txt.py`
- **Function**: Generates transition count histograms from register capture data
- **Input**: Register count files in `fpga_implementation/data_processing/m_bit_histograms/register_values/`
- **Output**: Histogram images saved to `fpga_implementation/data_processing/m_bit_histograms/output/`
- **Usage**:
  ```bash
  python -u fpga_implementation/data_processing/m_bit_histograms/histogram_from_txt.py
  ```

### Supported Coding Schemes

#### **MAIN PROJECT: Power Efficient SEC**
- **Syndrome-Based Encoder**: Novel approach combining error correction with power efficiency
  - 32-bit information words with 13-bit redundancy
  - Automated matrix generation using greedy algorithms
  - Automatic coset leaders lookup table generation
  - Minimum transition encoding for power optimization
  - Single-bit error detection and correction
  - Drop-in replacement matrices for seamless integration

#### Paper 1: Memory Bus Encoding Tutorial
- **Transition Signaling**: Data encoding using signal transitions
- **Offset Encoding**: Reduces dynamic range using arithmetic differences
- **Offset XOR**: Enhanced offset encoding with XOR operations
- **M-bit Bus Invert (M-BI)**: Reduces transitions through segmented bus inversion

#### Paper 2: System-on-Chip Networks Framework
- **Duplicate-Add Parity Bus Invert (DAP-BI)**: Combines duplication and bus inversion
- **Duplicate-Add Parity (DAP)**: Basic error detection through duplication
- **Extended Hamming (HammingX)**: Single error correction capability

### Simulation Modes
1. **Random Words**: Generates random test vectors
2. **LFSR**: Uses Linear Feedback Shift Register for sequence generation
3. **All Possible Words**: Tests every possible input combination

### Error Handling
- **Syndrome-based**: Automatic error detection and correction with optimized power consumption
- Configurable error injection for all supported schemes
- Error detection and correction capabilities vary by scheme
- Automatic validation of encoding/decoding correctness

## Key Features

### Software Simulation
- **Novel Syndrome-Based Error Correction**: Main project contribution
- **Automated Matrix Generation**: Complete H_V and H_U matrix generation with single command
- **Greedy Algorithm**: Optimal H_V matrix with identity + 7 extra vectors
- **Drop-in Replacement**: Generated matrices work seamlessly with existing code
- Modular design with clear separation of concerns
- Configurable simulation parameters
- Comprehensive logging and statistics
- Multiple generation modes for thorough testing
- Support for various encoding schemes with different error handling capabilities
- **Automatic LUT Generation**: No manual setup required for syndrome-based encoding

### Hardware Implementation
- **Complete FPGA Platform**: Full hardware validation of encoding schemes
- **Real-time Processing**: Hardware-accelerated encoding/decoding pipeline
- **UART Communication**: PC control and data logging interface
- **Oscilloscope Integration**: Real-time power measurement and analysis
- **Transition Histogram**: Hardware-accelerated transition counting
- **Configurable Parameters**: Runtime configuration via UART commands
- **Professional Design**: Clean, documented, and synthesis-ready Verilog code
- **Comprehensive Testing**: UART-driven testbench for validation
- **Data Processing Tools**: Python scripts for post-processing measurement data
- **Power Efficient SEC**: Novel syndrome-based error correction with coset leader lookup
- **M-bit Bus Invert**: Segmented bus inversion for power reduction

## Project Statistics
- **Total Code Lines**: 5,836 (excluding data files, logs, and documentation)
- **File Types**: Python (.py), Verilog (.v), VHDL (.vhd), Verilog Headers (.vh)
- **Main Components**: 
  - Software simulation framework with automated matrix generation
  - Complete FPGA implementation with UART communication
  - Data processing tools for voltage analysis and histogram generation
  - Power Efficient SEC with novel syndrome-based error correction

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
Prof. Osnat Keren
Prof. Itamar Levi

September 2025
