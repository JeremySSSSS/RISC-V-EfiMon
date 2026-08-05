# Data — characterization and validation

Measurement data used to characterize the classifier's energy coefficients
(CV32E40P / PULPissimo on Nexys A7) and to validate the model on BEEBS
kernels. Power in W, time in s, temperature in °C.

## `characterization/`

- `regression/` — Method 2 (NNLS regression, EfiMon-style, intensity sweep):
  calibration measurements, fitted `coefficients.csv`, and per-campaign backups.
- `loops/` — Method 1 (category-dominated loops): loop measurements, fitted
  coefficients, and per-campaign backups.
- `thermal/` — idle power vs. die temperature (forced-air sweep).

## `validation/`

Runs on held-out BEEBS kernels (disjoint from calibration). Three batches from
the same (thermal-plateau) campaign, each provided with both predictions over the
same measured runs: `validation_regression_measure_*.csv` (method 2 in `P_pred_W`)
and `validation_loops_measure_*.csv` (method 1). Since the counters are identical
and only the coefficients change, the measured power is the same in both and the
comparison isolates the model difference.
