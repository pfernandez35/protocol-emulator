# SPDX-FileCopyrightText: © 2026 Paul Fernandez
# SPDX-License-Identifier: Apache-2.0
r"""ASCII waveform recording and assertion for cocotb tests.

The idea is borrowed from Jane Street's own write-up, "Using ASCII waveforms to
test hardware designs":
https://blog.janestreet.com/using-ascii-waveforms-to-test-hardware-designs/

A test states the waveform it expects as a literal string. On failure the
mismatch is printed as two aligned waveforms with a caret under the first
differing column, which is far easier to read than "assert 0 == 1" -- and it
works in a CI log, with no viewer installed.

    tx   expected  ___/‾‾‾\___/‾‾‾
    tx   actual    ___/‾‾‾‾‾‾‾/‾‾‾
                           ^ first difference, column 7
"""

from cocotb.triggers import Timer

HIGH = "‾"
LOW = "_"
RISE = "/"
FALL = "\\"


def render(samples, width=1):
    """Render a sequence of 0/1 samples as an ASCII waveform.

    Each sample occupies `width` characters. The first character of a sample
    shows the transition into it (/ or \\), the rest show its level.
    """
    out = []
    prev = None
    for s in samples:
        level = HIGH if s else LOW
        if prev is None or s == prev:
            head = level
        else:
            head = RISE if s else FALL
        out.append(head + level * (width - 1))
        prev = s
    return "".join(out)


async def record(signals, period_ns, count, phase_ns=0):
    """Sample every signal `count` times, once per `period_ns`.

    `signals` maps a name to a zero-argument callable returning 0 or 1 -- a
    lambda reading a pin, never internal state (see ADR-004).

    `phase_ns` offsets the first sample. Pass half a period to sample in the
    middle of each bit rather than on its boundary, where the value is settling
    and the reading is a coin flip.
    """
    traces = {name: [] for name in signals}
    if phase_ns:
        await Timer(phase_ns, unit="ns")
    for i in range(count):
        if i:
            await Timer(period_ns, unit="ns")
        for name, probe in signals.items():
            traces[name].append(probe())
    return traces


def assert_wave(name, samples, expected, width=1):
    """Compare a recorded trace against an expected ASCII waveform.

    Raises AssertionError with both waveforms aligned and the first differing
    column marked.
    """
    got = render(samples, width)
    expected = expected.strip()
    if got == expected:
        return

    column = next(
        (i for i, (a, b) in enumerate(zip(got, expected)) if a != b),
        min(len(got), len(expected)),
    )
    label = max(len(name) + 10, 16)
    raise AssertionError(
        "waveform mismatch\n"
        + f"{name + ' expected':<{label}}{expected}\n"
        + f"{name + ' actual':<{label}}{got}\n"
        + " " * (label + column)
        + f"^ first difference, column {column}"
    )


def show(traces, width=1, indent="    "):
    """Format every trace in a dict for logging."""
    label = max(len(n) for n in traces) + 2
    return "\n".join(
        f"{indent}{name:<{label}}{render(samples, width)}"
        for name, samples in traces.items()
    )
