/*
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        09.2025
======================================================
*/

// Purpose: Finite State Machine controlling pipeline enables and UART handshakes.
//  - Pulses enables for data generation, encode, bus stage, and decode.
//  - Raises 'done' to snapshot transition stats and trigger UART transmit.


// Drives enable strobes across pipeline stages and orchestrates UART transaction
module fsm_controller (
    input  wire         clk,
    input  wire         rst_n,
    input  wire         valid_in,
    input  wire         txFinish,
    output reg          en_gen_data,
    output reg          en_enc,
    output reg          en_bus,
    output reg          en_dec,
    output reg          en_trans_count,
    output reg          en_k_comp,
    output reg          trigger,
    output reg          done,
    output reg          start_tx,
	output reg          inn_rst_n
);

    localparam [2:0] IDLE = 3'd0;
    localparam [2:0] S0   = 3'd1;
    localparam [2:0] S1   = 3'd2;
    localparam [2:0] S2   = 3'd3;
    localparam [2:0] S3   = 3'd4;
    localparam [2:0] S4   = 3'd5;
    localparam [2:0] S5   = 3'd6;

    reg [2:0] state;
	reg [2:0] prev_state;
	reg [2:0] next_state_reg; 
    reg [10:0] cnt;
    reg [3:0]  state_counter;       // counts S5 cycles to step next_state_reg
	
    always @(posedge clk or negedge rst_n) begin 
        if (~rst_n) begin
            state          <= IDLE;
            prev_state     <= IDLE;
            next_state_reg <= S0; 
            cnt            <= 11'd0;
            trigger        <= 1'b0;
            done           <= 1'b0;
            start_tx       <= 1'b0;
            state_counter  <= 4'd0; 
        end
        else begin
            prev_state <= state;
            start_tx <= 1'b0;
            done     <= 1'b0;
                
            case (state)
                IDLE: begin
                    trigger <= 1'b0;
                    if (valid_in) begin
                        state <= next_state_reg;   
                    end
			end

                S0, S1, S2, S3, S4: begin
                    trigger <= 1'b1;
                    if (cnt == 11'b11111111111) begin
                        cnt   <= 11'd0;
                        state <= S5;              
                    end 
                    else begin
                        cnt <= cnt + 1'b1;
                    end
                end

                S5: begin
                    trigger <= 1'b0;
                    if (prev_state != S5 && state == S5) begin
                        start_tx <= 1'b1;
                        done     <= 1'b1;
                    end
                    if (txFinish) begin
                        if (state_counter == 4'd1) begin
                            state_counter  <= 4'd0;
                            next_state_reg <= next_state_reg + 3'd4;
                        end
                        else begin
                            state_counter <= state_counter + 1'b1;
                        end
                        state <= IDLE;
                    end
                end
            endcase
        end
    end

    always @(*) begin
        // Default outputs
        en_gen_data    <= 1'b0;
        en_enc         <= 1'b0;
        en_bus         <= 1'b0;
        en_dec         <= 1'b0;
        en_trans_count <= 1'b0;
        en_k_comp      <= 1'b0;

        case (state)
            IDLE: begin
                inn_rst_n <= 0;
                if (valid_in == 1) begin
                    inn_rst_n <= 1;
                end
            end

            S0: begin
                en_gen_data <= 1'b1;
            end

            S1: begin
                en_gen_data <= 1'b1;
                en_enc      <= 1'b1;
            end

            S2: begin
                en_gen_data <= 1'b1;
                en_enc      <= 1'b1;
                en_bus      <= 1'b1;
            end

            S3: begin
                en_gen_data <= 1'b1;
                en_enc      <= 1'b1;
                en_bus      <= 1'b1;
                en_dec      <= 1'b1;
            end

            S4: begin
                en_gen_data    <= 1'b1;
                en_enc         <= 1'b1;
                en_bus         <= 1'b1;
                en_dec         <= 1'b1;
                en_trans_count <= 1'b1;
                en_k_comp      <= 1'b1;
            end

            S5: begin
            end

            default: begin
                // Everything stays 0
            end
        endcase
    end
endmodule
