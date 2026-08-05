#!/usr/bin/env bash
# Prepares the new calibration programs for characterization.
# Run ON THE BENCH (the gen_duty step needs OpenOCD on :3333).
set -e
HERE=$(dirname "$(readlink -f "$0")")

echo "== 1/3  make loops (new ctrl.S + 7 fp) =="
make -C "$HERE/loops/sources" all

echo "== 2/3  make regression (5 new + old set) =="
make -C "$HERE/regression/sources" all

echo "== 3/3  gen_duty: _d60/_d30 variants of the 5 new ones (measures over JTAG) =="
cd "$HERE/regression/sources"
python3 gen_duty.py wmac fir ratscale modmul memfill mulhstream

echo "DONE. Now run:"
echo "  python3 characterize.py loops        # new ctrl"
echo "  python3 characterize.py regression   # with the 5 new"
