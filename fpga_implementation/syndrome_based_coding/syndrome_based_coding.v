/*
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        09.2025
======================================================

File: syndrome_based_coding.v
Purpose: Implements the main Power Efficient SEC encoder/decoder modules
         - Syndrome-based encoding with coset leader lookup
         - Single-bit error correction via syndrome matching
         - Delta-syndrome flow for minimum transition encoding
*/


`include "h_matrix.vh"
`include "coset_leader_lut.vh"


// Matrix-vector multiply: s = H_U * u^T mod 2
// H_U is 6x32, u is 32-bit, result s is 6-bit
// Uses bitwise AND + XOR reduction for efficient GF(2) multiplication
module hu_mul (
    input  wire [31:0] u,  
    output wire [5:0]  s    
);
    // Dot products (mask + reduction XOR) using shared constants
    assign s[0] = ^(u & `HU0);
    assign s[1] = ^(u & `HU1);
    assign s[2] = ^(u & `HU2);
    assign s[3] = ^(u & `HU3);
    assign s[4] = ^(u & `HU4);
    assign s[5] = ^(u & `HU5);

endmodule


// Main Power Efficient SEC encoder implementing delta-syndrome flow
module my_encoder #(parameter M = 5, k = 32, A = 8)(
    input  wire        clk,
    input  wire        rst_n,       // active-low reset
    input  wire [31:0] info_word,   // 32-bit information word
    output wire [31:0] info_out,    // unchanged information word
    output wire [12:0] v_out        // redundancy vector
);

    // Step 1: Compute current syndrome s_curr = H_U @ u_bits
    wire [5:0] s_curr;
    hu_mul u_syndrome (.u(info_word), .s(s_curr));

    // Step 2: Previous syndrome register (syndrome_prev in Python)
    reg [5:0] syndrome_prev;
    
    // Step 3: Compute delta syndrome: delta_s = syndrome_prev XOR s_curr
    wire [5:0] delta_s = syndrome_prev ^ s_curr;

    // Step 4: Lookup delta_v from LUT
    wire [12:0] delta_v;
    coset_leader_lut u_lut (
        .syndrome(delta_s),
        .leader(delta_v)
    );

    // Step 5: Previous redundancy vector register (v_prev in Python)
    reg [12:0] v_prev;
    
    // Step 6: Compute current redundancy: v_curr = v_prev XOR delta_v
    wire [12:0] v_curr = v_prev ^ delta_v;

    // Step 7: Update state registers at clock edge
    // IMPORTANT: Update syndrome_prev AFTER computing v_curr (matches Python timing)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            syndrome_prev <= 6'b0;
            v_prev <= 13'b0;
        end else begin
            // Update previous syndrome with current syndrome (Python: self.syndrome_prev = s_curr)
            syndrome_prev <= s_curr;
            // Update previous redundancy with current redundancy
            v_prev <= v_curr;
        end
    end

    // Output assignments
    assign v_out = v_curr;
    assign info_out = info_word;

endmodule


// Power Efficient SEC decoder with single-bit error correction
module my_decoder #(parameter M = 5, k = 32, A = 8)(
    input  wire [44:0] c_in,
    output wire [31:0] data_out
);

    // Step 1: Compute syndrome s = H * c_in^T (GF(2))
    wire [5:0] s;
    assign s[0] = ^(c_in & `HROW0);
    assign s[1] = ^(c_in & `HROW1);
    assign s[2] = ^(c_in & `HROW2);
    assign s[3] = ^(c_in & `HROW3);
    assign s[4] = ^(c_in & `HROW4);
    assign s[5] = ^(c_in & `HROW5);

    // Step 2: Fast bypass for zero syndrome
    wire syndrome_is_zero = (s == 6'b0);

    // Step 3: Find matching column in H matrix
    wire [44:0] match_col_onehot;
    
    // Extract H matrix columns for comparison
    wire [44:0] HROW0_W = `HROW0;
    wire [44:0] HROW1_W = `HROW1;
    wire [44:0] HROW2_W = `HROW2;
    wire [44:0] HROW3_W = `HROW3;
    wire [44:0] HROW4_W = `HROW4;
    wire [44:0] HROW5_W = `HROW5;
    
    genvar col;
    generate
        for (col = 0; col < 45; col = col + 1) begin : gen_match
            wire [5:0] Hcol = {
                HROW5_W[44-col],
                HROW4_W[44-col],
                HROW3_W[44-col],
                HROW2_W[44-col],
                HROW1_W[44-col],
                HROW0_W[44-col]
            };
            assign match_col_onehot[col] = (Hcol == s);
        end
    endgenerate

    // Step 4: Create error correction mask
    wire any_match = |match_col_onehot;
    
    // Create flip mask - direct bit position mapping
    wire [44:0] flip_mask;
    generate
        for (col = 0; col < 45; col = col + 1) begin : gen_flip
            // If H column 'col' matches, flip codeword bit at position (44-col)
            assign flip_mask[44-col] = match_col_onehot[col];
        end
    endgenerate

    // Step 5: Apply error correction
    wire [44:0] c_corr = c_in ^ (any_match ? flip_mask : 45'b0);

    // Step 6: Extract corrected information bits
    // Use bypass for zero syndrome (no error case)
    assign data_out = syndrome_is_zero ? c_in[44:13] : c_corr[44:13];

endmodule