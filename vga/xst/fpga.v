`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    01:06:42 09/27/2013 
// Design Name: 
// Module Name:    fpga 
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
module fpga(
        input wire input_clk,
		input wire [7:0] sw,
		input wire [4:0] btn,
		output wire [7:0] led,
		output wire [7:0] seg,
		output wire [3:0] an,
		output wire RsTx,
		input wire RsRx,
        output wire [2:0] vgaRed,
        output wire [2:0] vgaGreen,
        output wire [2:1] vgaBlue,
        output wire Hsync, Vsync
	);
    assign RsTx = 0;
    reg rsrx1=1, rsrx2=1;
    always @(posedge clk) begin
        rsrx1 <= RsRx;
        rsrx2 <= rsrx1;
    end

	assign led = {vgaRed, vgaGreen, vgaBlue};

	dcm #(.D(20), .M(5)) dcm(.CLK_IN(input_clk), .CLK_OUT(clk));
	
	reg [31:0] ctr;
	always @(posedge clk) begin
		ctr <= ctr + 1;
	end
    
    reg [14:0] vpos;
    reg [14:0] hpos;
    
    assign Hsync = (hpos < 656 || hpos >= 752);
    assign Vsync = (vpos < 411 || vpos >= 413);

    always @(posedge clk) begin
        if (hpos == 799) begin
            hpos <= 0;
            if (vpos == 444) vpos <= 0;
            else vpos <= vpos + 1;
        end else begin
            hpos <= hpos + 1;
        end
    end
	
	//assign {vgaRed, vgaGreen, vgaBlue} = (hpos < 640 && vpos < 480) ? sw : 0;
	assign {vgaRed, vgaGreen, vgaBlue} = (hpos < 640 && vpos < 400) ? pixel : 0;
	wire [14:0] addr = {vpos[8:2], hpos[9:2]};
	wire [7:0] pixel;

	wire [14:0] waddr;
    wire [7:0] wdata;
    wire wen;

	framebuf your_instance_name (
	  .clka(clk), // input clka
	  .ena(wen), // input ena
	  .wea(wen), // input [0 : 0] wea
	  .addra(waddr), // input [14 : 0] addra
	  .dina(wdata), // input [7 : 0] dina

	  .clkb(clk), // input clkb
	  .addrb(addr), // input [14 : 0] addrb
	  .doutb(pixel) // output [7 : 0] doutb
	);

    wire [31:0] recvd_data;
    wire recvd_valid;
    uart_multibyte_receiver #(.CLK_CYCLES(25), .MSG_LOG_WIDTH(2))
        receiver(.clk(clk), .data(recvd_data), .valid(recvd_valid), .ack(1'b1), .uart_rx(rsrx2), .reset(btn[0]));

    assign waddr = recvd_data[22:8];
    assign wdata = recvd_data[7:0];
    assign wen = recvd_valid;

	sseg sseg (.clk(clk), .in({1'b0, waddr}), .an(an), .c(seg));
endmodule
