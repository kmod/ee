`timescale 1ns / 1ps

module dcm #(parameter M=5, D=20)
 (// Clock in ports
  input         CLK_IN,
  // Clock out ports
  output        CLK_OUT
 );

  // Input buffering
  //------------------------------------
  IBUFG clkin1_buf
   (.O (clkin1),
    .I (CLK_IN));


  // Clocking primitive
  //------------------------------------

  // Instantiation of the DCM primitive
  //    * Unused inputs are tied off
  //    * Unused outputs are labeled unused
  wire        psdone_unused;
  //wire        locked_int;
  //wire [7:0]  status_int;
  wire clkfb;
  wire clk0;
  wire clkfx;

  DCM_SP
  #(.CLKDV_DIVIDE          (10),
    .CLKFX_DIVIDE          (D),
    .CLKFX_MULTIPLY        (M),
    .CLKIN_DIVIDE_BY_2     ("FALSE"),
    .CLKIN_PERIOD          (10.0),
    .CLKOUT_PHASE_SHIFT    ("NONE"),
    .CLK_FEEDBACK          ("1X"),
    .DESKEW_ADJUST         ("SYSTEM_SYNCHRONOUS"),
    .PHASE_SHIFT           (0),
    .STARTUP_WAIT          ("FALSE"))
  dcm_sp_inst
    // Input clock
   (.CLKIN                 (clkin1),
    .CLKFB                 (clkfb),
    // Output clocks
    .CLK0                  (clk0),
    .CLK90                 (),
    .CLK180                (),
    .CLK270                (),
    .CLK2X                 (),
    .CLK2X180              (),
    .CLKFX                 (clkfx),
    .CLKFX180              (),
    .CLKDV                 (),
    // Ports for dynamic phase shift
    .PSCLK                 (1'b0),
    .PSEN                  (1'b0),
    .PSINCDEC              (1'b0),
    .PSDONE                (),
    // Other control and status signals
    .LOCKED                (),
    .STATUS                (),
    .RST                   (1'b0),
    // Unused pin- tie low
    .DSSEN                 (1'b0));


  // Output buffering
  //-----------------------------------
  BUFG clkf_buf
   (.O (clkfb),
    .I (clk0));

  BUFG clkout1_buf
   (.O   (CLK_OUT),
    .I   (clkfx));

endmodule

module sseg #(parameter N=18) (
		input wire clk,
		input wire [15:0] in,
		output reg [7:0] c,
		output reg [3:0] an
	);
	/**
	A simple seven-segment display driver, designed for the display on the Nexys 3.
	
	N: the driver will iterate over all four digits every 2**N clock cycles
	clk: the clock that is the source of timing for switching between digits
	in: a 16-bit value; each of the 4-bit nibbles will be put onto the display, msb leftmost
	c: an 8-bit output determining the segments to display.  active low.
	an: a 4-bit output determining the characters to enable.  active low.
	
	With a 10MHz clock I've been using N=16, which gives a full cycle every 6ms
	**/

	reg [N-1:0] ctr; // counter that determines which digit to display
	always @(posedge clk) begin
		ctr <= ctr + 1'b1;
	end
	
	wire [1:0] digit; // use the top two bits of the counter as the digit identifier
	assign digit = ctr[N-1:N-2];
	
	reg [3:0] val;
	always @(*) begin
		an = 4'b1111;
		an[digit] = 0;
		// select the values for the digit:
		case (digit)
			2'b00: val = in[3:0];
			2'b01: val = in[7:4];
			2'b10: val = in[11:8];
			2'b11: val = in[15:12];
		endcase

		// map that to a segment map:
		case(val)
			4'b0000: c = 8'b11000000;
			4'b0001: c = 8'b11111001;
			4'b0010: c = 8'b10100100;
			4'b0011: c = 8'b10110000;
			4'b0100: c = 8'b10011001;
			4'b0101: c = 8'b10010010;
			4'b0110: c = 8'b10000010;
			4'b0111: c = 8'b11111000;
			4'b1000: c = 8'b10000000;
			4'b1001: c = 8'b10010000;
			4'b1010: c = 8'b10001000;
			4'b1011: c = 8'b10000011;
			4'b1100: c = 8'b10100111;
			4'b1101: c = 8'b10100001;
			4'b1110: c = 8'b10000110;
			4'b1111: c = 8'b10001110;
			default: c = 8'b10110110;
		endcase
	end
endmodule


module uart_receiver #(parameter CLK_CYCLES=4178, CTR_WIDTH=16)
	(input wire clk, output reg [7:0] data, output reg received, input wire uart_rx);
		reg [CTR_WIDTH-1:0] ctr = CLK_CYCLES;
		
		reg [4:0] bits_left = 0;
		reg receiving = 0;
		
		always @(posedge clk) begin
			ctr <= ctr - 1'b1;
			received <= 0;
			
			if (ctr == 0) begin
				ctr <= (CLK_CYCLES-1);
				
				data <= {uart_rx, data[7:1]};
				bits_left <= bits_left - 1'b1;
				if (receiving && (bits_left == 1)) begin
					received <= 1;
				end
				if (bits_left == 0) begin
					receiving <= 0;
				end
			end
			
			if (uart_rx == 0 && !receiving) begin
				ctr <= (CLK_CYCLES-1 + CLK_CYCLES / 2); // try to sample in the middle of the bit, to maximize clk rate flexibility.  wait an additional CLK_CYCLES to skip the rest of the start bit
				bits_left <= 4'd8;
				receiving <= 1;
			end
		end
endmodule

module uart_multibyte_receiver #(parameter CLK_CYCLES=4178, CTR_WIDTH=16, MSG_LOG_WIDTH=3)
	(input wire clk, output reg [8*(2**MSG_LOG_WIDTH)-1:0] data, output reg valid, input wire ack, input wire uart_rx, output wire [7:0] led, input wire reset);
		reg [MSG_LOG_WIDTH-1:0] byte_idx;
		wire [MSG_LOG_WIDTH-1:0] next_byte_idx;
		assign next_byte_idx = byte_idx + 1'b1;
		
		reg [8*(2**MSG_LOG_WIDTH)-1:0] buffer;
		wire [8*(2**MSG_LOG_WIDTH)-1:0] next_buffer;
		assign next_buffer = {recvd_byte, buffer[8*(2**MSG_LOG_WIDTH)-1:8]};
		
		wire [7:0] recvd_byte;
		wire recvd_valid;
		uart_receiver #(.CLK_CYCLES(CLK_CYCLES)) uart_rvr(.clk(clk), .data(recvd_byte), .received(recvd_valid), .uart_rx(uart_rx));
				
		always @(posedge clk) begin
			if (ack) valid <= 1'b0;
			
			if (recvd_valid) begin
				buffer <= next_buffer;
				byte_idx <= next_byte_idx;
				if (next_byte_idx == 0) begin
					data <= next_buffer;
					valid <= 1'b1;
				end
			end

            if (reset) begin
                byte_idx <= 0;
            end
		end
endmodule
