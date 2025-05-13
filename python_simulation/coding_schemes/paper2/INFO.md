# Paper Information

## Title
Coding for System-on-Chip Networks: A Unified Framework

## Authors
- S.R. Sridhara
- N.R. Shanbhag

## Publication
Proceedings of the 41st Annual Design Automation Conference (DAC '04)

## Year
2004

## Implemented Schemes
This paper presents a unified framework for error control coding in SoC networks, including:

1. **M-bit Bus Invert (M-BI)**
   - Extension of basic bus invert coding
   - Segments bus into M parts for better transition reduction
   - Adds one control bit per segment

2. **Duplicate-Add-Parity (DAP)**
   - Simple error detection through bit duplication
   - Adds parity bit for additional error checking
   - Bus width: 2k + 1 for k-bit input

3. **DAP-Bus Invert (DAP-BI)**
   - Combines DAP with bus invert coding
   - Error detection with power optimization
   - Maintains DAP's error detection capabilities

4. **Extended Hamming Code (HammingX)**
   - Single error correction capability
   - Added shielding bits for transition reduction
   - Bus width: k + 2r - 1 (k data bits, r parity bits, r-1 shielding bits)

## Implementation Notes
- All schemes except M-BI support error detection/correction
- Focus on both power efficiency and reliability
- Novel combination of coding techniques for SoC applications