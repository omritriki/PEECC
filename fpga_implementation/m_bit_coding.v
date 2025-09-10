/*
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        09.2025
======================================================

File: m_bit_coding.v
Purpose: Implements M-bit Bus Invert (M-BI) encoding scheme
         - Segmented bus inversion for power reduction
         - Transition counting and inversion decision logic
         - Encoder/decoder pair with configurable segment size
*/


// Core M-BI logic: decides whether to invert segment based on transition count
module my_check_invert #(parameter A = 8)(
    input wire clk, rst_n, en,
    input wire [A-1:0] S_i,
    output wire [A-1:0] X_i,
    output wire INV_i
);
    wire [A-1:0] xor_out;
    wire [A-1:0] X_i_prev;
    wire [$clog2(A+1)-1:0] sum;
    wire equal, greater, inv_prev;

    my_buffer #(1) buf_inv (
        .clk(clk), 
        .rst_n(rst_n), 
        .en(en), 
        .in(INV_i), 
        .out(inv_prev));
    my_buffer #(A) buf_s_x (
        .clk(clk), 
        .rst_n(rst_n), 
        .en(en), 
        .in(X_i), 
        .out(X_i_prev)); 
	my_bitwiseXOR #(A) bxor (
        .a(S_i), 
        .b(X_i_prev), 
        .out(xor_out)); 
	my_adder #(A) add (
        .rst_n(rst_n), 
        .a(xor_out), 
        .sum(sum));
    my_comparator #(A) cmp (
        .sum(sum), 
        .equal(equal), 
        .greater(greater));

    assign INV_i = (equal & inv_prev) | greater;
    assign X_i = INV_i ? ~S_i : S_i;
endmodule


module my_bitwiseXOR #(parameter A = 8)(
    input wire [A-1:0] a,   
    input wire [A-1:0] b,
    output wire [A-1:0] out
);
    assign out = a ^ b;
endmodule


module my_adder #(parameter A = 8)(
    input wire rst_n,
    input wire [A-1:0] a,
    output reg [$clog2(A+1)-1:0] sum
);
    integer i;
    always @(*) begin
        if (~rst_n) begin
            sum = 0;
        end else begin
            sum = 0;
            for (i = 0; i < A; i = i + 1) begin
                sum = sum + a[i];
            end
        end
    end
endmodule


module my_comparator #(parameter A = 8)(
    input wire [$clog2(A+1)-1:0] sum,
    output wire equal,
    output wire greater
);
    assign equal = (sum == (A/2));
    assign greater = (sum > (A/2));
endmodule


// M-BI encoder: applies inversion logic across M segments
module my_encoder #(parameter M = 5, k = 32, A = 8)( 
    input wire clk, rst_n, en,
    input wire [k-1:0] S,
    output wire [k-1:0] X,
    output wire [M-1:0] INV1
);
    genvar i;
    generate
        for (i = 0; i < (k + M) % M; i = i + 1) begin : check_invert_gen1
            wire [A-2:0] S_part1 = S[i*(A-1) +: (A-1)];
            wire [A-2:0] X_part1;
            my_check_invert #(A-1) ci1 (
                .clk(clk), 
                .rst_n(rst_n), 
                .en(en),
                .S_i(S_part1),
                .X_i(X_part1), 
                .INV_i(INV1[i])
            );
            assign X[i*(A-1) +: (A-1)] = X_part1;
        end
    endgenerate
    
    genvar j;
    generate
        for (j = 0; j < (M - ((k + M) % M)); j = j + 1) begin : check_invert_gen2
	        localparam integer start = ((k+M)%M)*(A-1) + j*(A-2);
            wire [A-3:0] S_part2 = S[start +: (A-2)];
            wire [A-3:0] X_part2;
            my_check_invert #(A-2) ci2(
                .clk(clk), 
                .rst_n(rst_n), 
                .en(en),
                .S_i(S_part2),
                .X_i(X_part2), 
                .INV_i(INV1[((k+M)%M)+j])
            );
            assign X[start +: (A-2)] = X_part2; 
        end
    endgenerate
endmodule


// M-BI decoder: reverses inversion based on control bits
module my_decoder #(parameter M = 5, k = 32, A = 8)( 
    input wire [k-1:0] X,
    input wire [M-1:0] INV1,
    output wire [k-1:0] S_out
);
    genvar i;
    generate
        for (i = 0; i < (k + M) % M; i = i + 1) begin : mux_gen1
            wire [A-2:0] mux_out1;
            my_mux2x1 #(A-1) mux_inst1 (
                .sel(INV1[i]),
                .a(X[i*(A-1) +: (A-1)]),
                .b(~X[i*(A-1) +: (A-1)]),
                .out(mux_out1)
            );
            assign S_out[i*(A-1) +: (A-1)] = mux_out1;
        end
    endgenerate
    
    genvar j;
    generate
        for (j = 0; j < M-((k+M)%M); j = j + 1) begin : mux_gen2
	    localparam integer start = ((k+M)%M)*(A-1) +(j*(A-2));
            wire [A-3:0] mux_out2;
            my_mux2x1 #(A-2) mux_inst2 (
                .sel(INV1[j+((k+M)%M)]),
                .a(X[start +: (A-2)]),
                .b(~X[start +: (A-2)]),
                .out(mux_out2)
            );
            assign S_out[start +: (A-2)] = mux_out2;
        end
    endgenerate
endmodule