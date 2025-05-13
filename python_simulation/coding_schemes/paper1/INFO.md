# Paper Information

## Title
Memory Bus Encoding for Low Power: A Tutorial

## Authors
- W.C. Cheng
- M. Pedram

## Publication
Proceedings of the IEEE 2001 2nd International Symposium on Quality Electronic Design (ISQED '01)

## Year
2001

## Implemented Schemes
This paper introduces several low-power bus encoding schemes, including:

1. **Transition Signaling**
   - Basic transition-based encoding
   - Reduces switching activity by encoding transitions instead of absolute values

2. **Offset Encoding**
   - Similar to Transition Signaling but uses two's complement arithmetic
   - Particularly effective for sequential data access with fixed stride
   - Reduces dynamic range of transmitted values

## Implementation Notes
- Both schemes maintain state (previous word) for encoding/decoding
- No error correction capabilities
- Focus on power efficiency through transition reduction