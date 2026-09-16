# Project context — read before any work session

Protocol emulator ASIC. Entry for the Jane Street competition.
**Deadline: 18 January 2027.**

## Read in this order

| File | Contents | When |
|---|---|---|
| **[01-competition.md](01-competition.md)** | The brief, hard constraints, judging criteria, open questions | Once, in full |
| **[02-decisions.md](02-decisions.md)** | Log of technical and architectural decisions, with their *why* | Before overturning anything |
| **[03-workflow.md](03-workflow.md)** | Commands, layout, gotchas already hit | When you start coding |

Rule: **one structural decision made = one entry in `02-decisions.md`.**
Without it the reasoning is lost and gets re-litigated three weeks later.

## State as of 16 September 2026

Milestone 1 **done**: a byte written to `ui_in` and strobed with `uio_in[0]` comes out
of `uo_out[0]` as an 8N1 UART frame. 5 cocotb tests green. **The design has been through
the real flow**: synthesised, placed and routed, and `precheck` passes at 6x4.

| Measure | Generic yosys | **Real PDK** |
|---|---|---|
| Cells | 104 | **177** |
| Flip-flops | 23 | **23** |
| Cell area | — | **2,429 µm²** (46% sequential) |
| Die | — | 1289.28 × 710.64 µm = **0.92 mm²** |
| Utilisation | ~0.4% | **0.296%** |

Two things worth knowing from these numbers:

**45 of the 177 cells are `tiehi`/`tielo`** — a quarter of the design exists only to tie
unused output pins to a constant, because the Tiny Tapeout harness requires every pin to
be driven. Fixed overhead; it does not scale with the design, but do not be surprised by
it again.

**The real ceiling is higher than the blog's estimate.** At 2,429 µm² for 177 cells
(≈13.7 µm²/cell), the 902,417 µm² core would hold ~65,000 cells at 100% utilisation, so
roughly **39,000 at a routable 60%** — against the blog's ~24,000. Keep planning against
24,000: the margin is what place & route will consume. Treat the difference as headroom,
not as budget.

Reading: a fixed UART costs nothing. The budget will go entirely into the programmable
core — instruction memory, decoder, timing counters. That is where the project is won.

### Known broken

`gl_test` fails on an upstream PDK bug — `Unknown module type: ihp_dff_r` in the
standard-cell Verilog view. Not our design: `gds` and `precheck` pass. It blocks
gate-level verification for every project on this PDK. See `01-competition.md`.

## Blocked on / next actions

1. **Sign up** with Jane Street — Paul's to do. Not a formality: it is what triggers the
   email if the 8x4 area increase (+30%) is unlocked, which would change the architecture.
2. **Settle the Proposed ADRs** — 007 (verification strategy) and 009 (novelty axis).
   Both constrain the ISA, so they must be decided before week 2.
3. **ISA design** (weeks 2–3) — the structural decision of the project. Nothing serious
   starts before it.

## Schedule

| Weeks | Goal |
|---|---|
| 1 ✅ | Environment + UART TX + first area measurement |
| 2–3 | ISA design: spec + assembler + instruction set simulator (ISS) |
| 4–6 | RTL core, co-simulated against the ISS |
| 7–9 | UART/SPI/I2C firmware, proven against reference models |
| 10–12 | Fit the budget: SRAM, synthesis, timing |
| 13–15 | Stretch (low-speed USB / sniffer mode) + formal proofs |
| 16–17 | Write-up, demos, repo polish — half the score |
| 18 | Slack + submission |
