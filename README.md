# RISC-V-EfiMon

Hardware instruction classifier integrated into the RISC-V **CV32E40P** core
(**PULPissimo** SoC on a Nexys A7-100T FPGA) to estimate the energy
consumption of bare-metal firmware from per-category retired-instruction
counters exposed through CSRs.

The model instantiates the EfiMon approach with event rates measured in
hardware instead of OS-sampled proportions:

```
P = P_idle + ( Σ e_i · n_i + p_div · c_div ) / T
```

## Layout

```
rtl/        Only the files created or modified by this project
            (the rest of the CV32E40P and its dependencies are OpenHW upstream):
            - cv32e40p_insn_classifier.sv        classifier module (new)
            - cv32e40p_category_counter_bank.sv  64-bit counter bank (new)
            - cv32e40p_csr_rdata_mux.sv          standard/bank CSR read mux (new)
            - cv32e40p_core.sv                   classifier instance and wiring (mod.)
            - cv32e40p_id_stage.sv, _decoder.sv  category signals (mod.)
            - include/cv32e40p_pkg.sv            classifier parameters (mod.)
fpga/       XADC die-temperature integration for the Nexys A7 (SoC/FPGA level):
            xadc_temp.v (new) + modified PULPissimo top-levels and build script.
firmware/   Characterization and validation pipeline
            - common/        model, jtag, sheet, config, pulp_temp.h, appscript
            - loops/         method 1: category-dominated loops (sources/*.S)
            - regression/    method 2: NNLS regression (EfiMon-style) + intensity sweep (sources/wl_*.c)
            - benchmarks/    validation kernels: 9 from BEEBS + gray (own float load)
            - esp32_ina228/  power-meter firmware (ESP32 + INA228)
            - hw_verification/  functional check of the classifier vs. a reference model
            - openocd-ft232h.cfg  JTAG debug config (FT232H)
data/       Measurement data (see data/README.md)
            - characterization/ (regression, loops, thermal) + validation
```

## Classification

Fourteen 64-bit counters: 6 integer categories (`alu`, `mul`, `mulh`,
`div`, `mem`, `ctrl`) + 7 floating-point (`fp_add`, `fp_mul`, `fp_fma`,
`fp_div`, `fp_sqrt`, `fp_noncomp`, `fp_conv`) + one divider-busy cycle
counter (`c_div`). Counting happens at instruction **retirement**, reading
the operands from the EX stage.

## Characterization methods

1. **Dominated loops** — each loop runs ≥95 % of a single category;
   `e_i = (P_cat − P_idle)·T / n`. The divider is measured by cycles (`c_div`).
2. **NNLS regression (EfiMon)** — non-negative fit with intercept over an
   intensity sweep (100/60/30 % duty). Absolute rates `n_i/T` avoid the
   collinearity of proportions.

## Configuration (secrets)

WiFi credentials and the power-meter Apps Script URL are **not** in the
repo. Copy the templates and fill in your own values locally:

```
cp firmware/common/config_local.py.example    firmware/common/config_local.py
cp firmware/esp32_ina228/secrets.h.example    firmware/esp32_ina228/secrets.h
```

## License note

The CV32E40P core belongs to the OpenHW Group (Apache-2.0 / SHL license).
The files under `rtl/` keep their original license headers; this project's
contribution is the classifier and its integration. The kernels under
`firmware/benchmarks/beebs/` come from the BEEBS suite and keep their
license.
