"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""


// If we decide buffer doesn't need an enable signal, we can remove it from the module and
// remove it from check_invert modules

module MUX2x1 #(parameter A = 8)(
    input wire sel,
    input wire [A-1:0] a,
    input wire [A-1:0] b,
    output wire [A-1:0] out
);
    assign out = sel ? b : a;
endmodule


module Buffer #(parameter A = 1)(  
    input wire clk,
    input wire rst, 
    input wire en,  //is it needed?
    input wire [A-1:0] in,
    output reg [A-1:0] out
);
    always @(posedge clk or posedge rst) begin // check posedge/negedge
        if (rst)
            out <= 0;
        else if (en)
            out <= in;
    end
endmodule


module BitwiseXOR #(parameter A = 8)(
    input wire [A-1:0] a,   
    input wire [A-1:0] b,
    output wire [A-1:0] out
);
    assign out = a ^ b;
endmodule


module Adder #(parameter A = 8)(
    input wire [A-1:0] a,
    output reg [$clog2(A+1)-1:0] sum 
);
    integer i;
    always @(*) begin
        sum = 0;
        for (i = 0; i < A; i = i + 1) begin
            sum = sum + a[i];
        end
    end
endmodule


module Comparator #(parameter A = 8)(
    input wire [$clog2(A+1)-1:0] sum,
    output wire equal,
    output wire greater
);
    assign equal = (sum == (A/2));
    assign greater = (sum > (A/2));
endmodule


/*
Module:     CheckInvert
Description:
            This parameterized module checks whether inversion should be applied to an input data word
Notations:
            S_i   - Input data word (original data)
            X_i   - Encoded data word (possibly inverted version of S_i)
            INV_i - Inversion flag indicating whether inversion was applied
Parameters:
            A - Width of the input and output data words. Adjustable to support various bus sizes.
*/
module CheckInvert #(parameter A = 8)( // verify different A's
    input wire clk,
    input wire rst, 
    input wire en,  //is it needed?
    input wire [A-1:0] S_i,
    output wire [A-1:0] X_i,
    output wire INV_i
);
    wire [A-1:0] xor_out;
    wire [A-1:0] X_i_prev;
    wire [$clog2(A+1)-1:0] sum;
    wire equal, greater, inv_prev;

    Buffer #(1) buf_inv (.clk(clk), .rst(rst), .en(en), .in(INV_i), .out(inv_prev));
    Buffer #(A) buf_s_x (.clk(clk), .rst(rst), .en(en), .in(X_i), .out(X_i_prev)); 
	BitwiseXOR #(A) bxor (.a(S_i), .b(X_i_prev), .out(xor_out)); 
	Adder #(A) add (.a(xor_out), .sum(sum));
    Comparator #(A) cmp (.sum(sum), .equal(equal), .greater(greater));

    assign INV_i = (equal & inv_prev) | greater;
    assign X_i = INV_i ? ~S_i : S_i;
endmodule


/*
Module:     Encoder
Description:
            Applies bus invert encoding to a wide input word, partitioning it into segments
            and encoding each segment to reduce bit transitions
Notations:
            S_i   - Input data word segment
            X_i   - Encoded data word segment
            INV_i - Inversion flag per segment
Parameters:
            M - Number of segments 
            k - Total input/output word width
            A - Segment width
*/

//////Maybe A should be calculated inside and not given as a parameter???
module Encoder #(parameter M = 5, k = 32, A = 8)( 
    input wire clk,
    input wire rst,
    input wire en,
    input wire [k-1:0] S,
    output wire [k-1:0] X,
    output wire [M-1:0] INV
);
    genvar i;
    generate
        for (i = 0; i < (k + M) % M; i = i + 1) begin : check_invert_gen1
            wire [A:0] S_part1 = S[i*(A+1) +: (A+1)];
            CheckInvert #(A+1) ci1 (
                .clk(clk), .rst(rst), .en(en),
                .S_i(S_part1),
                .X_i(X[i*(A+1) +: (A+1)]),
                .INV_i(INV[i])
            );
        end
    endgenerate
	
	genvar j;
	generate
        for (j = (k + M) % M; j < M; j = j + 1) begin : check_invert_gen2
            wire [A-1:0] S_part2 = S[j*(A) +: (A)];
            CheckInvert #(A) ci2(
                .clk(clk), .rst(rst), .en(en),
                .S_i(S_part2),
                .X_i(X[j*(A) +: (A)]),
                .INV_i(INV[j])
            );
        end
    endgenerate
endmodule


