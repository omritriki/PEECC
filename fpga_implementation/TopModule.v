/*
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
*/

module TopModule #(parameter M=5, k=32, A=8)(
    input M_CLK_OSC, //clk
    input M_RESET_B, //active low reset
    input FTDI_BDBUS_0, //FTDI device bus, need only [0] for rx and [1] for tx
    output FTDI_BDBUS_1,
    output M_HEADER
    //output wire [(11*((k+M)/2))-1:0] registers, ///////////////////////////////?????????????????????????????????
    //output wire        isequal  /////????????????????
    
);

    // Calculate the number of padding bits needed
    localparam integer PADDING_BITS = ((((11*((k+M)/2))+8-1)/8)*8) - (11*((k+M)/2));

    // Internal signals
    wire en_gen_data;
	 wire isequal;
    //wire en_gen_err;
    wire en_enc;
    wire en_bus;
    wire en_dec;
    wire en_trans_count;
    wire en_k_comp;
    wire done;
    //wire [15:0] data_bus_rx_in; // 128 bits - 16 bytes
    wire [11*((k+M)/2)-1:0] data_bus_tx_out; // 128 bits - 16 bytes
    wire rx_valid_in; // valid input from uart - '1' when data is valid
    wire start_tx; // start transmission signal to uart - '1' when data is ready to be sent
    wire txFinish; // transmission finished signal from uart - '1' when data is sent
    wire txBusy; // end of transmission signal from uart - '1' while data is sent

    //----------------------------------------------
    // UART instantiation
    //----------------------------------------------
    uart_interface #(
    	.bytes_to_receive(2), // 128 bits - 16 bytes /////////////will need to change for our needs
	.bytes_to_transmit(((11*((k+M)/2))+8-1)/8) // 128 bits - 16 bytes /////////////will need to change for our needs
    ) inst_uart_interface(
	.clk(M_CLK_OSC), // clk input
	.reset(~M_RESET_B), // active high reset 
	.ser_in(FTDI_BDBUS_0),  // uart RXD input
	.ser_out(FTDI_BDBUS_1), // uart TXD output
	.bus_SERDES(), // parallel input 16 bytes from uart
	.ciphertext({{(PADDING_BITS-1){1'b0}}, isequal, data_bus_tx_out}), // parallel output 16 bytes to uart
	.valid_in(rx_valid_in), // valid input from uart - '1' when data is valid
	.start_tx(start_tx), // start transmission signal to uart - '1' when data is ready to be sent
	.txFinish(txFinish), // transmission finished signal from uart - '1' when data is sent
	.eot(txBusy) // end of transmission signal from uart - '1' while data is sent 
    );

    //----------------------------------------------
    // FSM_controller instantiation
    //----------------------------------------------
    FSM_controller U1 (
        .clk             (M_CLK_OSC),
        .rst_n           (M_RESET_B),
        .valid_in        (rx_valid_in),
		  .txFinish	       (txFinish),
        .en_gen_data     (en_gen_data),
        //.en_gen_err      (en_gen_err),
        .en_enc          (en_enc),
        .en_bus          (en_bus),
        .en_dec          (en_dec),
        .en_trans_count  (en_trans_count),
        .en_k_comp       (en_k_comp),
        .trigger         (M_HEADER),
        .done            (done),
	.start_tx	 (start_tx)
    );

    //----------------------------------------------
    // DataPath instantiation
    //----------------------------------------------
    DataPath #(
        .M(M), //5
        .k(k), //32
        .A(A) //8
    ) U2 (
        .clk            (M_CLK_OSC),
        .rst_n          (M_RESET_B),
        .done           (done),
        .en_gen_data    (en_gen_data),
        //.en_gen_err     (en_gen_err),
        .en_enc         (en_enc),
        .en_bus         (en_bus),
        .en_dec         (en_dec),
        .en_trans_count (en_trans_count),
        .en_k_comp      (en_k_comp),
        .registers      (data_bus_tx_out),
        .isequal        (isequal)
    );

endmodule