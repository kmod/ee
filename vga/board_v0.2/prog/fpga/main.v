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
    output wire [2:0] leds,
    input wire input_clk,

    inout wire [3:0] mb_a,
    inout wire [3:0] mb_b,
    inout wire [3:0] mb_c,
    inout wire [3:0] mb_d,
    inout wire [3:0] mb_e,

    output reg [4:0] vr,
    output reg [4:0] vg,
    output reg [4:0] vb,
    inout wire vsync,
    inout wire hsync
    );

    reg [31:0] led_ctr;
    always @(posedge pixel_clk) begin
        led_ctr <= led_ctr + 1'b1;
    end
    assign leds = ~led_ctr[26:24];

    wire pixel_clk;
	dcm #(.D(3), .M(5)) dcm(.CLK_IN(input_clk), .CLK_OUT(pixel_clk));

    reg [0:0] ctr;
    reg [14:0] vpos;
    reg [14:0] hpos;

    // http://tinyvga.com/vga-timing/1280x800@60Hz
    assign hsync = (hpos < 1344 || hpos >= 1480); // active low
    assign vsync = !(vpos < 801 || vpos >= 804); // active *high*
    assign blank = (hpos >= 1280 || vpos >= 800); // active high

    always @(posedge pixel_clk) begin
        /*ctr <= ctr + 1;
        if (ctr != 0) begin
            // pass
        end else */if (hpos != 1679) begin
            hpos <= hpos + 1;
        end else begin
            hpos <= 0;
            if (vpos == 827) vpos <= 0;
            else vpos <= vpos + 1;
        end
    end

    always @(*) begin
        if (blank) begin
            vr = 0;
            vg = 0;
            vb = 0;
        end else if (mb_a[0]) begin
            vr = vpos[8:4];
            vb = hpos[8:4];
            vg = 0;
        end else begin
            vr = vpos[8:4];
            vg = hpos[8:4];
            vb = 0;
        end
    end
    //assign vb = {vpos[8:7], hpos[9:7]};
endmodule
