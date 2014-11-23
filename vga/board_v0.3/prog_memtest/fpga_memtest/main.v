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

    , output reg [2:0] leds

    , inout wire [2:0] mb_a
    , inout wire [3:0] mb_b
    , inout wire [3:2] mb_c
    , inout wire [3:2] mb_d
    );

    wire spi_mosi;
    reg spi_miso;
    wire spi_clk;
    wire spi_ss;
    assign spi_mosi = mb_a[0];
    assign mb_a[1] = spi_miso;
    assign spi_clk = mb_a[2];
    assign spi_ss = mb_b[0];

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
                    spi_out_byte <= 8'hab;
                    state <= IDLE;
                end
                WRITE: begin
                    case ({new_spi_in_byte[7:1], 1'b0})
                        8'b00001000:
                            leds[0] <= new_spi_in_byte[0];
                        8'b00001010:
                            leds[1] <= new_spi_in_byte[0];
                        8'b00001100:
                            leds[2] <= new_spi_in_byte[0];
                        default:
                            spi_out_byte <= 8'h11;
                    endcase
                    state <= IDLE;
                end
            endcase
        end
    end

    always @(negedge spi_clk) begin
        spi_miso <= spi_out_byte[7];
    end

    /*
    reg [31:0] led_ctr;
    always @(posedge spi_clk) begin
        led_ctr <= led_ctr + 1'b1;
    end
    assign leds = ~led_ctr[2:0];
    */

endmodule
