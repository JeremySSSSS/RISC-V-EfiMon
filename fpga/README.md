# fpga — XADC die-temperature integration (Nexys A7)

FPGA-target files that add on-chip die-temperature sensing to the PULPissimo SoC,
used to characterize and correct the thermal drift of the static power.

- `xadc_temp.v` — **new**: reads the Artix-7 XADC on-chip temperature register
  over DRP and latches the 12-bit code. Conversion (Xilinx UG480):
  `T[C] = code * 503.975 / 4096 - 273.15`.
- `pulpissimo.sv` — **modified**: instantiates `xadc_temp` and exposes the
  temperature code through GPIO so the firmware can read it (over JTAG the host
  reads it via GPIO, see `firmware/common/jtag.py` and `firmware/common/pulp_temp.h`).
- `xilinx_pulpissimo.v` — **modified**: FPGA top-level wiring for the XADC.
- `run_batch.tcl` — **modified**: adds `xadc_temp.v` to the Vivado synthesis batch.

The temperature code is exposed on GPIO and read from the host without running a
program (`jtag.leer_temp()`), or alongside a workload's results.

## Bitstreams

- `xilinx_pulpissimo_16csr_xadc.bit` — **the bitstream used for the reported
  results**: 16 CSRs (`0xBC0`–`0xBCF`), 6 integer categories + a single aggregate
  float counter + divider cycles, with the XADC. This is the build that produced
  the characterization/validation data in `../data/`.
- `xilinx_pulpissimo.bit` — the current redesign: 28 CSRs (`0xBC0`–`0xBDB`), 6
  integer + 7 floating-point categories + divider cycles, with the XADC. The
  7-category float split is implemented but not yet characterized (future work).

## Note

`pulpissimo.sv`, `xilinx_pulpissimo.v` and `run_batch.tcl` are modified PULPissimo
files (upstream by the PULP group, Solderpad license); only the XADC additions are
this project's contribution. They need Vivado to synthesize (the XADC is a Xilinx
hard macro).
