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
    );

    wire spi_mosi;
    wire spi_miso;
    wire spi_clk;
    assign spi_mosi = mb_a[0];
    assign mb_a[1] = spi_miso;
    assign spi_clk = mb_a[2];

    wire jtag_ledf;
    assign mb_b[1] = jtag_ledf;






    assign jtag_ledf = spi_clk;

    /*
    wire spi_clk_ibufg;
    IBUFG  u_ibufg_sys_clk
        (
         .I  (spi_clk),
         .O  (spi_clk_ibufg)
         );
         */

    reg [31:0] led_ctr;
    always @(posedge spi_clk) begin
        led_ctr <= led_ctr + 1'b1;
    end
    assign leds = ~led_ctr[2:0];

endmodule
