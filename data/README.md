# Characterization and validation data

Final data of the project: instruction-count-based energy estimation on the
CV32E40P core (PULPissimo / Nexys A7), with two characterization methods.

- **M1 — dominated loops:** one category per loop, isolated against idle.
- **M2 — regression (NNLS):** mixed programs, differential model (base α +
  per-category overhead + stall term), fitted intercept and **mul** as the
  reference; multi-cycle categories folded into per-instruction energy.

## Validation — measured vs. predicted

20 validation runs (held-out loads: BEEBS + custom fp kernels), estimated power
against the power measured by the bench (INA228). The diagonal is the perfect fit.

![Validation M1 vs M2](validacion.png)

| method | RMSE | error (RMSE / P̄) |
|---|---|---|
| **M1** (dominated loops) | 1.43 mW | **0.123 %** |
| **M2** (NNLS regression) | 1.57 mW | **0.135 %** |

The error on total power (~1.17 W, 99 % static) is about 0.12 %; relative to the
**dynamic** component (~22 mW, what the model actually predicts) it is ~5–8 %.

## M1 vs. M2 coefficient comparison

Per-instruction energy of each category, from the two independent methods.

![M1 vs M2 coefficients](coef_barras.png)

Both methods agree on the dominant categories (div ≈ 10.3 / 10.6 nJ, mulh, fp_div,
fp_sqrt), which cross-validates the model: M1 measures them in isolation, M2 solves
for them from real mixed programs, and they land on the same values.

## Layout

```
data/
├── characterization/
│   ├── loops/            # M1: data.csv (raw), campaigns/ (per run), coefficients.csv
│   └── regression/       # M2: same
└── validation/           # 20 runs (M1 + M2)
```

The `.pdf` files (`validacion.pdf`, `coef_barras.pdf`) are the vector versions for
the document.
