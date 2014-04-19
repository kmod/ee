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

    inout wire [4:0] vr,
    inout wire [4:0] vg,
    inout wire [4:0] vb,
    inout wire vsync,
    inout wire hsync
    );

    reg [31:0] led_ctr;
    always @(posedge input_clk) begin
        led_ctr <= led_ctr + 1'b1;
    end
    assign leds = ~led_ctr[26:24];


    reg [0:0] ctr;
    reg [14:0] vpos;
    reg [14:0] hpos;

    // http://tinyvga.com/vga-timing/640x400@70Hz
    assign hsync = (hpos < 656 || hpos >= 752);
    assign vsync = (vpos < 412 || vpos >= 414);

    always @(posedge input_clk) begin
        ctr <= ctr + 1;
        if (ctr != 0) begin
            // pass
        end else if (hpos != 799) begin
            hpos <= hpos + 1;
        end else begin
            hpos <= 0;
            if (vpos == 449) vpos <= 0;
            else vpos <= vpos + 1;
        end
    end

    assign vr = vpos[6:2];
    assign vg = hpos[6:2];
    assign vb = led_ctr[28:24];
endmodule
