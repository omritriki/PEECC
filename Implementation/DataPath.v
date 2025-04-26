// If we decide buffer doesn't need an enable signal, we can remove it from the module and
// remove it from check_invert modules

module MUX2x1 #(parameter A = 8)(
    input wire sel,
    input wire [A-1:0] a,
    input wire [A-1:0] b,
    output wire [A-1:0] out
);
    assign out = sel ? b : a;
    always @(*) begin
	$monitor("mux2x1: ", $time, out);
    end
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


module FourCycleDelay #(parameter k = 32)(
    input wire clk,
    input wire rst,
    input wire [k-1:0] data_in,
    output reg [k-1:0] data_out
);
    reg [k-1:0] buf0, buf1, buf2, buf3;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            buf0 <= 0;
            buf1 <= 0;
            buf2 <= 0;
            buf3 <= 0;
        end 
        else begin
            buf3 <= buf2;
            buf2 <= buf1;
            buf1 <= buf0;
            buf0 <= data_in;
            data_out <= buf3;
        end
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
    input wire [A-1:0] S_i,  //7
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
            wire [A-2:0] S_part1 = S[i*(A-1) +: (A-1)];
            wire [A-2:0] X_part1;
            CheckInvert #(A-1) ci1 (
                .clk(clk), .rst(rst), .en(en),
                .S_i(S_part1),
                .X_i(X_part1),  // X_part1 is assigned here
                .INV_i(INV[i])
            );
            assign X[i*(A-1) +: (A-1)] = X_part1;  // X_part1 is assigned to part-select of X
        end
    endgenerate
    
    genvar j; //k=32, M=5, A=8
    generate
        for (j = 0; j < (M - ((k + M) % M)); j = j + 1) begin : check_invert_gen2
	    localparam integer start = ((k+M)%M)*(A-1) + j*(A-2);
	    initial begin
	        $display("start: ", start);
	    end
            wire [A-3:0] S_part2 = S[start +: (A-2)];
            wire [A-3:0] X_part2;
            CheckInvert #(A-2) ci2(
                .clk(clk), .rst(rst), .en(en),
                .S_i(S_part2),
                .X_i(X_part2),  // X_part2 is assigned here
                .INV_i(INV[((k+M)%M)+j])
            );
            assign X[start +: (A-2)] = X_part2;  // X_part2 is assigned to part-select of X
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
            wire [A:0] mux_out1;
            MUX2x1 #(A+1) mux_inst1 (
                .sel(INV[i]),
                .a(X[i*(A+1) +: (A+1)]),
                .b(~X[i*(A+1) +: (A+1)]),
                .out(mux_out1)
            );
            assign S_out[i*(A+1) +: (A+1)] = mux_out1;
        end
    endgenerate
    
    genvar j;
    generate
        for (j = (k + M) % M; j < M-1; j = j + 1) begin : mux_gen2
            wire [A-1:0] mux_out2;
            MUX2x1 #(A) mux_inst2 (
                .sel(INV[j]),
                .a(X[j*(A) +: (A)]),
                .b(~X[j*(A) +: (A)]),
                .out(mux_out2)
            );
            assign S_out[j*A +: A] = mux_out2;
        end
    endgenerate
endmodule


module Transition_Counter #(parameter n = 37) (
    input wire clk,
    input wire rst,
    input wire en,
    input wire done,
    input wire [n-1:0] data_in,
    output reg [11*(n/2)-1:0] registers
);

    reg [n-1:0] prev_data;
    reg [n-1:0] xor_result;
    reg [10:0] registers_cnt [(n/2):0]; 
    
    integer i, j, transition_count;

    initial begin
        for (i = 0; i <= (n/2); i = i + 1) begin //the limit was changed from 11*(n/2)-1
            registers_cnt[i] = 11'b0;
        end
    end
    
    
     
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            prev_data <= {n{1'b0}};
            // Reset all counters
            for (i = 0; i <= (n/2); i = i + 1) begin    //I added this in the rst. not tested but it seems more right
                registers[i] <= 11'b0; 
            end
	    registers <= 0;  //change the reset assignment from a for loop to just assigning 0
        end 
	else if (en) begin
	    xor_result = data_in ^ prev_data;
            transition_count = 0;
            // Count the number of transitions
            for (i = 0; i < n; i = i + 1) begin
                transition_count = transition_count + xor_result[i];
            end
	    prev_data <= data_in;
            // Increment the corresponding register0
            registers_cnt[transition_count] <= registers_cnt[transition_count] + 1;            
        end
        // Store the final count in the output register after 2000 cycles
        if (done) begin
            for (j = 0; j <= (n/2); j = j + 1) begin  ////the limit was changed from 11*(n/2)-1
                registers[j*11 +: 11] <= registers_cnt[j]; //registers is not an array but a bit vector so I needed to change from registers[j] to registers[j*11 +: 11]
            end
        end
    end
endmodule


module K_Comparator #(parameter k = 32)(
    input wire clk,
    input wire [k-1:0] S_in,
    input wire [k-1:0] S_out,
	output wire isequal
);
	//wire [k-1:0] xored;
	//BitwiseXOR bxor (.a(S_out), .b(S_in), .out(xored));
	//HammingWeight hw (.in(xored), .weight(cnt));
	assign isequal = (S_in == S_out);
endmodule


// Check double loading of seed
module LFSR_seeded #(parameter k = 32) (
    input wire clk,
    input wire rst,
    input wire load,
    input wire [k-1:0] seed,
    output reg [k-1:0] lfsr_out
);
    reg load_d = 0; 

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            lfsr_out <= seed; 
            load_d <= 0;
        end 
        else begin
            load_d <= load; 
            if (load && !load_d) begin
                lfsr_out <= seed; // Rising edge detected
            end 
            else begin
                lfsr_out <= {lfsr_out[k-2:0], lfsr_out[k-1] ^ lfsr_out[k-2]};
            end
        end
    end
