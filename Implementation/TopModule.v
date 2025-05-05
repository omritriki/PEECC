/*
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
*/

module TopModule #(parameter M=5, k=32, A=8)(
    input  wire        CLK,
    input  wire        RST,
    input  wire        ValidIn,
    //output wire [10:0] registers [0:18], // Example for 19-element array, each 11 bits
    output wire [(11*((k+M)/2))-1:0] registers,
    output wire        IsEqual
);

    // Internal signals
    wire trigger;
    wire en_gen_data;
    wire en_gen_err;
    wire en_enc;
    wire en_bus;
    wire en_dec;
    wire en_trans_count;
    wire en_bf1;
    wire en_bf2;
    wire en_k_comp;
    wire done;

    //----------------------------------------------
    // FSM_controller instantiation
    //----------------------------------------------
    FSM_controller U1 (
        .clk             (CLK),
        .reset           (RST),
        .valid_in        (ValidIn),
        .en_gen_data     (en_gen_data),
        .en_gen_err      (en_gen_err),
        .en_enc          (en_enc),
        .en_bus          (en_bus),
        .en_dec          (en_dec),
        .en_trans_count  (en_trans_count),
        .en_bf1          (en_bf1),
        .en_bf2          (en_bf2),
        .en_k_comp       (en_k_comp),
        .trigger         (trigger),
        .done            (done)
    );

    //----------------------------------------------
    // DataPath instantiation
    //----------------------------------------------
    DataPath #(
        .M(M), //5
        .k(k), //32
        .A(A) //8
    ) U2 (
        .clk            (CLK),
        .rst            (RST),
        .done           (done),
        .en_gen_data    (en_gen_data),
        .en_gen_err     (en_gen_err),
        .en_enc         (en_enc),
        .en_bus         (en_bus),
        .en_dec         (en_dec),
        .en_trans_count (en_trans_count),
        .en_bf1         (en_bf1),
        .en_bf2         (en_bf2),
        .en_k_comp      (en_k_comp),
        .registers      (registers),
        .isequal        (IsEqual)
    );

endmodule