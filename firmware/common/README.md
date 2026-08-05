# common — shared bench modules

- `jtag.py` — loads and runs an ELF on the CV32E40P via OpenOCD (FT232H):
  starts the program, waits for retirement, reads the classifier CSRs and
  computes the expected measurement-window duration for the pairing guard with
  the ESP32.
- `sheet.py` — I/O with the spreadsheet through the Apps Script Web App.
  `Inbox.get_pavg()` waits for the power window the ESP32 posts and discards old
  rows whose duration does not match the expected one (avoids misaligning the batch).
- `model.py` — the estimation model: `E = P_static·T + Σ e_i·n_i`, reading and
  writing `coefficients.csv`.
- `pulp_temp.h` — reads the die temperature (XADC) from firmware (see `../../fpga/`).
- `appscript_google_sheet.gs` — the spreadsheet's Apps Script backend (deployed
  as a Web App; its /exec URL goes in `config_local.py`).

## Local configuration (required)

`config_local.py` holds the real Web App URL and is **not versioned**. To set up
the bench on a new machine:

```
cp config_local.py.example config_local.py
# edit SCRIPT_URL with the /exec URL of your own Apps Script deployment
```
