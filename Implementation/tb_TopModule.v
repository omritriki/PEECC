
module tb_TopModule();

    // Testbench regs and wires
    reg clk;
    reg rst;
    reg ValidIn;
    wire [11*18-1:0] registers;
    wire IsEqual;

    // Instantiate the TopModule
    TopModule DUT (
        .CLK(clk),
        .RST(rst),
        .ValidIn(ValidIn), 
        .registers(registers),
        .IsEqual(IsEqual)
    );

    // Generate a clock: 10 ns period => 100 MHz
    // set initial value
    initial begin
        clk = 1'b0;
        ValidIn = 1'b0;  
    end
	 
	 always #5 clk = ~clk;

    // Main stimulus
    initial begin
        // Apply reset
      	#1
        rst = 1'b1;
	#2
	rst = 1'b0;
	#4
	ValidIn = 1'b1;
        #10;
	ValidIn = 1'b0;
         // Let the design run for a while
         #90000;

         // Stop simulation
         $stop;
    end

    // Optional: For debugging or waveforms, you can dump file
    //initial begin
     //   $dumpfile("tb_TopModule.vcd");
     //   $dumpvars;
    //end

endmodule
