# Decision log

Format: one structural decision = one entry. Abandoned decisions are kept too (status
`Superseded`), because knowing what was ruled out and why is what stops it being
re-proposed two months later.

| # | Decision | Status |
|---|---|---|
| [001](#adr-001--verilog-rather-than-hardcaml) | Verilog rather than Hardcaml | Accepted |
| [002](#adr-002--tiles-6x4-despite-the-template) | `tiles: 6x4` despite the template | Accepted, pending CI |
| [003](#adr-003--milestone-1-is-disposable-by-design) | Milestone 1 is disposable by design | Accepted |
| [004](#adr-004--tests-decode-the-pin-never-internal-state) | Tests read pins, never internal state | Accepted |
| [005](#adr-005--timing-is-asserted-from-day-one) | Timing asserted from day one | Accepted |
| [006](#adr-006--no-shadow-register-on-the-uart-tx) | No shadow register on the UART TX | Accepted, local scope |
| [007](#adr-007--verification-is-a-deliverable-not-a-chore) | Verification is a deliverable | **Proposed** |
| [008](#adr-008--clock-assumed-at-50-mhz) | Clock at 50 MHz | **Provisional** |
| [009](#adr-009--novelty-axis--listen-dont-just-talk) | Novelty axis: listen, don't just talk | **Proposed** |
| [010](#adr-010--internal-docs-in-french-code-and-public-docs-in-english) | Internal docs in French | **Superseded by 011** |
| [011](#adr-011--everything-in-english) | Everything in English | Accepted |

---

## ADR-001 — Verilog rather than Hardcaml

**Status:** Accepted · 16 Sep 2026

**Context.** Jane Street uses Hardcaml (an OCaml DSL for RTL generation) for its own
designs and mentions it in the post. Using it would carry signalling value with the
judges. The official competition template is Verilog.

**Decision.** Verilog.

**Why.** Paul has FPGA and VHDL experience, but from several years ago. Hardcaml would
stack learning OCaml *and* a hardware-generation DSL on top of an HDL refresher, on an
already dense project with an 18-week deadline. The Verilog path is the one the template,
the Tiny Tapeout documentation and almost every available example follow — less friction
at every point where we get stuck.

**Consequence.** We give up an easy point of appeal. We compensate on the verification
axis (ADR-007), which weighs more heavily in the stated criteria. Worth reconsidering
only if the project runs far ahead of schedule, which is unlikely.

---

## ADR-002 — `tiles: 6x4` despite the template

**Status:** Accepted, pending CI · 16 Sep 2026

**Context.** The blog explicitly mandates `tiles: "6x4"` in `info.yaml`. The upstream
template comment lists only `1x1, 1x2, 2x2, 3x2, 4x2, 6x2, 8x2` as valid — 6x4 is absent.

**Decision.** Set `6x4` as the blog requires, and let CI settle it.

**Why.** Two hypotheses: either the competition tooling was updated and the comment was
not, or the blog is ahead of the template. Reading cannot distinguish them; only running
can. The `precheck` job answers in one run for zero effort — far cheaper than guessing.

**Consequence.** If `precheck` rejects 6x4, that is an email to
`asic-competition@janestreet.com`, not a design problem. The area budget (~24K cells)
does not move until the question is settled. Do not size the architecture on the
assumption that 8x4 will land.

---

## ADR-003 — Milestone 1 is disposable by design

**Status:** Accepted · 16 Sep 2026

**Context.** The blog advises: "Start by getting a UART transmitter out of a pin. Then
make it programmable." A fixed UART is the exact opposite of what the competition asks
for.

**Decision.** Write a hard-wired 8N1 UART TX (`src/uart_tx.v`) and document it as
destined for deletion.

**Why.** Three uses, all transitional: validate the RTL → GDS chain end to end, get a
**first real area number** to calibrate everything else against, and later serve as a
**reference model** for testing the UART firmware running on the core.

**Consequence.** The risk is getting attached to it. The header comment in `uart_tx.v`
states plainly that the block must disappear. If a fixed UART is still in the design at
week 10, the project has failed at its primary goal.

---

## ADR-004 — Tests decode the pin, never internal state

**Status:** Accepted · 16 Sep 2026

**Context.** A testbench can either observe the DUT's internal signals or observe only
its pins.

**Decision.** The cocotb tests sample `uo_out` at the midpoint of each bit time, the way
a real receiver would. No access to internal state.

**Why.** After synthesis, gate-level simulation sees only a netlist: internal signal
names are gone. A test written against internal state has to be rewritten at exactly the
moment when there is least time and most need for confidence. A test written against pins
carries over from RTL to netlist unchanged.

**Consequence.** Tests take slightly longer to write. In exchange the whole suite is
reusable at gate level (the CI `gl_test` job) with no modification. This rule applies to
the entire project, not just milestone 1.

---

## ADR-005 — Timing is asserted from day one

**Status:** Accepted · 16 Sep 2026

**Context.** On this project timing precision is not one quality among many: it is the
chip's entire reason to exist. A protocol emulator that drifts by a cycle speaks no
protocol at all.

**Decision.** `test_bit_timing` checks that every bit slot lasts **exactly** `CLK_DIV`
clock cycles, not approximately.

**Why.** Timing drift does not show up in a functional test — the byte still arrives. It
shows up in silicon, against a real peripheral, when it is too late. Writing the
assertion now costs ten lines.

**Consequence.** Every future timing instruction in the core gets the same treatment: an
exact assertion, never a tolerance. This is also the foundation of the verification
argument (ADR-007).

---

## ADR-006 — No shadow register on the UART TX

**Status:** Accepted, local scope · 16 Sep 2026

**Context.** The UART TX ignores `load` while busy. A production UART double-buffers so
frames can go out back to back with no gap.

**Decision.** No double buffer. `load` during `busy` is silently ignored.

**Why.** A shadow register costs 8 flip-flops plus control logic, in a block that is
meant to disappear (ADR-003). On the final chip, frame sequencing will be handled **in
firmware** — that is exactly the kind of policy we want out of the hardware.

**Consequence.** Tests must wait for `busy == 0` between bytes (`wait_idle` helper). This
cost one test failure on the first run — documented in `03-workflow.md`.

---

## ADR-007 — Verification is a deliverable, not a chore

**Status:** **Proposed** — needs Paul's sign-off · 16 Sep 2026

**Context.** The judging criteria name "formal methods, random constrained tests,
AI-assisted verification" and state that verification will be "extremely important" in
the coming ASIC flow.

**Proposed decision.** Build verification as a product in its own right:

1. A cycle-accurate **instruction set simulator (ISS)** in Python, written *before* the
   RTL and serving as an executable specification.
2. A **differential fuzzer**: constrained-random program generation, run in parallel on
   the ISS and the RTL, compared cycle by cycle.
3. **Formal properties** (SymbiYosys) on the timing instructions — e.g. "`WAIT n` always
   releases exactly n cycles later, from any state".

**Why.** This is where the value-to-effort ratio is best for this specific project. It is
software, so it is the ground where Paul is strong and where AI assistance is most
effective — whereas physical timing closure is the ground where both are weakest. And it
is explicitly what the judges said they want to see.

**Consequence.** The ISS becomes the critical path: RTL cannot start before it. This
justifies spending weeks 2–3 on spec and ISS without writing a line of Verilog, which can
feel slow. It is not.

---

## ADR-008 — Clock assumed at 50 MHz

**Status:** **Provisional** — confirm before freezing the ISA · 16 Sep 2026

**Context.** `info.yaml` requires a frequency. The maximum frequency actually achievable
on CMOS5L through Tiny Tapeout is not known at this stage.

**Decision.** 50 MHz, with `CLK_DIV = 434` for 115200 baud.

**Why.** A plausible order of magnitude for a Tiny Tapeout board, and a number was needed
to make progress. Nothing currently contradicts it.

**Consequence — important.** This is the heaviest assumption in the project. The
frequency sets timing resolution, hence maximum bit rate, hence **the feasibility of the
stretch goals** (low-speed USB at 1.5 Mbit/s, 10M Ethernet). It also sets how many cycles
are available per bit to execute firmware — that is, how much complexity the ISA can
afford. **Confirm before freezing the ISA**, not after.

---

## ADR-009 — Novelty axis: listen, don't just talk

**Status:** **Proposed** — needs Paul's sign-off · 16 Sep 2026

**Context.** Criterion #1 is unique functionality. The explicit references (RP2040 PIO,
Sitara PRU) define the state of the art: rebuilding a smaller PIO is the default path,
and therefore the least remarkable one.

**Proposed decision.** Don't just **transmit** protocols — **sniff and auto-identify**
them: timestamped edge capture, automatic baud detection, on-the-fly UART/SPI/I2C
classification.

**Why.** Jane Street states their use case is "hardware debugging and reverse
engineering". A chip that identifies an unknown protocol on a bus answers that stated
need, and neither PIO nor PRU does it. It also reuses exactly the primitives emulation
already requires (read pins, count cycles) — so it is marginal area cost, not a second
subsystem.

**Consequence.** Must be settled **during** ISA design, not after: if sniffing is adopted,
the ISA needs a temporal capture primitive (edge timestamping) that cannot be bolted on
later without starting over.

---

## ADR-010 — Internal docs in French, code and public docs in English

**Status:** **Superseded by [ADR-011](#adr-011--everything-in-english)** · 16 Sep 2026

**Context.** Paul works in French. The repo is public and will be read by
English-speaking judges, and a second contributor might join.

**Decision.** `context/` in French; code, comments, commit messages, `docs/info.md` and
the final write-up in English.

**Why.** `context/` is for steering the project and its primary reader was Paul.
Everything judged or read by third parties is in English.

**Superseded because** Paul opted for English throughout the same day. See ADR-011.

---

## ADR-011 — Everything in English

**Status:** Accepted · 16 Sep 2026

**Context.** ADR-010 split the repo between French internal docs and English public ones.
Paul confirmed he is comfortable reading English documentation.

**Decision.** The entire repository is in English, `context/` included.

**Why.** A single language removes the judgement call, on every new file, of which side
of the line it falls. The repo is public and open source from day one; teams are strongly
recommended, so an incoming contributor is a realistic scenario and English maximises who
can join. It also means `context/` can be linked to directly from the final write-up
without translation — and the decision log is itself evidence of methodology, which is a
judged criterion.

**Consequence.** Spoken exchanges with Paul stay in French; the written artefacts do not.
