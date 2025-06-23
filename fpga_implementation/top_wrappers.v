module top_wrapper (
	M_CLK_OSC, //clk
	M_RESET_B, //active low reset
	FTDI_BDBUS_0, //FTDI device bus, need only [0] for rx and [1] for tx
	FTDI_BDBUS_1,
	//M_LED,
	M_HEADER
	
);

	input M_CLK_OSC;
	input M_RESET_B;
	input FTDI_BDBUS_0;
	output FTDI_BDBUS_1;
//	output [9:0] M_LED;
	output M_HEADER;

   localparam k = 32;
   localparam M = 5;

	wire pll_locked;
	wire clk_4mhz_int;

	clk_wiz_v3_6 my_pll (
	.CLK_IN1(M_CLK_OSC),
	.CLK_OUT1(clk_4mhz_int),
	.RESET(~M_RESET_B),
	.LOCKED(pll_locked)
	);

    // Instantiate the TopModule
    TopModule #(.M(M), .k(k), .A(((k+M)/M)+1)) DUT(
        .M_CLK_OSC(clk_4mhz_int),
        .M_RESET_B(M_RESET_B),
        .FTDI_BDBUS_0(FTDI_BDBUS_0), 
        .FTDI_BDBUS_1(FTDI_BDBUS_1),
        .M_HEADER(M_HEADER)
    );


endmodule 