# Protocol Emulator — project instructions

## Read BEFORE touching this repo

**Read `context/README.md`, then the files it points to.** This is not optional: the
project has constraints that cannot be inferred from the code alone — a hard area budget,
a competition deadline, judging criteria that drive the architecture, and decisions
already taken whose *reasoning* is written nowhere else.

| File | Contents |
|---|---|
| `context/README.md` | Project map, current state, next actions |
| `context/01-competition.md` | The brief, hard constraints, judging criteria |
| `context/02-decisions.md` | Log of technical and architectural decisions (ADRs) |
| `context/03-workflow.md` | Commands, layout, gotchas already hit |

## The project in one sentence

Design an open-source ASIC: a programmable micro-CPU that bit-bangs hardware protocols
(UART/SPI/I2C) in firmware rather than fixed logic, in **~24,000 cells**, for the Jane
Street competition, **deadline 18 January 2027**. Judged on **functional novelty** and on
**verification methodology**.

## Working rules

1. **Record decisions.** One structural decision made = one entry in
   `context/02-decisions.md`, in the same format as the existing ones (Context / Decision
   / Why / Consequence). Without the why, the decision gets re-litigated in three weeks.
2. **Never contradict an ADR silently.** To reverse a decision, set its status to
   `Superseded` and write a new one. Never rewrite history.
3. **Test through the pins, never internal state** (ADR-004). The suite must stay
   replayable as-is against the post-synthesis netlist.
4. **Timing assertions are exact, never tolerant** (ADR-005). Timing precision is the
   chip's reason to exist.
5. **Watch the area budget on every significant addition.**
   `yosys -p "read_verilog src/*.v; synth -top tt_um_pfernandez35_protoemu -flatten; stat"`
   Benchmark: the fixed UART TX is 104 cells, 0.4% of budget.
6. **Adding a source file takes two edits**: `info.yaml:source_files` **and**
   `test/Makefile:PROJECT_SOURCES`. Forgetting the second gives an incomprehensible error.
7. **`docs/` belongs to Tiny Tapeout** (the published datasheet — CI fails if it is left
   as template stubs). Internal documentation goes in `context/`. Do not mix them.
8. **Everything written in this repo is in English** (ADR-011), including `context/`.
   Spoken exchanges with Paul are in French.

## Paul's call, not the assistant's

- Filling in the Jane Street sign-up form (personal data).
- Settling the ADRs marked **Proposed** — notably 007 (verification strategy) and 009
  (novelty axis), which both constrain the ISA design.
