## How it works

A programmable core for bit-banging hardware protocols. Rather than putting a UART
block, an SPI block and an I2C block on one die, the goal is a small CPU whose
instruction set is built for reading pins, writing pins, counting cycles and hitting
timing precisely — so that a protocol is implemented in firmware and the chip stays
reprogrammable after fabrication.

**Current state: milestone 1.** The design currently contains a fixed-function 8N1 UART
transmitter. This is deliberate scaffolding, not the architecture: it proves the RTL →
GDS flow end to end, gives a first real area number to budget against, and will serve as
a reference model for verifying the UART firmware once the programmable core exists. It
is meant to be deleted.

A byte presented on `ui_in` and strobed with `uio_in[0]` is shifted out of `uo_out[0]`
as a standard 8N1 frame: one start bit low, eight data bits LSB first, one stop bit high.
Each bit slot is exactly `CLK_DIV` clock cycles wide (434 by default, giving 115200 baud
from a 50 MHz clock). `uo_out[1]` is high while a frame is in flight; `load` is ignored
during that time, as there is no shadow register — back-to-back framing is a policy that
belongs in firmware, not in fixed logic.

Area, from generic yosys synthesis: 104 cells, 23 flip-flops — roughly 0.4% of the
~24k-cell budget for 6x4 tiles. Nearly all of the budget remains for the programmable
core.

## How to test

Drive `clk` at 50 MHz and release `rst_n`. Put a byte on `ui_in[7:0]`, then pulse
`uio_in[0]` high for a single clock cycle. The frame appears on `uo_out[0]`.

Connect `uo_out[0]` to any 3.3 V USB-serial adapter's RX line and open a terminal at
**115200 baud, 8N1**. Each strobe produces one character. Wait for `uo_out[1]` (busy) to
go low before loading the next byte.

For a different baud rate, scale the `CLK_DIV` parameter in `src/project.v`:
`CLK_DIV = clock_hz / baud`.

The cocotb test suite in `test/` decodes the serial line the way a receiver would —
sampling at the midpoint of each bit — so it runs unmodified against both RTL and the
post-synthesis gate-level netlist. It also asserts that every bit slot is exactly
`CLK_DIV` cycles wide, since timing precision is the entire point of the chip.

## External hardware

None required. A 3.3 V USB-serial adapter (FT232, CP2102 or similar) on `uo_out[0]` is
useful for observing the output, as is a logic analyser or oscilloscope for checking bit
timing in silicon.
