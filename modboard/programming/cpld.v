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
    input p3B1,
    input p3B2,
    input pG0,
    input pRST,
    output p2A2,
    output p2A3,
    output p3A0,
    output p3A1,
    output p3A2,
    output p3A3
    );

    assign p2A2 = 1;
    assign p2A3 = !p3B1;

    assign p3A1 = pRST;

    //reg [13:0] ctr = 0;
    //assign {p3A3, p3A2, p3A1, p3A0} = ctr[13:10];
    //always @(posedge pG0) begin
        //ctr <= ctr + 1;
    //end
    assign p3A3 = p3B2;
    assign p3A2 = !p3B2;

endmodule
