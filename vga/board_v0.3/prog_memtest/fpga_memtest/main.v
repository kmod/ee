`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    01:54:56 04/07/2014 
// Design Name: 
// Module Name:    main 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module main(
    input wire input_clk

    , output wire [2:0] leds

    , inout wire [2:0] mb_a
    , inout wire [3:0] mb_b
    , inout wire [3:2] mb_c
    , inout wire [3:2] mb_d

    ,
   inout  [15:0]                                    mcb1_dram_dq,
   output [12:0]                                    mcb1_dram_a,
   output [1:0]                                     mcb1_dram_ba,
   output                                           mcb1_dram_cke,
   output                                           mcb1_dram_ras_n,
   output                                           mcb1_dram_cas_n,
   output                                           mcb1_dram_we_n,
   output                                           mcb1_dram_dm,
   inout                                            mcb1_dram_udqs,
   inout                                            mcb1_rzq,
   output                                           mcb1_dram_udm,
   inout                                            mcb1_dram_dqs,
   output                                           mcb1_dram_ck,
   output                                           mcb1_dram_ck_n,

   inout  [15:0]                                    mcb3_dram_dq,
   output [12:0]                                    mcb3_dram_a,
   output [2:0]                                     mcb3_dram_ba,
   output                                           mcb3_dram_ras_n,
   output                                           mcb3_dram_cas_n,
   output                                           mcb3_dram_we_n,
   output                                           mcb3_dram_odt,
   output                                           mcb3_dram_reset_n,
   output                                           mcb3_dram_cke,
   output                                           mcb3_dram_dm,
   inout                                            mcb3_dram_udqs,
   inout                                            mcb3_dram_udqs_n,
   inout                                            mcb3_rzq,
   inout                                            mcb3_zio,
   output                                           mcb3_dram_udm,
   inout                                            mcb3_dram_dqs,
   inout                                            mcb3_dram_dqs_n,
   output                                           mcb3_dram_ck,
   output                                           mcb3_dram_ck_n
    );

    // Aliases:
    wire spi_mosi;
    wire spi_miso;
    wire spi_clk;
    wire spi_ss;
    wire jtag_ledf;
    assign spi_mosi = mb_a[0];
    assign mb_a[1] = spi_miso;
    assign spi_clk = mb_a[2];
    assign spi_ss = mb_b[0];
    assign mb_b[1] = jtag_ledf;


    assign jtag_ledf = !spi_ss;


    wire c1_calib_done;
    wire c3_calib_done;

    wire clk1;
    wire clk3;
    wire input_clk_bufg;
    //IBUFG clkin1_buf (.O (input_clk_bufg), .I (input_clk));

    dcm #(.M(3), .D(2), .INPUT_BUFFER(0), .OUTPUT_BUFFER(0)) dcm1(.CLK_IN(input_clk), .CLK_OUT(clk1));
    dcm #(.M(9), .D(2), .INPUT_BUFFER(0), .OUTPUT_BUFFER(0)) dcm3(.CLK_IN(input_clk), .CLK_OUT(clk3));
    mem mem(.c1_sys_clk(clk1), .c3_sys_clk(clk3), .c1_calib_done(c1_calib_done), .c3_calib_done(c3_calib_done),
        .mcb1_dram_dq(mcb1_dram_dq),
        .mcb1_dram_a(mcb1_dram_a),
        .mcb1_dram_ba(mcb1_dram_ba),
        .mcb1_dram_cke(mcb1_dram_cke),
        .mcb1_dram_ras_n(mcb1_dram_ras_n),
        .mcb1_dram_cas_n(mcb1_dram_cas_n),
        .mcb1_dram_we_n(mcb1_dram_we_n),
        .mcb1_dram_dm(mcb1_dram_dm),
        .mcb1_dram_udqs(mcb1_dram_udqs),
        .mcb1_rzq(mcb1_rzq),
        .mcb1_dram_udm(mcb1_dram_udm),
        .mcb1_dram_dqs(mcb1_dram_dqs),
        .mcb1_dram_ck(mcb1_dram_ck),
        .mcb1_dram_ck_n(mcb1_dram_ck_n),

        .mcb3_dram_dq(mcb3_dram_dq),
        .mcb3_dram_a(mcb3_dram_a),
        .mcb3_dram_ba(mcb3_dram_ba),
        .mcb3_dram_cke(mcb3_dram_cke),
        .mcb3_dram_ras_n(mcb3_dram_ras_n),
        .mcb3_dram_cas_n(mcb3_dram_cas_n),
        .mcb3_dram_we_n(mcb3_dram_we_n),
        .mcb3_dram_odt(mcb3_dram_odt),
        .mcb3_dram_reset_n(mcb3_dram_reset_n),
        .mcb3_dram_dm(mcb3_dram_dm),
        .mcb3_dram_udqs(mcb3_dram_udqs),
        .mcb3_dram_udqs_n(mcb3_dram_udqs_n),
        .mcb3_rzq(mcb3_rzq),
        .mcb3_zio(mcb3_zio),
        .mcb3_dram_udm(mcb3_dram_udm),
        .mcb3_dram_dqs(mcb3_dram_dqs),
        .mcb3_dram_dqs_n(mcb3_dram_dqs_n),
        .mcb3_dram_ck(mcb3_dram_ck),
        .mcb3_dram_ck_n(mcb3_dram_ck_n)
    );


    wire [15:0] write_bits;
    wire [15:0] read_bits;
    spi_controller spi_ctlr(.spi_mosi(spi_mosi), .spi_miso(spi_miso), .spi_clk(spi_clk), .spi_ss(spi_ss), .write_bits(write_bits), .read_bits(read_bits));

    // "register" definitions:
    assign leds[2:0] = ~write_bits[2:0];
    assign read_bits[7:0] = write_bits[7:0];
    assign read_bits[8] = c1_calib_done;
    assign read_bits[9] = c3_calib_done;

endmodule

module spi_controller(
    input wire spi_mosi,
    output reg spi_miso,
    input wire spi_clk,
    input wire spi_ss,

    output reg [15:0] write_bits,
    input wire [15:0] read_bits
    );

    reg [2:0] spi_ctr = 0;
    reg [7:0] spi_in_byte;
    reg [7:0] spi_out_byte = 0;

    localparam IDLE = 0;
    localparam READ = 1;
    localparam WRITE = 2;
    reg [3:0] state = IDLE;

    wire [7:0] new_spi_in_byte;
    assign new_spi_in_byte = {spi_in_byte[6:0], spi_mosi};
    wire [2:0] new_spi_ctr;
    assign new_spi_ctr = spi_ctr + 1'b1;
    always @(posedge spi_clk or posedge spi_ss) begin
        if (spi_ss)
            spi_ctr <= 0;
        else
            spi_ctr <= new_spi_ctr;
    end


    always @(posedge spi_clk) begin
        spi_in_byte <= new_spi_in_byte;

        spi_out_byte <= {spi_out_byte[6:0], 1'b0};
        if (!spi_ss && new_spi_ctr == 0) begin
            case (state)
                IDLE: begin
                    if (new_spi_in_byte == 8'h01)
                        state <= READ;
                    else if (new_spi_in_byte == 8'h02)
                        state <= WRITE;
                end
                READ: begin
                    spi_out_byte <= {7'b0, read_bits[new_spi_in_byte[3:0]]};
                    state <= IDLE;
                end
                WRITE: begin
                    write_bits[new_spi_in_byte[4:1]] <= new_spi_in_byte[0];
                    state <= IDLE;
                end
            endcase
        end
    end

    always @(negedge spi_clk) begin
        spi_miso <= spi_out_byte[7];
    end
endmodule
    
