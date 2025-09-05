`include "h_matrix_defs.vh"

// Matrix-vector multiply: s = H_U * u^T mod 2
// H_U is 6x32, u is 32-bit, result s is 6-bit
module hu_mul (
    input  wire [31:0] u,   // information word
    output wire [5:0]  s    // result vector
);
    // Dot products (mask + reduction XOR) using shared constants
    assign s[0] = ^(u & `HU0);
    assign s[1] = ^(u & `HU1);
    assign s[2] = ^(u & `HU2);
    assign s[3] = ^(u & `HU3);
    assign s[4] = ^(u & `HU4);
    assign s[5] = ^(u & `HU5);

endmodule

module syndrome_xor_reg (
    input  wire       clk,
    input  wire       rst_n,         // active-low reset
    input  wire [5:0] syndrome_in,   // current syndrome from hu_mul
    output wire [5:0] xor_syndrome   // XOR between current and previous
);

    reg [5:0] prev_syndrome; // internal register

    // Store previous syndrome
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            prev_syndrome <= 6'b0;
        else
            prev_syndrome <= syndrome_in;
    end

    // XOR current vs previous
    assign xor_syndrome = syndrome_in ^ prev_syndrome;

endmodule

// Syndrome → Coset Leader LUT
module coset_leader_lut (
    input  wire [5:0] syndrome,      // 6-bit key
    output reg  [12:0] leader        // 13-bit coset leader
);

    always @* begin
        case (syndrome)
            6'b000000: leader = 13'b0000000000000;
            6'b100000: leader = 13'b1000000000000;
            6'b010000: leader = 13'b0100000000000;
            6'b110000: leader = 13'b1100000000000;
            6'b001000: leader = 13'b0010000000000;
            6'b101000: leader = 13'b1010000000000;
            6'b011000: leader = 13'b0110000000000;
            6'b111000: leader = 13'b0000010000010;
            6'b000100: leader = 13'b0001000000000;
            6'b100100: leader = 13'b1001000000000;
            6'b010100: leader = 13'b0101000000000;
            6'b110100: leader = 13'b0000000011000;
            6'b001100: leader = 13'b0011000000000;
            6'b101100: leader = 13'b0000000010010;
            6'b011100: leader = 13'b0000100001000;
            6'b111100: leader = 13'b0000001100000;
            6'b000010: leader = 13'b0000100000000;
            6'b100010: leader = 13'b1000100000000;
            6'b010010: leader = 13'b0100100000000;
            6'b110010: leader = 13'b0000010100000;
            6'b001010: leader = 13'b0010100000000;
            6'b101010: leader = 13'b0000000010000;
            6'b011010: leader = 13'b0000010100000;
            6'b111010: leader = 13'b0100000100000;
            6'b000110: leader = 13'b0001100000000;
            6'b100110: leader = 13'b0000001100000;
            6'b010110: leader = 13'b0010000100000;
            6'b110110: leader = 13'b0000001000010;
            6'b001110: leader = 13'b0000110000000;
            6'b101110: leader = 13'b0000100001000;
            6'b011110: leader = 13'b0000000001000;
            6'b111110: leader = 13'b1000000001000;
            6'b000001: leader = 13'b0000010000000;
            6'b100001: leader = 13'b1000010000000;
            6'b010001: leader = 13'b0100010000000;
            6'b110001: leader = 13'b0000100100000;
            6'b001001: leader = 13'b0010010000000;
            6'b101001: leader = 13'b0100000000010;
            6'b011001: leader = 13'b0000010101000;
            6'b111001: leader = 13'b0000000000010;
            6'b000101: leader = 13'b0001010000000;
            6'b100101: leader = 13'b0001001001000;
            6'b010101: leader = 13'b0000000010000;
            6'b110101: leader = 13'b1000000100000;
            6'b001101: leader = 13'b0001011000000;
            6'b101101: leader = 13'b0000100100000;
            6'b011101: leader = 13'b0000000100000;
            6'b111101: leader = 13'b1000001000000;
            6'b000011: leader = 13'b0000110000000;
            6'b100011: leader = 13'b0100010001000;
            6'b010011: leader = 13'b1000010001000;
            6'b110011: leader = 13'b0000010000000;
            6'b001011: leader = 13'b0001010000000;
            6'b101011: leader = 13'b0000100010000;
            6'b011011: leader = 13'b0000000000001;
            6'b111011: leader = 13'b0010001000000;
            6'b000111: leader = 13'b0010010000000;
            6'b100111: leader = 13'b0000000001100;
            6'b010111: leader = 13'b0000100010000;
            6'b110111: leader = 13'b0001000100000;
            6'b001111: leader = 13'b0000001000000;
            6'b101111: leader = 13'b1000001000000;
            6'b011111: leader = 13'b0100001000000;
            6'b111111: leader = 13'b0000001100000;

            default: leader = 13'b0000000000000; // fallback
        endcase
    end

endmodule

module xor_with_prev (
    input  wire        clk,
    input  wire        rst_n,   // active-low reset
    input  wire [12:0] v_in,    // input vector from lookup table
    output reg  [12:0] v_xor    // XOR result
);

    // Register to store previous vector
    reg [12:0] v_prev;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            v_prev <= 13'b0;
            v_xor  <= 13'b0;
        end else begin
            v_xor  <= v_in ^ v_prev; // XOR current with previous
            v_prev <= v_in;          // update previous with current
        end
    end

endmodule

module ecc_encoder (
    input  wire        clk,
    input  wire        rst_n,       // active-low reset
    input  wire [31:0] info_word,   // 32-bit information word
    output wire [31:0] info_out,    // unchanged information word
    output wire [12:0] v_out        // redundancy vector
);

    // Wires
    wire [5:0] xor_syndrome;       // registered/XORed syndrome
    wire [5:0] syndrome;   // combinational syndrome from hu_mul
    wire [12:0] v_lookup;  // from LUT
    wire [12:0] v_xor;     // final redundancy vector

    // 1. Syndrome calculation using hu_mul (combinational)
    hu_mul u_syndrome (
        .u(info_word),
        .s(syndrome)
    );

    // 1b. Register/XOR stage for syndrome
    syndrome_xor_reg u_syndrome_reg (
        .clk(clk),
        .rst_n(rst_n),
        .syndrome_in(syndrome),
        .xor_syndrome(xor_syndrome)
    );

    

    // 2. Lookup table (coset leader) using coset_leader_lut
    coset_leader_lut u_lut (
        .syndrome(xor_syndrome),
        .leader(v_lookup)
    );

    // 3. XOR with previous vector
    xor_with_prev u_xor_prev (
        .clk(clk),
        .rst_n(rst_n),
        .v_in(v_lookup),
        .v_xor(v_xor)
    );

    // Outputs
    assign info_out = info_word;
    assign v_out    = v_xor;

endmodule

module ecc_decoder (
    input  wire [44:0] c_in,
    output wire [31:0] data_out
);

    // 1) Syndrome: s = H * c_in^T (GF(2)) using shared HROWx
    wire [5:0] s;
    assign s[0] = ^(c_in & `HROW0);
    assign s[1] = ^(c_in & `HROW1);
    assign s[2] = ^(c_in & `HROW2);
    assign s[3] = ^(c_in & `HROW3);
    assign s[4] = ^(c_in & `HROW4);
    assign s[5] = ^(c_in & `HROW5);

    // Fast bypass: if syndrome is zero, pass-through info bits
    wire syndrome_is_zero = (s == 6'b0);

    // 2) Compare syndrome to each column H[:, col]
    wire [44:0] match_col_onehot;
    // Bind macro concatenations to wires so we can index them with variables
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
    integer i;
    // Add this after the generate block
    always @* begin
        $display("[%0t] Syndrome: 0x%02h", $time, s);
        for (i = 0; i < 45; i = i + 1) begin
            if (match_col_onehot[i]) begin
                $display("  Matched column %0d", i);
            end
        end
    end

    // 3) Flip the matching bit (if any)
    wire any_match = |match_col_onehot;

    //reverse the match_col_onehot vector to have the MSB first
    wire [44:0] flip_mask;
    generate
        for (col = 0; col < 45; col = col + 1) begin : gen_flip
            assign flip_mask[44-col] = match_col_onehot[col];
        end
    endgenerate

    wire [44:0] c_corr = c_in ^ (any_match ? flip_mask : 45'b0);

    // 4) Output corrected information part
    //assign data_out = c_corr[44:13];

    //4) Output corrected information part (bypass if s == 0)
    assign data_out = syndrome_is_zero ? c_in[44:13] : c_corr[44:13];

endmodule

// Top module: connects encoder and decoder, and compares input vs decoded output
module top_module (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] info_in,
    output wire [31:0] decoded_out,
    output wire        match
);

    wire [31:0] info_out_enc;
    wire [12:0] v_out_enc;
    wire [44:0] codeword;

    // Encoder: produce redundancy for the provided info word
    ecc_encoder u_encoder (
        .clk(clk),
        .rst_n(rst_n),
        .info_word(info_in),
        .info_out(info_out_enc),
        .v_out(v_out_enc)
    );

    // Decoder: correct up to one bit and output the info part
    ecc_decoder u_decoder (
        .c_in({info_out_enc, v_out_enc}),
        .data_out(decoded_out)
    );

    // Equality flag: original input equals decoded output
    assign match = (decoded_out == info_in);

endmodule
