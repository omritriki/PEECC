// H_U rows (MSB = column 0) - matches python_simulation H_matrix.py
`define HU0 32'hC3FDD5CB
`define HU1 32'hDF80A2FC
`define HU2 32'hA344B72E
`define HU3 32'h1BB295A5
`define HU4 32'hE98FAD39
`define HU5 32'hA5AE5E33

// H_V rows (MSB = column 32) - matches python_simulation H_matrix.py
`define HV0 13'b1000000101010
`define HV1 13'b0100000110111
`define HV2 13'b0010001001111
`define HV3 13'b0001001010100
`define HV4 13'b0000101101101
`define HV5 13'b0000011110011

// Full 45-bit rows
`define HROW0 {`HU0, `HV0}
`define HROW1 {`HU1, `HV1}
`define HROW2 {`HU2, `HV2}
`define HROW3 {`HU3, `HV3}
`define HROW4 {`HU4, `HV4}
`define HROW5 {`HU5, `HV5}


