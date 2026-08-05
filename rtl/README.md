# rtl — instruction classifier (CV32E40P)

Only the RTL files this project **created or modified** to add the per-category
instruction classifier to the CV32E40P core. The rest of the CV32E40P and its
dependencies are OpenHW Group upstream (Apache-2.0 / SHL); these files keep their
original license headers.

## New modules

- `cv32e40p_insn_classifier.sv` — the classifier. At each instruction
  **retirement** it reads the EX-stage operation signals, maps the instruction to
  one category, and drives the counter bank. Detects 6 integer categories
  (`alu`, `mul`, `mulh`, `div`, `mem`, `ctrl`) and 7 floating-point categories
  (`fp_add`, `fp_mul`, `fp_fma`, `fp_div`, `fp_sqrt`, `fp_noncomp`, `fp_conv`) from
  the fpnew operation code.
- `cv32e40p_category_counter_bank.sv` — 14 × 64-bit counters (13 categories +
  divider-busy cycles `c_div`), read back over 28 CSRs at `0xBC0`–`0xBDB`.
- `cv32e40p_csr_rdata_mux.sv` — selects the read data between the standard CSR
  block and the classifier counter bank.

## Modified core files

- `cv32e40p_core.sv` — instantiates the classifier and the read mux, and wires the
  retirement/EX signals.
- `cv32e40p_id_stage.sv`, `cv32e40p_decoder.sv` — expose the operation signals the
  classifier reads.
- `include/cv32e40p_pkg.sv` — classifier parameters and CSR addresses.

Counting is enabled only for retired, non-CSR, non-system instructions, so the
readout accesses do not perturb the histogram.
