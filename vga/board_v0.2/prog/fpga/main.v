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
    input wire input_clk
    );

    reg [31:0] ctr;
    always @(posedge input_clk) begin
        ctr <= ctr + 1'b1;
    end
    assign leds = ~ctr[26:24];

endmodule
