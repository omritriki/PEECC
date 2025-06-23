/*
======================================================
   Power Efficient Error Correction Encoding for
           On-Chip Interconnection Links

           Shlomit Lenefsky & Omri Triki
                   06.2025
======================================================
*/

`timescale 1 ns / 1 ps
module top_wrapper_tb();

    parameter symbol_time = 17361.1;

    // Testbench regs and wires
    reg clk;
    reg rst_n;
    reg rx;
    wire tx;
    wire M_HEADER;	

    // Instantiate the TopModule
    top_wrapper DUT(
        .M_CLK_OSC(clk),
        .M_RESET_B(rst_n),
        .FTDI_BDBUS_0(rx), 
        .FTDI_BDBUS_1(tx),
        .M_HEADER(M_HEADER)
    );

    task send_uart_byte; // TASK THAT RECEIVES A BYTE AND SENDS IT SERIALLY VIA UART
	input [7:0] in_byte;
    begin 
	//$display("sending byte %0h", in_byte);
	repeat (4) @(posedge clk);
	#(symbol_time) rx = 1'b0; // start bit
	#(symbol_time) rx = in_byte[0];
	#(symbol_time) rx = in_byte[1];
	#(symbol_time) rx = in_byte[2];
	#(symbol_time) rx = in_byte[3];
	#(symbol_time) rx = in_byte[4];
	#(symbol_time) rx = in_byte[5];
	#(symbol_time) rx = in_byte[6];
	#(symbol_time) rx = in_byte[7];
	#(symbol_time) rx = 1'b1; // stop bit
	repeat (4) @(posedge clk);
	repeat (40) @(posedge clk);

    end
    endtask

    always #(20.8333/2) clk = ~clk; //48MHZ clock (IF USING PLL)
    //always #125 clk = ~clk;     //4MHZ clock (IF NOT USING PLL)

    initial begin
	clk = 0;
	rst_n = 0;
	rx = 1;
	repeat (4) @(posedge clk);

	rst_n = 1;
	
	send_uart_byte(8'h00);
	send_uart_byte(8'h00);

	repeat (30000) @(posedge clk);

	$stop;


    end
endmodule
