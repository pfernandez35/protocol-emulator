/*
 * Copyright (c) 2026 Paul Fernandez
 * SPDX-License-Identifier: Apache-2.0
 *
 * Protocol emulator ASIC -- Jane Street competition entry.
 *
 * Milestone 1: a byte written on ui_in and strobed with `load` comes out of
 * uo_out[0] as an 8N1 UART frame. This exists to prove the full RTL -> GDS
 * flow end to end and to get a first real area number, not because the final
 * chip will contain a hard UART.
 */

`default_nettype none

module tt_um_pfernandez35_protoemu (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire tx;
  wire busy;

  uart_tx #(
      .CLK_DIV(434)  // 50 MHz / 115200 baud
  ) u_uart_tx (
      .clk  (clk),
      .rst_n(rst_n),
      .data (ui_in),
      .load (uio_in[0]),
      .tx   (tx),
      .busy (busy)
  );

  assign uo_out = {6'b0, busy, tx};

  // uio is entirely input for now (only uio_in[0] is used as the load strobe).
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:1], 1'b0};

endmodule
