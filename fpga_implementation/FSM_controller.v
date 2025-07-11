 /*
======================================================
   Power Efficient Error Correction Encoding for
           On-Chip Interconnection Links

           Shlomit Lenefsky & Omri Triki
                   06.2025
======================================================
*/

module FSM_controller (
    input  wire         clk,
    input  wire         rst_n,
    input  wire         valid_in,
    input  wire         txFinish,
    output reg          en_gen_data,
    //output reg          en_gen_err,     // disabled for now
    output reg          en_enc,
    output reg          en_bus,
    output reg          en_dec,
    output reg          en_trans_count,
    output reg          en_k_comp,
    output reg          trigger,
    output reg          done,
    output reg         start_tx
);

    // State declarations
    localparam [2:0] IDLE = 3'd0;
    localparam [2:0] S0   = 3'd1;
    localparam [2:0] S1   = 3'd2;
    localparam [2:0] S2   = 3'd3;
    localparam [2:0] S3   = 3'd4;
    localparam [2:0] S4   = 3'd5;
    localparam [2:0] S5   = 3'd6;

    (* S = "TRUE"*) (* dont_touch = "TRUE" *) reg [2:0] state, nextstate;

    // Counter signals
    reg  enable_cnt, enable_cnt_next;
    reg  done_cnt;
    reg [10:0] cnt;

    always @(posedge clk) begin ////////
	// Synchronous state register
        if (~rst_n) begin
            state       <= IDLE;
            enable_cnt  <= 1'b0;
            cnt         <= 11'b1;
            done_cnt    <= 1'b0;
            trigger     <= 1'b0;
				done        <= 1'b0;
				start_tx    <= 1'b0;
        end
        else begin
            state <= nextstate;
				enable_cnt <= enable_cnt_next;
				// Pulse start_tx only on S5 entry
            if (state != S5 && nextstate == S5) begin
                start_tx <= 1'b1;
					 done <= 1'b1;
				end
            else begin
                start_tx <= 1'b0;
					 done <= 1'b0;
            end

				// Counter
				if (enable_cnt) begin
					if (cnt == 11'd0) begin
						done_cnt <= 1'b1;
					end
					else begin
						done_cnt <= 1'b0;
					end

					cnt <= cnt + 1'b1;

					// If (cnt > 0) and (cnt < 4) => set trigger
					// Check cnt next-state to see if it is > 0 and < 4
					// so we use the current value of cnt before increment
					if ((cnt > 0) && (cnt < 4)) begin
						trigger <= 1'b1;
					end
					else begin
						trigger <= 1'b0;
					end
				end
				else begin
					cnt      <= 11'd1;
					done_cnt <= 1'b0;
					trigger  <= 1'b0;
				end
		  end
    end
 
    // Next-state logic
    always @(*) begin
        // Default assignments
        nextstate   = state;
		  enable_cnt_next = enable_cnt;

        case (state)
            IDLE: begin
                if (valid_in == 1'b1) begin
                    nextstate  = S4; ///////////////////////////return to state s0
                    enable_cnt_next = 1'b1;
						  //start_tx = 1'b0;
                end
            end

            S0: begin
                if (done_cnt == 1'b1) begin
                    nextstate = S1;
                end
            end

            S1: begin
                if (done_cnt == 1'b1) begin
                    nextstate = S2;
                end
            end

            S2: begin
                if (done_cnt == 1'b1) begin
                    nextstate = S3;
                end
            end

            S3: begin
                if (done_cnt == 1'b1) begin
                    nextstate = S4;
                end
            end

            S4: begin
                if (done_cnt == 1'b1) begin
                    nextstate = S5;
						  //done = 1'b1;
						  enable_cnt_next = 1'b0;
                end
            end

	    S5: begin
                if (txFinish == 1'b1) begin
                    nextstate = IDLE;
                end
            end

            default: begin
                nextstate  = IDLE;
            end
        endcase
    end

    // State output logic
    always @(*) begin
        // Default outputs
        en_gen_data    = 1'b0;
        //en_gen_err     = 1'b0;  // disabled for now
        en_enc         = 1'b0;
        en_bus         = 1'b0;
        en_dec         = 1'b0;
        en_trans_count = 1'b0;
        //done           = 1'b0;
        en_k_comp      = 1'b0;

        case (state)
            IDLE: begin
                // All signals 0
            end

            S0: begin
                en_gen_data = 1'b1;
            end

            S1: begin
                en_gen_data = 1'b1;
                en_enc      = 1'b1;
            end

            S2: begin
                en_gen_data = 1'b1;
                en_enc      = 1'b1;
                en_bus      = 1'b1;
            end

            S3: begin
                en_gen_data = 1'b1;
                en_enc      = 1'b1;
                en_bus      = 1'b1;
                en_dec      = 1'b1;
            end

            S4: begin
                en_gen_data    = 1'b1;
                en_enc         = 1'b1;
                en_bus         = 1'b1;
                en_dec         = 1'b1;
                en_trans_count = 1'b1;
                en_k_comp      = 1'b1;
            end

	    S5: begin
	    end

            default: begin
                // Everything stays 0
            end
        endcase
    end

endmodule