endmodule


// add seed and load
module Input_Data_Generator #(parameter k = 32) (
    input wire clk,
    input wire rst,
    input wire en,
    output reg [k-1:0] S_data
);
    wire [k-1:0] lfsr_out;

    // k is currently constatnt
    wire [31:0] seed = 32'b11000000000000000000000000000001;
    LFSR_seeded #(k) lfsr_gen (.clk(clk), .rst(rst), .load(en), .seed(seed), .lfsr_out(lfsr_out));
    
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            S_data <= 0;
        end 
        else if (en) begin
            S_data <= lfsr_out;
        end
    end
endmodule


module DataPath #(parameter M = 5, k = 32, A = 8)(
    input wire clk,
    input wire rst,
    input wire done, 
    input wire en_gen_data, en_gen_err, en_enc, en_bus, en_dec, en_trans_count, en_bf1, en_bf2, en_k_comp,
    output wire isequal,
    output reg [11*((k+M)/2)-1:0] registers
);
    wire [k-1:0] X, enc_mux_out, kcomp_mux_out;
    wire [(k+M)-1:0] bus_mux_out, dec_mux_out;
    wire [M-1:0] INV;
    wire [k-1:0] S_data, S_data_2cmp, S_out;
    wire [k-1:0] k_zero_input = {k{1'b0}};
    wire [(k+M)-1:0] n_zero_input = {(k+M){1'b0}};

    Input_Data_Generator #(k) data_gen( 
        .clk(clk), .rst(rst), .en(en_gen_data), .S_data(S_data)
    );

    MUX2x1 #(k) enc_mux (
        .sel(en_enc & ~rst),
        .a(k_zero_input), 
        .b(S_data),
        .out(enc_mux_out)
    );
        
    Encoder enc (
        .clk(clk), .rst(rst), .en(en_enc), .S(enc_mux_out), .X(X), .INV(INV)
    );

    MUX2x1 #(k+M) bus_mux (
        .sel(en_bus & ~rst),
        .a(n_zero_input), 
        .b({X, INV}),
        .out(bus_mux_out)
    );
            
    MUX2x1 #(k+M) dec_mux (
        .sel(en_dec & ~rst),
        .a(n_zero_input), 
        .b(bus_mux_out),
        .out(dec_mux_out)
    );
    
    Decoder dec (
        .X(dec_mux_out[(k+M)-1:M]), .INV(dec_mux_out[M-1:0]),
        .S_out(S_out)
    );
    
    MUX2x1 #(k) kcomp_mux (
        .sel(en_k_comp & ~rst),
        .a(S_data_2cmp),  
        .b(S_out),
        .out(kcomp_mux_out)
    );

    wire [11*((k+M)/2)-1:0] trans_cnt_registers;

    Transition_Counter #(k+M) trans_cnt ( 
        .clk(clk), .rst(rst), .en(en_trans_count), .done(done),
        .data_in(bus_mux_out), .registers(trans_cnt_registers)
    );

    //assign registers = trans_cnt_registers;
    
    FourCycleDelay fcd (
        .clk(clk), .rst(rst), .data_in(enc_mux_out), .data_out(S_data_2cmp)
    );

    K_Comparator k_comp (
        .clk(clk), .S_in(S_data_2cmp), .S_out(kcomp_mux_out), .isequal(isequal)
    );
	 
	 always @(*) begin
		registers = trans_cnt_registers;
	 end
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