/*
Module:     Decoder
Description:
            Decodes bus invert encoded data by applying inversion based on inversion flags
Notations:
            X_i   - Encoded data word segment
            INV_i - Inversion flag per segment
            S_i   - Decoded (original) data word segment
Parameters:
            M - Number of segments (inversion flags)
            k - Total input/output word width
            A - Segment width
*/
module Decoder #(parameter M = 5, k = 32, A = 8)( 
    input wire [k-1:0] X,
    input wire [M-1:0] INV,
    output wire [k-1:0] S_out
);
    genvar i;
    generate
        for (i = 0; i < (k + M) % M; i = i + 1) begin : mux_gen1
          MUX2x1 #(A+1) mux_inst1 (
                .sel(INV[i]),
                .a(X[i*(A+1) +: (A+1)]),
                .b(~X[i*(A+1) +: (A+1)]),
                .out(S_out[i*(A+1) +: (A+1)])
            );
        end
    endgenerate
	
	genvar j;
    generate
        for (j = (k + M) % M; j < M; j = j + 1) begin : mux_gen2
          MUX2x1 #(A) mux_inst2 (
                .sel(INV[j]),
                .a(X[j*(A) +: (A)]),
                .b(~X[j*(A) +: (A)]),
                .out(S_out[j*(A) +: (A)])
            );
        end
    endgenerate
endmodule


////////// UNCHECKED MODULES //////////
module Transition_Counter #(parameter n = 8) ( // ***note you will get the value with one cycle delay ***
    input wire clk,
    input wire rst,
    input wire en,
    input wire [n-1:0] data_in,
    output reg [10:0] registers [(n/2):0]
);
    
    reg [n-1:0] prev_data;
    wire [n-1:0] xor_result;
	reg [9:0] registers_cnt [(n/2):0];
	reg [$clog2(n+1)-1:0] transition_count = {$clog2(n+1){1'b0}};
    integer i, j;
    
    // Compute bitwise XOR to determine transitions
    assign xor_result = data_in ^ prev_data;
     
    always @(posedge clk or posedge rst) begin
	// reset
        if (rst) begin
            prev_data <= (n-1){1'b0};
			// Reset all counters
			for (i = 0; i < (n/2)+1; i = i + 1) begin
                registers[i] <= 0; 
			end
		// activate
        end else if (en) begin
            prev_data <= data_in;
            transition_count <= 0;
            // Count the number of transitions
            for (i = 0; i < n; i = i + 1) begin
                transition_count = transition_count + xor_result[i];
            end
			// Increment the corresponding register
            registers_cnt[transition_count] <= registers_cnt[transition_count] + 1;
            
			registers <= registers_cnt; //output only at the end on 2000 test or in every test
        end
    end
endmodule

module K_Comparator #(parameter k = 32)(
    input wire clk,
    input wire [k-1:0] S_in,
    input wire [k-1:0] S_out,
	output wire equal
);
	//wire [k-1:0] xored;
	//BitwiseXOR bxor (.a(S_out), .b(S_in), .out(xored));
	//HammingWeight hw (.in(xored), .weight(cnt));
	assign equal = (S_in == S_out);
endmodule


// option 1
module LFSR #(parameter n = 8) ( // may need to change according to our implementation
    input wire clk,
    input wire rst,
    output reg [n-1:0] lfsr_out
);
    always @(posedge clk or posedge rst) begin
        if (rst)
            lfsr_out <= 1;
        else
            lfsr_out <= {lfsr_out[n-2:0], lfsr_out[n-1] ^ lfsr_out[n-2]};
    end
endmodule

//option 2
module LFSR_seeded #(parameter n = 8) (
    input wire clk,
    input wire rst,
    input wire load,
    input wire [n-1:0] seed,
    output reg [n-1:0] lfsr_out
);
    always @(posedge clk or posedge rst) begin
        if (rst)
            lfsr_out <= seed; // Set LFSR to seed value on reset
        else if (load)
            lfsr_out <= seed; // Allow manual loading of a seed value
        else
            lfsr_out <= {lfsr_out[n-2:0], lfsr_out[n-1] ^ lfsr_out[n-2]};
    end
endmodule


module Input_Data_Generator #(parameter k = 32) (
    input wire clk,
    input wire rst,
    input wire en,
    input wire [1:0] ctrl,
    output reg [k-1:0] S_data
);
    
    reg [k-1:0] counter;
    wire [k-1:0] lfsr_out;
    
    LFSR #(k) lfsr_gen (.clk(clk), st(rst), .lfsr.r_out(lfsr_out));
    
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            S_data <= 0;
            counter <= 0;
        end else if (en) begin
            case (ctrl)
                2'b00: begin // Sequential
                    S_data <= counter;
                    counter <= counter + 1;
                end
                2'b10: begin // Random LFSR
                    S_data <= lfsr_out;
                end
                2'b11: begin // Custom sequence (e.g., reverse binary)
                    S_data <= ~counter;
                    counter <= counter + 1;
                end
            endcase
        end
    end
endmodule



