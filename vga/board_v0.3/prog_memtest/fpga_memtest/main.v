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
    reg spi_miso;
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

    /*
      input		c1_p0_cmd_clk,
      input		c1_p0_cmd_en,
      input [2:0]	c1_p0_cmd_instr,
      input [5:0]	c1_p0_cmd_bl,
      input [29:0]	c1_p0_cmd_byte_addr,
      output		c1_p0_cmd_empty,
      output		c1_p0_cmd_full,
      input		c1_p0_wr_clk,
      input		c1_p0_wr_en,
      input [C1_P0_MASK_SIZE - 1:0]	c1_p0_wr_mask,
      input [C1_P0_DATA_PORT_SIZE - 1:0]	c1_p0_wr_data,
      output		c1_p0_wr_full,
      output		c1_p0_wr_empty,
      output [6:0]	c1_p0_wr_count,
      output		c1_p0_wr_underrun,
      output		c1_p0_wr_error,
      input		c1_p0_rd_clk,
      input		c1_p0_rd_en,
      output [C1_P0_DATA_PORT_SIZE - 1:0]	c1_p0_rd_data,
      output		c1_p0_rd_full,
      output		c1_p0_rd_empty,
      output [6:0]	c1_p0_rd_count,
      output		c1_p0_rd_overflow,
      output		c1_p0_rd_error,
      */

      wire		c1_p0_cmd_clk;
      reg		c1_p0_cmd_en;
      reg [2:0]	c1_p0_cmd_instr;
      reg [5:0]	c1_p0_cmd_bl;
      reg [29:0]	c1_p0_cmd_byte_addr;
      wire		c1_p0_cmd_empty;
      wire		c1_p0_cmd_full;
      wire		c1_p0_wr_clk;
      reg		c1_p0_wr_en;
      wire [3:0]	c1_p0_wr_mask;
      reg [31:0]	c1_p0_wr_data;
      wire		c1_p0_wr_full;
      wire		c1_p0_wr_empty;
      wire [6:0]	c1_p0_wr_count;
      wire		c1_p0_wr_underrun;
      wire		c1_p0_wr_error;
      wire		c1_p0_rd_clk;
      reg		c1_p0_rd_en;
      wire [31:0]	c1_p0_rd_data;
      wire		c1_p0_rd_full;
      wire		c1_p0_rd_empty;
      wire [6:0]	c1_p0_rd_count;
      wire		c1_p0_rd_overflow;
      wire		c1_p0_rd_error;

    dcm #(.M(3), .D(2), .INPUT_BUFFER(0), .OUTPUT_BUFFER(0)) dcm1(.CLK_IN(input_clk), .CLK_OUT(clk1));
    dcm #(.M(9), .D(2), .INPUT_BUFFER(0), .OUTPUT_BUFFER(0)) dcm3(.CLK_IN(input_clk), .CLK_OUT(clk3));
    wire c1_rst; // active high
    wire c3_rst; // active high
    mem #(
        .C1_RST_ACT_LOW(0),
        .C3_RST_ACT_LOW(0)
    ) mem(
        .c1_sys_clk(clk1),
        .c1_sys_rst_i(c1_rst),
        .c3_sys_clk(clk3),
        .c3_sys_rst_i(c3_rst),
        .c1_calib_done(c1_calib_done),
        .c3_calib_done(c3_calib_done),

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
        .mcb3_dram_ck_n(mcb3_dram_ck_n),

        .c1_p0_cmd_clk(c1_p0_cmd_clk),
        .c1_p0_cmd_en(c1_p0_cmd_en),
        .c1_p0_cmd_instr(c1_p0_cmd_instr),
        .c1_p0_cmd_bl(c1_p0_cmd_bl),
        .c1_p0_cmd_byte_addr(c1_p0_cmd_byte_addr),
        .c1_p0_cmd_empty(c1_p0_cmd_empty),
        .c1_p0_cmd_full(c1_p0_cmd_full),
        .c1_p0_wr_clk(c1_p0_wr_clk),
        .c1_p0_wr_en(c1_p0_wr_en),
        .c1_p0_wr_mask(c1_p0_wr_mask),
        .c1_p0_wr_data(c1_p0_wr_data),
        .c1_p0_wr_full(c1_p0_wr_full),
        .c1_p0_wr_empty(c1_p0_wr_empty),
        .c1_p0_wr_count(c1_p0_wr_count),
        .c1_p0_wr_underrun(c1_p0_wr_underrun),
        .c1_p0_wr_error(c1_p0_wr_error),
        .c1_p0_rd_clk(c1_p0_rd_clk),
        .c1_p0_rd_en(c1_p0_rd_en),
        .c1_p0_rd_data(c1_p0_rd_data),
        .c1_p0_rd_full(c1_p0_rd_full),
        .c1_p0_rd_empty(c1_p0_rd_empty),
        .c1_p0_rd_count(c1_p0_rd_count),
        .c1_p0_rd_overflow(c1_p0_rd_overflow),
        .c1_p0_rd_error(c1_p0_rd_error)
    );

    assign c1_p0_cmd_clk = spi_clk;
    assign c1_p0_wr_clk = spi_clk;
    assign c1_p0_rd_clk = spi_clk;
    assign c1_rst = spi_ss;
    assign c3_rst = spi_ss;


    reg [15:0] write_bits;
    wire [31:0] read_bits;
    //spi_controller spi_ctlr(.spi_mosi(spi_mosi), .spi_miso(spi_miso), .spi_clk(spi_clk), .spi_ss(spi_ss), .write_bits(write_bits), .read_bits(read_bits));

    // "register" definitions:
    assign leds[2:0] = ~write_bits[2:0];
    assign read_bits[7:0] = write_bits[7:0];
    assign read_bits[8] = c1_calib_done;
    assign read_bits[9] = c3_calib_done;
    assign read_bits[10] = c1_p0_cmd_empty;
    assign read_bits[11] = c1_p0_cmd_full;
    assign read_bits[12] = c1_p0_wr_empty;
    assign read_bits[13] = c1_p0_wr_full;
    assign read_bits[14] = c1_p0_wr_underrun;
    assign read_bits[15] = c1_p0_wr_error;
    assign read_bits[16] = c1_p0_rd_empty;
    assign read_bits[17] = c1_p0_rd_full;
    assign read_bits[18] = c1_p0_rd_overflow;
    assign read_bits[19] = c1_p0_rd_error;

    /*
endmodule

module spi_controller(
    input wire spi_mosi,
    output reg spi_miso,
    input wire spi_clk,
    input wire spi_ss,

    output reg [15:0] write_bits,
    input wire [31:0] read_bits
    );
    */

    reg [2:0] spi_ctr = 0;
    reg [7:0] spi_in_byte;
    reg [7:0] spi_out_byte = 0;

    localparam IDLE = 0;
    localparam READ = 1;
    localparam WRITE = 2;
    localparam READMEM = 3;
    localparam WRITEMEM = 4;
    reg [3:0] state = IDLE;

    wire [7:0] new_spi_in_byte;
    assign new_spi_in_byte = {spi_in_byte[6:0], spi_mosi};
    wire [2:0] new_spi_ctr;
    assign new_spi_ctr = spi_ctr + 1'b1;

    reg[31:0] mem_addr;
    reg [3:0] mem_ctr;
    wire [3:0] new_mem_ctr;
    assign new_mem_ctr = mem_ctr + 1'b1;

    always @(*) begin
        c1_p0_cmd_instr = 3'b001; // READ
        c1_p0_cmd_bl = 0;
        c1_p0_cmd_byte_addr = mem_addr;
        c1_p0_cmd_en = 0;
        c1_p0_rd_en = 0;
        c1_p0_wr_en = 0;

        if (state == READMEM) begin
            c1_p0_cmd_instr = 3'b001; // READ
            c1_p0_cmd_en = (mem_ctr == 4) && (new_spi_ctr == 0);
            c1_p0_rd_en = (mem_ctr == 9) && (new_spi_ctr == 0);
        end else if (state == WRITEMEM) begin
            c1_p0_cmd_instr = 3'b000; // WRITE
            c1_p0_cmd_en = (mem_ctr == 8) && (new_spi_ctr == 0);
            c1_p0_wr_en = (mem_ctr == 4) && (new_spi_ctr == 0);
        end
    end

    always @(posedge spi_clk or posedge spi_ss) begin
        if (spi_ss) begin
            spi_ctr <= 0;
            state <= IDLE;
            spi_out_byte <= 0;
        end else begin
            spi_ctr <= new_spi_ctr;
            spi_in_byte <= new_spi_in_byte;
            spi_out_byte <= {spi_out_byte[6:0], 1'b0};
            if (new_spi_ctr == 0) begin
                case (state)
                    IDLE: begin
                        if (new_spi_in_byte == 8'h01)
                            state <= READ;
                        else if (new_spi_in_byte == 8'h02)
                            state <= WRITE;
                        else if (new_spi_in_byte == 8'h03) begin
                            state <= READMEM;
                            mem_ctr <= 0;
                        end else if (new_spi_in_byte == 8'h04) begin
                            state <= WRITEMEM;
                            mem_ctr <= 0;
                        end
                    end
                    READ: begin
                        spi_out_byte <= {7'b0, read_bits[new_spi_in_byte[4:0]]};
                        state <= IDLE;
                    end
                    WRITE: begin
                        write_bits[new_spi_in_byte[4:1]] <= new_spi_in_byte[0];
                        state <= IDLE;
                    end
                    READMEM: begin
                        mem_ctr <= mem_ctr + 1'b1;

                        case (mem_ctr)
                            0: begin
                                mem_addr[31:24] <= new_spi_in_byte;
                            end
                            1: begin
                                mem_addr[23:16] <= new_spi_in_byte;
                            end
                            2: begin
                                mem_addr[15:8] <= new_spi_in_byte;
                            end
                            3: begin
                                mem_addr[7:0] <= new_spi_in_byte;
                            end
                            4: begin
                                // dummy byte for submitting command
                                spi_out_byte <= 8'b10101010;
                            end
                            5: begin
                                spi_out_byte <= {c1_p0_rd_count, c1_p0_rd_overflow, c1_p0_rd_error};
                            end
                            6: begin
                                spi_out_byte <= c1_p0_rd_data[31:24];
                            end
                            7: begin
                                spi_out_byte <= c1_p0_rd_data[23:16];
                            end
                            8: begin
                                spi_out_byte <= c1_p0_rd_data[15:8];
                            end
                            9: begin
                                spi_out_byte <= c1_p0_rd_data[7:0];
                                state <= IDLE;
                            end
                        endcase
                    end
                    WRITEMEM: begin
                        mem_ctr <= mem_ctr + 1'b1;

                        case (mem_ctr)
                            0: begin
                                c1_p0_wr_data[31:24] <= new_spi_in_byte;
                                spi_out_byte <= 0;
                            end
                            1: begin
                                c1_p0_wr_data[23:16] <= new_spi_in_byte;
                                spi_out_byte <= 1;
                            end
                            2: begin
                                c1_p0_wr_data[15:8] <= new_spi_in_byte;
                                spi_out_byte <= 2;
                            end
                            3: begin
                                c1_p0_wr_data[7:0] <= new_spi_in_byte;
                                spi_out_byte <= 3;
                            end
                            4: begin
                                mem_addr[31:24] <= new_spi_in_byte;
                                spi_out_byte <= {c1_p0_wr_count, c1_p0_wr_underrun, c1_p0_wr_error};
                            end
                            5: begin
                                mem_addr[23:16] <= new_spi_in_byte;
                                spi_out_byte <= {c1_p0_wr_count, c1_p0_wr_underrun, c1_p0_wr_error};
                            end
                            6: begin
                                mem_addr[15:8] <= new_spi_in_byte;
                                spi_out_byte <= 6;
                            end
                            7: begin
                                mem_addr[7:0] <= new_spi_in_byte;
                                spi_out_byte <= 7;
                            end
                            8: begin
                                // dummy byte for submitting command
                                spi_out_byte <= 8'b10101010;
                            end
                            9: begin
                                spi_out_byte <= {c1_p0_wr_count, c1_p0_wr_underrun, c1_p0_wr_error};
                                state <= IDLE;
                            end
                        endcase
                    end
                endcase
            end
        end
    end

    always @(negedge spi_clk or posedge spi_ss) begin
        if (spi_ss)
            spi_miso <= 0;
        else
            spi_miso <= spi_out_byte[7];
    end
endmodule
    
