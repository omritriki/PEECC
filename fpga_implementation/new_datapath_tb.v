`timescale 1ns/1ps

module datapath_tb;

    // DUT signals
    reg         clk;
    reg         rst_n;
    reg  [31:0] info_in;
    wire [31:0] decoded_out;
    wire        match;

    // Instantiate DUT
    top_module dut (
        .clk(clk),
        .rst_n(rst_n),
        .info_in(info_in),
        .decoded_out(decoded_out),
        .match(match)
    );

    // 100 MHz clock
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    // Helper: apply one vector with a reset pulse to ensure valid codeword
    task apply_and_check(input [31:0] vec);
        begin
            // Reset to clear syndrome/v_prev state so current v is valid
            rst_n   = 1'b0;
            info_in = vec;
            @(posedge clk);
            rst_n   = 1'b1;

            // Allow a couple of cycles for pipeline (syndrome reg + v_prev reg)
            @(posedge clk);
            @(posedge clk);

            if (match) begin
                $display("[%0t] PASS: info_in=0x%08h decoded_out=0x%08h", $time, info_in, decoded_out);
            end else begin
                $display("[%0t] FAIL: info_in=0x%08h decoded_out=0x%08h", $time, info_in, decoded_out);
            end
        end
    endtask

    // Stimulus
    initial begin
        // Init
        rst_n   = 1'b0;
        info_in = 32'h0;
        repeat (2) @(posedge clk);
        rst_n   = 1'b1;
        @(posedge clk);

        // A few fixed vectors
        apply_and_check(32'h00000000);
        apply_and_check(32'hFFFFFFFF);
        apply_and_check(32'hA5A5A5A5);
        apply_and_check(32'h5A5A5A5A);
        apply_and_check(32'h12345678);
        apply_and_check(32'hDEADBEEF);

        // A few random vectors
        repeat (5) begin
            apply_and_check($urandom);
        end

        $display("Testbench completed.");
        $finish;
    end

endmodule