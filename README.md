
# Power Efficient Error Correction Encoding for On-Chip Interconnection Links

## Overview
This project focuses on developing and analyzing power-efficient error correction techniques for reliable data transfer over on-chip interconnection links. The key objective is to minimize dynamic power consumption while ensuring data integrity.

## Project Structure

| File | Purpose |
|------|--------|
| **Comparator.py** | Contains the `Comparator` function to compare input and output data streams to verify correctness. |
| **Controller.py** | Contains the `Controller` function, likely responsible for managing the system's control flow and data path coordination. |
| **Decoder.py** | Implements the `Decoder` function, which decodes the received data and corrects potential errors. |
| **Encoder.py** | Includes `mBitBusInvert` and `Check_Invert` functions, responsible for encoding the data using m-bit bus inversion to minimize transitions and power consumption. |
| **Generator.py** | Provides the `generate` function, likely used for test data or input pattern generation. |
| **Transition_Count.py** | Contains `Transition_Count` function to calculate bit transitions, helping evaluate dynamic power consumption. |

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/power-efficient-ecc.git
cd power-efficient-ecc
```

2. (Optional) Install dependencies if any (not specified in the files yet):

```bash
pip install -r requirements.txt
```

## Usage

Each Python file contains modular functions which can be called individually or integrated into a simulation/testbench setup:

```bash
python Encoder.py
python Decoder.py
python Comparator.py
# etc.
```

Example:

```python
from Encoder import mBitBusInvert
encoded_word = mBitBusInvert(input_word)
```

## Key Features
- **Power-Conscious Encoding:** Implements m-bit bus invert encoding to minimize bit transitions and reduce dynamic power.
- **Error Detection & Correction:** Decoder module ensures data integrity.
- **Power Monitoring:** Transition counter evaluates the system's power profile.
- **Modular Design:** Separate modules for encoding, decoding, controlling, and testing.

## Authors
Shlomit Lenefsky & Omri Triki  
June 2025
