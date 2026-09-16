# SPDX-FileCopyrightText: © 2026 Paul Fernandez
# SPDX-License-Identifier: Apache-2.0
"""Milestone 1 tests: a real UART frame comes out of uo_out[0].

The testbench decodes the serial line the way a receiver would -- sample in
the middle of each bit time -- rather than peeking at internal state, so the
same test will keep working against the gate-level netlist.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer

from waveform import assert_wave, record, show

CLK_NS = 20  # 50 MHz
CLK_DIV = 434  # must match the CLK_DIV parameter in project.v
BIT_NS = CLK_NS * CLK_DIV


def tx(dut):
    return int(dut.uo_out.value) & 1


def busy(dut):
    return (int(dut.uo_out.value) >> 1) & 1


async def reset(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


async def send(dut, byte):
    """Strobe `load` for one clock cycle with `byte` on the data pins."""
    dut.ui_in.value = byte
    dut.uio_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0


async def wait_idle(dut, timeout_bits=20):
    """Block until the transmitter has finished the frame in flight.

    The core accepts a new byte only when not busy -- there is no shadow
    register. That is a deliberate milestone-1 simplification; the emulator
    core will handle back-to-back framing in firmware instead.
    """
    for _ in range(timeout_bits * CLK_DIV):
        await RisingEdge(dut.clk)
        if busy(dut) == 0:
            return
    raise AssertionError("transmitter never went idle")


async def capture_frame(dut, timeout_bits=20):
    """Wait for a start bit, then decode one 8N1 frame. Returns the byte."""
    for _ in range(timeout_bits * CLK_DIV):
        await RisingEdge(dut.clk)
        if tx(dut) == 0:
            break
    else:
        raise AssertionError("no start bit seen on uo_out[0]")

    # Move to the middle of the start bit, verify it, then step bit by bit.
    await Timer(BIT_NS // 2, unit="ns")
    assert tx(dut) == 0, "start bit was not low at its midpoint"

    value = 0
    for i in range(8):
        await Timer(BIT_NS, unit="ns")
        value |= tx(dut) << i  # LSB first

    await Timer(BIT_NS, unit="ns")
    assert tx(dut) == 1, "stop bit was not high"
    return value


@cocotb.test()
async def test_uart_bytes(dut):
    """Send a few bytes and decode them off the pin."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    assert tx(dut) == 1, "line should idle high after reset"

    for byte in (0xA5, 0x00, 0xFF, 0x01, 0x80):
        await send(dut, byte)
        got = await capture_frame(dut)
        assert got == byte, f"sent 0x{byte:02X}, received 0x{got:02X}"
        dut._log.info(f"0x{byte:02X} round-tripped")
        await wait_idle(dut)


@cocotb.test()
async def test_busy_flag(dut):
    """busy rises with the frame and clears only after the stop bit."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    assert busy(dut) == 0, "busy should be low when idle"

    await send(dut, 0x5A)
    await ClockCycles(dut.clk, 1)
    assert busy(dut) == 1, "busy should be high right after load"

    # Still busy just before the end of the 10-bit frame.
    await Timer(BIT_NS * 10 - CLK_NS * 4, unit="ns")
    assert busy(dut) == 1, "busy dropped before the frame finished"

    await Timer(CLK_NS * 8, unit="ns")
    assert busy(dut) == 0, "busy did not clear after the stop bit"


@cocotb.test()
async def test_load_ignored_while_busy(dut):
    """A load during a frame must not corrupt the byte in flight."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    await send(dut, 0xC3)

    async def heckle():
        # Hammer load with a different byte while the first one is going out.
        for _ in range(5):
            await Timer(BIT_NS, unit="ns")
            await send(dut, 0x3C)

    cocotb.start_soon(heckle())
    got = await capture_frame(dut)
    assert got == 0xC3, f"frame corrupted by mid-transmission load: 0x{got:02X}"


@cocotb.test()
async def test_bit_timing(dut):
    """Every bit must be exactly CLK_DIV clocks wide -- this is the whole point.

    Timing precision is the core value proposition of the final chip, so it
    gets asserted from day one rather than eyeballed in a waveform.
    """
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    # 0x55 makes the frame alternate on every single bit slot
    # (0,1,0,1,0,1,0,1,0,1), so each slot is its own level run and can be
    # measured independently. 0xAA would merge the start bit with data[0].
    await send(dut, 0x55)

    # Find the start bit edge.
    while tx(dut) == 1:
        await RisingEdge(dut.clk)

    # Measure the width of each of the 10 bit slots in clock cycles.
    for slot in range(10):
        level = tx(dut)
        cycles = 0
        while True:
            await RisingEdge(dut.clk)
            cycles += 1
            if tx(dut) != level or cycles > CLK_DIV * 2:
                break
        if slot == 9:
            break  # the stop bit runs into idle, which is the same level
        assert cycles == CLK_DIV, (
            f"bit slot {slot} lasted {cycles} clocks, expected {CLK_DIV}"
        )


@cocotb.test()
async def test_frame_waveform(dut):
    """Assert the serial line against a literal ASCII waveform.

    Technique borrowed from Jane Street's "Using ASCII waveforms to test
    hardware designs". The expected shape of the frame is written out in the
    test, so a regression shows up as two misaligned pictures rather than as a
    failed integer comparison.

    Each column is one bit time, sampled at its midpoint:
    start, d0..d7 (LSB first), stop, idle.
    """
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    for byte, expected in (
        (0x55, "___/‾‾\\__/‾‾\\__/‾‾\\__/‾‾\\__/‾‾‾‾‾"),
        (0xA5, "___/‾‾\\__/‾‾\\_____/‾‾\\__/‾‾‾‾‾‾‾‾"),
    ):
        await send(dut, byte)

        # Line up on the start bit, then sample at each bit's midpoint.
        while tx(dut) == 1:
            await RisingEdge(dut.clk)

        traces = await record(
            {"tx": lambda: tx(dut)},
            period_ns=BIT_NS,
            count=11,
            phase_ns=BIT_NS // 2,
        )
        dut._log.info(f"0x{byte:02X}\n{show(traces, width=3)}")
        assert_wave("tx", traces["tx"], expected, width=3)
        await wait_idle(dut)
