# The competition

Source: https://blog.janestreet.com/protocol-emulator-asic-competition/ (10 Sep 2026)
Contact: `asic-competition@janestreet.com`

## What is being asked

Design an **open-source, general-purpose protocol emulator**: a tiny CPU whose
instruction set is built for reading pins, writing pins, counting cycles and hitting
timing precisely enough that a protocol is implemented **in firmware**, not in fixed
logic.

> "The goal isn't to put a UART block, an SPI block, and an I2C block on one die and
> call it done."

The chip must stay **reprogrammable after fabrication**, within its timing and I/O
constraints. Named references: the RP2040's PIO state machines and TI Sitara PRU cores —
"and consider what you'd do differently".

- **Minimum**: UART, SPI, I2C
- **Stretch**: low-speed USB, 10 Mbit Ethernet
- **Also floated**: JTAG, SWD, PS/2, CAN

## Hard constraints

| | |
|---|---|
| Process | IHP 130nm CMOS5L (`ihp-sg13cmos5l`) via [Tiny Tapeout](https://www.tinytapeout.com/) |
| Template | [`TinyTapeout/ttihp-verilog-template`](https://github.com/TinyTapeout/ttihp-verilog-template/tree/cmos5l), branch `cmos5l` |
| Area | **6x4 tiles** ≈ 0.7 mm²; budget ≈ **1K logic cells / tile** → ~24,000 cells |
| Licence | Open source required. Public development encouraged (nothing to keep hidden) |
| Teams | Strongly recommended |
| Deadline | **18 January 2027** |
| Tools | All free and open source |

Nothing forbids the use of AI. Quite the opposite — see the criteria below.

## Judging criteria

Verbatim, they are looking for:

1. **Unique functionality**
2. **Novel approaches to design and verification** — they name "formal methods, random
   constrained tests, **AI-assisted verification**"

> "As AI-assisted chip design becomes more common, we believe verification will be an
> extremely important aspect of the ASIC design flow going forwards."

**Direct strategic consequence**: verification is not end-of-project drudgery, it is a
**judged deliverable**. A more modest design with a remarkable verification methodology
beats an ambitious one that is poorly verified. See ADR-007.

## Prize

Jane Street pays to tape out the most novel designs on a Tiny Tapeout shuttle, targeting
**March 2027** (subject to the foundry schedule). Winners receive the fabricated chip
mounted on a dev board.

## Open questions

- [ ] **Is 6x4 actually accepted by the tools?** The upstream `info.yaml` comment only
      lists `1x1, 1x2, 2x2, 3x2, 4x2, 6x2, 8x2`. The blog mandates 6x4. We set 6x4
      (ADR-002). **CI is the arbiter** — the `precheck` job will settle it. If it fails:
      email `asic-competition@janestreet.com`.
- [ ] **8x4 (+30% area)** is "under consideration". They will email **people who signed
      up**. → a concrete reason to fill in the sign-up form, beyond formality.
- [ ] **Maximum clock frequency** on this node. We assumed 50 MHz (ADR-008). It sets the
      timing resolution, hence the maximum bit rate, hence whether low-speed USB
      (1.5 Mbit/s) and 10M Ethernet are realistic. **Confirm before freezing the ISA.**
- [ ] **Sign-up form**: not yet submitted. Paul's to do (personal data).
      https://docs.google.com/forms/d/e/1FAIpQLSeF7fq756MegxZRQxotBwUJYZx-cL9MrGjxV0z4uD_J0sADxQ/viewform
- [ ] The **final submission link** will be added to the blog page closer to the deadline.

## Resources

- Tiny Tapeout documentation: https://www.tinytapeout.com/
- SRAM example on this node: https://www.tinytapeout.com/chips/ttihp0p2/tt_um_urish_sram_test
- Hardcaml (their in-house tool, not required): https://hardcaml.org/
