`include "h_matrix.vh"
`include "coset_leader_lut.vh"


// Matrix-vector multiply: s = H_U * u^T mod 2
// H_U is 6x32, u is 32-bit, result s is 6-bit
module hu_mul (
    input  wire [31:0] u,   // information word
    output wire [5:0]  s    // result vector
);
    // Dot products (mask + reduction XOR) using shared constants
    // Note: Bit order alignment with Python - assuming Python uses LSB-first indexing
    assign s[0] = ^(u & `HU0);
    assign s[1] = ^(u & `HU1);
    assign s[2] = ^(u & `HU2);
    assign s[3] = ^(u & `HU3);
    assign s[4] = ^(u & `HU4);
    assign s[5] = ^(u & `HU5);

endmodule


// Encoder aligned with Python behavior
module ecc_encoder (
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
`ifdef DEBUG
    // Debug registers for codeword and its syndrome (declare at module scope for Verilog)
    reg [44:0] cw_dbg;
    reg [5:0]  s_codeword;
`endif
    
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

`ifdef DEBUG
    always @(posedge clk) begin
        if (rst_n) begin
            // Compute codeword-level syndrome to verify H*[u|v]=0
            // Build codeword as encoder sees it (no pipeline):
            cw_dbg = {info_word, v_curr};
            s_codeword[0] = ^(cw_dbg & `HROW0);
            s_codeword[1] = ^(cw_dbg & `HROW1);
            s_codeword[2] = ^(cw_dbg & `HROW2);
            s_codeword[3] = ^(cw_dbg & `HROW3);
            s_codeword[4] = ^(cw_dbg & `HROW4);
            s_codeword[5] = ^(cw_dbg & `HROW5);
            //$display("[ENC] info=%h, s_curr=%b, delta_s=%b, addr=%b, delta_v=%013b, v_curr=%013b, Hcw=%b", 
                     //info_word, s_curr, delta_s, {delta_s[0],delta_s[1],delta_s[2],delta_s[3],delta_s[4],delta_s[5]}, delta_v, v_curr, s_codeword);
        end
    end
`endif

endmodule


module ecc_decoder (
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


// Top module with proper timing alignment
module top_module (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] info_in,
    output wire [31:0] decoded_out,
    output wire        match
);
    
    // Encoder outputs
    wire [31:0] info_out_enc;
    wire [12:0] v_out_enc;

    ecc_encoder u_encoder (
        .clk      (clk),
        .rst_n    (rst_n),
        .info_word(info_in),
        .info_out (info_out_enc),
        .v_out    (v_out_enc)
    );

    // Pipeline registers to align timing
    reg [31:0] info_pipe1;
    reg [12:0] v_pipe1;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            info_pipe1 <= 32'b0;
            v_pipe1 <= 13'b0;
        end else begin
            info_pipe1 <= info_in;
            v_pipe1 <= v_out_enc;
        end
    end

    // Build codeword: [info_bits, redundancy_bits]
    // Ensure bit ordering matches Python's np.concatenate((u_array, v_curr))
    wire [44:0] codeword = {info_pipe1, v_pipe1};

    ecc_decoder u_decoder (
        .c_in(codeword),
        .data_out(decoded_out)
    );

    // Compare input with decoded output
    assign match = (decoded_out == info_pipe1);

endmodule