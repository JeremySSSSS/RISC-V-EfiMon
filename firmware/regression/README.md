# regression — method M2 (EfiMon-style regression)

Method M2 programs: 15 calibration programs with varied category mixes, each run
at three intensities (100/60/30 % duty cycle by inserting idle windows), and a
non-negative least-squares (NNLS) fit of the coefficients with an intercept over
the total power. Each campaign's idle runs anchor the intercept (static power).

- `sources/` — the 15 calibration programs and their duty variants
  (`duty_variants.mk`).
- `gen_duty.py` — generates a new duty variant: measures the program's base
  mcycle over JTAG, computes `REPS`/`SLEEP_TICKS` for the requested intensity and
  appends the rule to the Makefile.

Run with `python3 ../characterize.py regression --model efimon` or from the GUI
(which already passes the official model; the CLI default is `clasico`). The
measurements it produces go to the top-level `../../data/` folder.
