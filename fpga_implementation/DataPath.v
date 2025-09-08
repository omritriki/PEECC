/*
======================================================
   Power Efficient Error Correction Encoding for
           On-Chip Interconnection Links

           Shlomit Lenefsky & Omri Triki
                   06.2025
======================================================
*/

module my_mux2x1 #(parameter A = 8)(
    input wire sel,
    input wire [A-1:0] a,
    input wire [A-1:0] b,
    output wire [A-1:0] out
);
    assign out = sel ? b : a;
endmodule


module my_buffer #(parameter A = 1)(  
    input wire clk, rst_n, en,
    input wire [A-1:0] in,
    output reg [A-1:0] out
);
    always @(posedge clk or negedge rst_n) begin
        if (~rst_n)
            out <= 0;
        else if (en)
            out <= in;
    end
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


(* S = "TRUE"*) (* dont_touch = "TRUE" *)
module my_transition_counter #(parameter n = 37) (
    input wire clk, rst_n, en, done,
    input wire [n-1:0] data_in,
    output reg  [4:0] reg_num,
    output reg  [21:0] sum_value
);
    reg [n-1:0] prev_data;
    reg [n-1:0] xor_result;
    reg [10:0] registers_cnt [(n/2):0];
	reg [10:0] temp_max;
	reg [21:0] temp_sum;
	reg [4:0] temp_reg;	 

    integer i, j, transition_count;
    
	always @(posedge clk or negedge rst_n) begin
		if (~rst_n) begin
            prev_data = 0;
            xor_result = 0;
            reg_num = 0;
            sum_value = 0;
            for (i = 0; i <= (n/2); i = i + 1) begin
                registers_cnt[i] = 11'b0;
            end
        end 
        else begin
            if (en) begin
                xor_result = data_in ^ prev_data;
                transition_count = 0;  
                for (i = 0; i < n; i = i + 1) begin
                    transition_count = transition_count + xor_result[i];
                end
                prev_data = data_in;
                registers_cnt[transition_count] = registers_cnt[transition_count] + 1'b1;
            end

            if (done) begin
                temp_max = 0;
                temp_sum = 0;
                temp_reg = reg_num;
					
                for (j = 0; j <= (n/2); j = j + 1) begin
                    if (registers_cnt[j] > temp_max) begin
                        temp_max = registers_cnt[j];
                        temp_reg = j;
                    end
                    $display("register %d: %h", j, registers_cnt[j]);
                    temp_sum = temp_sum + (registers_cnt[j] * j);
                end
                reg_num = temp_reg;
                sum_value = temp_sum;
            end
        end
	end
endmodule


module lfsr_14bit (
    input  wire clk, rst_n,
    input  wire [13:0] seed,       
    output wire msb_out
);
    reg [13:0] lfsr_reg;
    reg feedback;
 
    always @(posedge clk or negedge rst_n) begin
        if (~rst_n) begin 
            lfsr_reg <= seed;
            feedback <= 1'b0;
        end
        else begin
            feedback <= lfsr_reg[13] ^ lfsr_reg[4] ^ lfsr_reg[3] ^ lfsr_reg[1] ^ lfsr_reg[0];
            lfsr_reg <= {lfsr_reg[12:0], feedback};
        end
    end
    assign msb_out = lfsr_reg[0];
endmodule


module input_data_generator #(parameter k = 32)(
    input wire clk, rst_n, en,
    output reg [k-1:0] S_data
);
    wire [k-1:0] lfsr_out;

    genvar j;
    generate
        for (j = 0; j < k; j = j + 1) begin: Gen_lfsrs
            lfsr_14bit lfsr (
                .clk(clk),
                .rst_n(rst_n),
                .seed(14'b11000000000001 ^ j[13:0]),
                .msb_out(lfsr_out[j])
            );
        end
    endgenerate

    always @(posedge clk or negedge rst_n) begin
        if (~rst_n) begin
            S_data <= 0;
        end
        else begin 
            if (en) begin
                S_data <= lfsr_out;
            end
        end
    end
endmodule


module my_fcd #(parameter k = 32)(
    input wire clk, rst_n,
    input wire [k-1:0] data_in,
    output reg [k-1:0] data_out
);
    reg [k-1:0] buf0, buf1, buf2;

    always @(posedge clk or negedge rst_n) begin
        if (~rst_n) begin
            buf0 <= 0;
            buf1 <= 0;
            buf2 <= 0;
            data_out <= 0;
        end 
        else begin
            buf2 <= buf1;
            buf1 <= buf0;
            buf0 <= data_in;
            data_out <= buf2;
        end
    end
