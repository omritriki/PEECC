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

    // Helper: apply one vector and check after proper pipeline delay
    task apply_and_check(input [31:0] vec);
        reg [31:0] expected_data;
        begin
            // Apply the input vector
            info_in = vec;
            expected_data = vec;  // Store what we expect to get back
            
            // Wait for the pipeline to process this data
            // The encoder has 1 pipeline stage, top_module has 1 delay stage
            // So we need to wait 2 cycles for the data to flow through
            @(posedge clk);  // Cycle 1: data enters encoder
            @(posedge clk);  // Cycle 2: data exits encoder, enters decoder
            
            // Check the result
            if (decoded_out == expected_data) begin
                $display("[%0t] PASS: info_in=0x%08h decoded_out=0x%08h", $time, expected_data, decoded_out);
            end else begin
                $display("[%0t] FAIL: info_in=0x%08h decoded_out=0x%08h", $time, expected_data, decoded_out);
            end
        end
    endtask

    // Stimulus
    initial begin
        // Initialize and reset
        rst_n   = 1'b0;
        info_in = 32'h0;
        repeat (3) @(posedge clk);
        rst_n   = 1'b1;
        
        // Wait a few extra cycles for the system to stabilize
        repeat (3) @(posedge clk);

        // Test vectors
        apply_and_check(32'h00000000);
        apply_and_check(32'hFFFFFFFF);
        apply_and_check(32'hA5A5A5A5);
        apply_and_check(32'h5A5A5A5A);
        apply_and_check(32'h12345678);
        apply_and_check(32'hDEADBEEF);

        // A few random vectors
        apply_and_check(32'h12F837E7);
        apply_and_check(32'h8EB74A7C);
        apply_and_check(32'h4682679C);
        apply_and_check(32'h3030BA1C);
        apply_and_check(32'h519AFDE8);

        $display("Testbench completed.");
        $finish;
    end

endmodule