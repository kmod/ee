`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    16:54:47 09/18/2013 
// Design Name: 
// Module Name:    cpld 
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
module cpld(
    input p3B2,
    //input b,
    output reg p3A0,
    output reg p3A1,
    output reg p3A2,
    output reg p3A3

    );

    always @(posedge p3B2) begin
        {p3A3, p3A2, p3A1, p3A0} <= {p3A3, p3A2, p3A1, p3A0} + 1;
    end
    //assign p3A3 = p3B2;
    //assign p3A2 = !p3B2;

endmodule
