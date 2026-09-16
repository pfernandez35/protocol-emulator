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
of `uo_out[0]` as an 8N1 UART frame. 4 cocotb tests green. RTL simulation runs locally;
the full GDS flow runs in CI.

| Measure | Value |
|---|---|
| UART TX area (generic yosys, `-flatten`) | **104 cells**, 23 flip-flops |
| Total budget | ~24,000 cells (24 tiles × ~1K) |
| Occupancy | **~0.4%** |

Reading: a fixed UART costs nothing. The budget will go entirely into the programmable
core — instruction memory, decoder, timing counters. That is where the project is won.

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
