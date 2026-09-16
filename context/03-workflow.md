# Workflow

## Layout

```
src/
  project.v          Top level. Must be named tt_um_pfernandez35_protoemu.
  uart_tx.v          Fixed 8N1 UART — disposable by design (ADR-003).
test/
  Makefile           PROJECT_SOURCES must list every file in src/.
  tb.v               Verilog wrapper instantiating the top. Dumps waves as FST.
  test.py            cocotb tests.
info.yaml            Tiny Tapeout metadata: tiles, pinout, source_files.
docs/info.md         Datasheet PUBLISHED by Tiny Tapeout. Not to be confused with
                     context/, which is internal working documentation.
context/             This folder. Internal.
.github/workflows/   gds · test · docs · fpga (the real ASIC flow lives here)
```

## Commands

```bash
# RTL simulation — the daily loop
cd test && PATH=../.venv/bin:$PATH make -B

# View waveforms
gtkwave test/tb.fst        # or: surfer test/tb.fst

# Area estimate, no PDK (fast, order of magnitude only)
yosys -p "read_verilog src/*.v; synth -top tt_um_pfernandez35_protoemu -flatten; stat"

# Real PDK area, 6x4 precheck, gate-level test → CI only, on push
```

Local environment: `.venv/` (cocotb 2.0.1, pytest), `iverilog` and `yosys` via Homebrew.
Everything else in the ASIC flow runs in GitHub Actions — nothing to install.

## The CI flow

A `git push` triggers `.github/workflows/gds.yaml`:

| Job | What it gives you |
|---|---|
| `gds` | Synthesis + place & route → GDS. **The real PDK area.** |
| `precheck` | Tiny Tapeout conformance checks. **This is what settles 6x4** (ADR-002). |
| `gl_test` | Replays the cocotb tests against the post-synthesis netlist. Passes unchanged thanks to ADR-004. |
| `viewer` | Publishes a layout view to GitHub Pages. |

`docs.yaml` runs `tt_tool.py --check-docs` against `docs/info.md` and **fails on the
template placeholder text** — the datasheet has to be genuinely written, not left as
stubs.

`fpga.yaml` builds an ICE40UP5K bitstream but does not run on push (`branches: none`).
Worth enabling if a compatible board is available — the blog recommends testing on FPGA
before the ASIC flow.

## Gotchas already hit

**Adding a source file takes two edits.** `info.yaml:source_files` **and**
`test/Makefile:PROJECT_SOURCES`. Forgetting the second produces an obscure elaboration
error that does not point at the cause.

**cocotb 2.x uses `unit=`, not `units=`.** The plural is the 1.x API, and most examples
online are still 1.x.

**Testing a UART with `0xAA` is a trap.** The frame is sent LSB first as
`{stop, data, start}`. With `0xAA`, the start bit (0) and `data[0]` (0) are at the same
level and **merge into a single two-bit-wide pulse** — any bit-width measurement is then
wrong. Use **`0x55`**, whose frame alternates on every slot (`0,1,0,1,0,1,0,1,0,1`), so
each bit is measurable in isolation.

**You must wait for `busy == 0` between bytes.** No shadow register (ADR-006). Strobed
during `busy`, `load` is silently dropped — the test then fails further along on a
missing start bit, at a point that does not identify the cause. See the `wait_idle()`
helper in `test.py`.

**The repo was cloned from the template with `--depth 1`.** The first push to a fresh
remote fails with `did not receive expected object` because the shallow base commit has
no parents. Fixed with `git fetch --unshallow upstream`. The template remote is kept as
`upstream`; `origin` is Paul's repo.

## Conventions

- One `src/*.v` file = one module, same name.
- Every test observes pins, never internal state (ADR-004).
- Every timing assertion is exact, never tolerant (ADR-005).
- One structural decision made = one entry in `02-decisions.md`, with its why.
- Never rewrite a decision: mark it `Superseded` and write a new one (see ADR-010/011).
