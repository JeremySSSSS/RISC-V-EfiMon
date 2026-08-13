#!/usr/bin/env bash
# Prepara los programas de calibracion nuevos para caracterizar.
# Correr EN EL BANCO (necesita OpenOCD en :3333 para el paso gen_duty).
set -e
HERE=$(dirname "$(readlink -f "$0")")

echo "== 1/3  make bucles (ctrl.S nuevo + 7 fp) =="
make -C "$HERE/bucles/fuentes" all

echo "== 2/3  make regresion (5 nuevos + set viejo) =="
make -C "$HERE/regresion/fuentes" all

echo "== 3/3  gen_duty: variantes _d60/_d30 de los 5 nuevos (mide por JTAG) =="
cd "$HERE/regresion/fuentes"
python3 gen_duty.py wmac fir ratscale modmul memfill mulhstream

echo "LISTO. Ahora podes correr:"
echo "  python3 characterize.py loops        # ctrl nuevo"
echo "  python3 characterize.py regression   # con los 5 nuevos"