endmodule


module my_k_comparator #(parameter k = 32)(
    input wire [k-1:0] S_in,
    input wire [k-1:0] S_out,
	output wire isequal
);
	assign isequal = (S_in == S_out);
endmodule


module DataPath #(parameter M = 5, k = 32, A = 8)(
    input wire clk, rst_n, done,
    input wire en_gen_data, en_enc, en_bus, en_dec, en_trans_count, en_k_comp,
    output wire isequal,
	output wire [4:0] max_reg,
    output wire [21:0] sum_transitions
);
    wire [k-1:0] X, enc_mux_out, kcomp_mux_out, enc_reg_out, kcomp_reg_out;
    wire [(k+M)-1:0] bus_reg_out, bus_mux_out, dec_reg_out, dec_mux_out;
    wire [M-1:0] INV1;
    wire [k-1:0] S_data, S_data_2cmp, S_out;
    wire [k-1:0] k_zero_input = {k{1'b0}};
    wire [(k+M)-1:0] n_zero_input = {(k+M){1'b0}};

    input_data_generator #(k) data_gen( 
        .clk(clk), 
        .rst_n(rst_n), 
        .en(en_gen_data), 
        .S_data(S_data)
    );

    my_mux2x1 #(k) enc_mux (
        .sel(en_enc),
        .a(k_zero_input), 
        .b(S_data),
        .out(enc_mux_out)
    );

    my_buffer #(k) enc_reg (
        .clk(clk), 
        .rst_n(rst_n), 
        .en(en_enc), 
        .in(enc_mux_out), 
        .out(enc_reg_out)
    );
        
    my_encoder #(M, k, A) enc (
        .clk(clk), 
        .rst_n(rst_n), 
        .en(en_enc), 
        .S(enc_reg_out), 
        .X(X), 
        .INV1(INV1)
    );

    my_buffer #(k+M) bus_reg (
		.clk(clk), 
        .rst_n(rst_n), 
        .en(en_bus), 
        .in({X, INV1}), 
        .out(bus_reg_out)
    );

    my_mux2x1 #(k+M) bus_mux (
        .sel(en_bus),
        .a(n_zero_input), 
        .b(bus_reg_out),
        .out(bus_mux_out)
    );
            
    my_mux2x1 #(k+M) dec_mux (
        .sel(en_dec),
        .a(n_zero_input), 
        .b(bus_mux_out),
        .out(dec_mux_out)
    );

    my_buffer #(k+M) dec_reg (
	    .clk(clk), 
        .rst_n(rst_n), 
        .en(en_dec), 
        .in(dec_mux_out), 
        .out(dec_reg_out)
    );
    
    my_decoder #(M, k, A) dec(
        .X(dec_reg_out[(k+M)-1:M]), 
        .INV1(dec_reg_out[M-1:0]),
        .S_out(S_out)
    );

    my_buffer #(k) kcomp_reg (
	    .clk(clk), 
        .rst_n(rst_n), 
        .en(en_k_comp), 
        .in(S_out), 
        .out(kcomp_reg_out)
    );
    
    my_mux2x1 #(k) kcomp_mux (
        .sel(en_k_comp),
        .a(S_data_2cmp),  
        .b(kcomp_reg_out),
        .out(kcomp_mux_out)
    );

    my_transition_counter #(k+M) trans_cnt ( 
        .clk(clk), 
        .rst_n(rst_n), 
        .en(en_trans_count), 
        .done(done),
        .data_in(bus_mux_out), 
        .reg_num(max_reg), 
        .sum_value(sum_transitions)
    );

    my_fcd #(k) fcd (
        .clk(clk), 
        .rst_n(rst_n), 
        .data_in(enc_mux_out), 
        .data_out(S_data_2cmp)
    );

    my_k_comparator #(k) k_comp (
        .S_in(S_data_2cmp), 
        .S_out(kcomp_mux_out), 
        .isequal(isequal)
    );

endmodule