# Energy characterization and validation bench

Measurement-bench software: it loads bare-metal programs onto the CV32E40P
over JTAG, reads the classifier CSRs, receives the average power measured by
the ESP32+INA228, and produces the energy coefficients `e_i` and their
validation.

## Entry point

```
python3 gui.py            # web UI at http://localhost:8237
python3 gui.py --lan      # reachable from the local network (phone, etc.)
```

The GUI queues jobs (characterization campaigns and validation batches) and
runs them serially with live output. Everything the GUI does can also be run
from the console with the scripts below.

## Scripts

| Script | Purpose |
|---|---|
| `characterize.py` | Runs a full campaign of one method and fits the coefficients: `characterize.py loops` (M1) or `characterize.py regression --model efimon` (M2; efimon is the project's official model, requested explicitly because the CLI default is `classic`). Each campaign backs up its coefficients in `<method>/campaigns/coefficients_<timestamp>.csv`. |
| `verify.py` | Validates the coefficients against the loads in `benchmarks/`: `verify.py --method 1\|2 <programs...>`. `--pidle archive` (default) uses the static power from calibration; `--pidle measure` measures it on the spot (recommended if ambient temperature changed). `--repeats N` averages N batches. Each batch is stored in `validations/`. |
| `thermal_sweep.py` | Static-power vs. die-temperature sweep (forced-air) — evidence of the thermal dependence documented in the thesis. |

## Layout

- `loops/` (M1) and `regression/` (M2): calibration kernel sources (`sources/`)
  and the helper scripts.
- `benchmarks/`: validation loads, never used for calibration.
- `hw_verification/`: functional check of the classifier against a reference model.

The measurement data these scripts produce (per-method `data.csv`,
`coefficients.csv`, campaigns and validation runs) lives in the top-level
`../data/` folder.

## Requirements

OpenOCD with the FT232H connected to the Nexys A7 (config in
`firmware/openocd-ft232h.cfg`), the ESP32
measuring (see `esp32_ina228/README.md`), and `common/config_local.py` with
the Apps Script URL (see `common/appscript_google_sheet.gs`).
