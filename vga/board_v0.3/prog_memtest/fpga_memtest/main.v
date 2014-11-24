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




    wire [15:0] write_bits;
    wire [15:0] read_bits;
    spi_controller spi_ctlr(.spi_mosi(spi_mosi), .spi_miso(spi_miso), .spi_clk(spi_clk), .spi_ss(spi_ss), .write_bits(write_bits), .read_bits(read_bits));

    // "register" definitions:
    assign leds[2:0] = ~write_bits[2:0];
    assign read_bits[7:0] = write_bits[7:0];

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
    