module DataPath #(parameter M = 5, k = 32, A = 8)(
    input wire clk,
    input wire rst,
    input wire en_gen_data, en_gen_err, en_enc, en_bus, en_dec,en_trans_count,en_bf1,en_bf2, en_k_comp,
	//input wire load_seed,
	//input wire [s-1:0] seed_err,
    input wire [k-1:0] S_in,
	input wire [1:0] ctrl_input, ctrl_err,
    //output wire [k-1:0] S_out
	output wire [$clog2(k+1)-1:0] cnt,
	output wire isequal
);
    wire [k-1:0] X, X_noc, enc_mux_out, kcomp_mux_out;
	wire [n-1:0] bus_mux_out, dec_mux_out;
    wire [M-1:0] INV, INV_noc;
	wire [k-1:0] S_data,S_data_buf1,S_data_buf2;
	wire ctrl;
	wire [k-1:0] k_zero_input = {k{1'b0}};
	wire [n-1:0] n_zero_input = {n{1'b0}};
	

    Input_Data_Generator #(k) data_gen( 
        .clk(clk), .rst(rst), .en(en_gen_data), .ctrl(ctrl_input),
        .S_data(S_data)
    );

	
	//Input_Data_Generator_seeded (n = 8) err_gen ( 
    //    .clk(clk), .rst(rst), .en(en_gen_err),
    //    .ctrl(ctrl_err), .load_seed(load_seed), .seed(seed_err), .Error(error)
    //);

    
	
	MUX2x1 #(k) enc_mux (
                .sel(en_enc and ~rst),
                .a(k_zero_input), //or input from words memory
                .b(S_data),
                .out(enc_mux_out)
            );
		.
    Encoder enc (
        .clk(clk), .S(enc_mux_out), .X(X), .INV(INV)
    );

	//BitwiseXOR bxor (.a({X,INV}), .b(error), .out({X_noc,INV_noc}));  // for errors
    MUX2x1 #(n) bus_mux (
                .sel(en_bus and ~rst),
                .a(n_zero_input), //or input from words memory
                .b({X, INV}),
                .out(bus_mux_out)
            );
			
	MUX2x1 #(n) dec_mux (
                .sel(en_dec and ~rst),
                .a(n_zero_input), //or input from words memory
                .b(bus_mux_out),
                .out(dec_mux_out)
            );
	
	Decoder dec (
        .X(dec_mux_out[n-1:M), .INV(dec_mux_out[M-1:0),
        .S_out(S_out)
    );
	
	MUX2x1 #(n) kcomp_mux (
                .sel(en_kcomp and ~rst),
                .a(enc_mux_out), //or input from words memory
                .b(dec_mux_out),
                .out(kcomp_mux_out)
            );

    Transition_Counter trans_cnt ( // for 2 consecutive words
        .clk(clk), .rst(rst), .en(en_trans_count),
        .data_in(bus_mux_out), .transition_count(cnt)
    );


    Buffer buf1 (.clk(clk), .rst(rst), .en(en_bf1), .in(S_data), .out(S_data_buf1));
    Buffer buf2 (.clk(clk), .rst(rst), .en(en_bf2), .in(S_data_buf1), .out(S_data_buf2));

    K_Comparator k_comp (
        .clk(clk), .S_in(S_data_buf2), .S_out(kcomp_mux_out), .equal(isequal)
    );

endmodule



/* Currently unused
module HammingWeight #(parameter k = 8) ( 
    input wire [k-1:0] in,
    output reg [$clog2(k+1)-1:0] weight
);
    integer i;
    always @(*) begin
        weight = 0;
        for (i = 0; i < k; i = i + 1) begin
            weight = weight + in[i];
        end
    end
endmodule


module Input_Data_Generator_seeded #(parameter n = 8) ( //to be used as Error_Generator
    input wire clk,
    input wire rst,
    input wire en,
    input wire [1:0] ctrl,
    input wire load_seed,
    input wire [n-1:0] seed,
    output reg [n-1:0] S_data
);
    
    reg [n-1:0] counter;
    wire [n-1:0] gray_code;
    wire [n-1:0] lfsr_out;
    
    GrayCounter #(n) gray_gen (.clk(clk), .rst(rst), .gray_out(gray_code));
    LFSR #(n) lfsr_gen (.clk(clk), .rst(rst), .load(load_seed), .seed(seed), .lfsr_out(lfsr_out));
    
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            S_data <= 0;
            counter <= 0;
        end else if (en) begin
            case (ctrl)
                2'b00: begin // Sequential
                    S_data <= counter;
                    counter <= counter + 1;
                end
                2'b01: begin // Gray code sequence
                    S_data <= gray_code;
                end
                2'b10: begin // Random LFSR
                    S_data <= lfsr_out;
                end
                2'b11: begin // Custom sequence (e.g., reverse binary)
                    S_data <= ~counter;
                    counter <= counter + 1;
                end
            endcase
        end
    end
endmodule
*/