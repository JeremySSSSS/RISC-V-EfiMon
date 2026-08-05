# loops — method M1 (dominated loops)

Method M1 programs: assembly microbenchmarks where a single category dominates
retirement, so that category's energy coefficient is solved directly from the
measured power, without regression.

- `sources/` — one category-dominated loop per category (`alu`, `mul`, `mulh`,
  `div`, `mem`, `ctrl` and the seven floating-point ones `fp_add`, `fp_mul`,
  `fp_fma`, `fp_div`, `fp_sqrt`, `fp_noncomp`, `fp_conv`), plus `idle`, with its
  Makefile.

Run with `python3 ../characterize.py loops` or from the GUI. The measurements it
produces (`data.csv`, `coefficients.csv`, per-campaign backups) go to the
top-level `../../data/` folder.
