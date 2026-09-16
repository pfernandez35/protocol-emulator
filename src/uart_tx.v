/*
 * Copyright (c) 2026 Paul Fernandez
 * SPDX-License-Identifier: Apache-2.0
 *
 * Minimal 8N1 UART transmitter.
 *
 * This is deliberately a fixed-function block: it is step 1 of the protocol
 * emulator ("get a UART transmitter out of a pin"). The whole point of the
 * project is that this block eventually disappears, replaced by firmware
 * running on the emulator core. Keep it around as a reference model and as
 * an area yardstick.
 */

`default_nettype none

module uart_tx #(
    // Clock cycles per bit. 50 MHz / 115200 baud = 434.
    parameter CLK_DIV = 434
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data,   // byte to send, captured on `load`
    input  wire       load,   // single-cycle strobe, ignored while busy
    output reg        tx,     // serial line, idles high
    output wire       busy
);

  localparam CNT_W = $clog2(CLK_DIV);
  localparam [CNT_W-1:0] CNT_MAX = CLK_DIV - 1;

  reg [CNT_W-1:0] cnt;      // baud tick counter
  reg [3:0]       bit_idx;  // which frame bit is currently on the wire
  reg [9:0]       frame;    // {stop, data[7:0], start}, shifted out LSB first
  reg             active;

  assign busy = active;

  always @(posedge clk) begin
    if (!rst_n) begin
      tx      <= 1'b1;
      active  <= 1'b0;
      cnt     <= {CNT_W{1'b0}};
      bit_idx <= 4'd0;
      frame   <= 10'h3FF;
    end else if (!active) begin
      tx <= 1'b1;
      if (load) begin
        frame   <= {1'b1, data, 1'b0};
        tx      <= 1'b0;  // start bit goes out immediately
        cnt     <= {CNT_W{1'b0}};
        bit_idx <= 4'd0;
        active  <= 1'b1;
      end
    end else if (cnt == CNT_MAX) begin
      cnt <= {CNT_W{1'b0}};
      if (bit_idx == 4'd9) begin
        active <= 1'b0;   // stop bit has had its full bit time
        tx     <= 1'b1;
      end else begin
        bit_idx <= bit_idx + 4'd1;
        tx      <= frame[bit_idx+1];
      end
    end else begin
      cnt <= cnt + {{(CNT_W-1){1'b0}}, 1'b1};
    end
  end

endmodule
