# Variantes de ciclo de trabajo (barrido de intensidad estilo EfiMon).
# GENERADO: REPS = trabajo POR TANDA (el harness llama al kernel CHUNKS
# veces); activo ~12s (d60) / ~6s (d30); ventana total ~20 s.
DUTY_ELFS := $(OUT)/dmul_d60.elf $(OUT)/dmul_d30.elf $(OUT)/dmulh_d60.elf $(OUT)/dmulh_d30.elf $(OUT)/ddiv_d60.elf $(OUT)/ddiv_d30.elf $(OUT)/dctrl_d60.elf $(OUT)/dctrl_d30.elf $(OUT)/crc_d60.elf $(OUT)/crc_d30.elf $(OUT)/dotprod_d60.elf $(OUT)/dotprod_d30.elf $(OUT)/fpoly_d60.elf $(OUT)/fpoly_d30.elf $(OUT)/fsm_d60.elf $(OUT)/fsm_d30.elf $(OUT)/gcd_d60.elf $(OUT)/gcd_d30.elf $(OUT)/histogram_d60.elf $(OUT)/histogram_d30.elf $(OUT)/matmul_d60.elf $(OUT)/matmul_d30.elf $(OUT)/memcpy_d60.elf $(OUT)/memcpy_d30.elf $(OUT)/modpow_d60.elf $(OUT)/modpow_d30.elf $(OUT)/mulhash64_d60.elf $(OUT)/mulhash64_d30.elf $(OUT)/mulhscale_d60.elf $(OUT)/mulhscale_d30.elf $(OUT)/radix_d60.elf $(OUT)/radix_d30.elf $(OUT)/sort_d60.elf $(OUT)/sort_d30.elf $(OUT)/trialdiv_d60.elf $(OUT)/trialdiv_d30.elf $(OUT)/vecscale_d60.elf $(OUT)/vecscale_d30.elf


$(OUT)/crc_d60.elf: harness.S wl_crc.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=586 -DCHUNKS=10 -DSLEEP_TICKS=4800358 -o $@ harness.S wl_crc.c

$(OUT)/crc_d30.elf: harness.S wl_crc.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=293 -DCHUNKS=10 -DSLEEP_TICKS=8400628 -o $@ harness.S wl_crc.c

$(OUT)/dotprod_d60.elf: harness.S wl_dotprod.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=3609 -DCHUNKS=10 -DSLEEP_TICKS=4799971 -o $@ harness.S wl_dotprod.c

$(OUT)/dotprod_d30.elf: harness.S wl_dotprod.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=1805 -DCHUNKS=10 -DSLEEP_TICKS=8401346 -o $@ harness.S wl_dotprod.c

$(OUT)/fpoly_d60.elf: harness.S wl_fpoly.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=3863 -DCHUNKS=10 -DSLEEP_TICKS=4800173 -o $@ harness.S wl_fpoly.c

$(OUT)/fpoly_d30.elf: harness.S wl_fpoly.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=1931 -DCHUNKS=10 -DSLEEP_TICKS=8400303 -o $@ harness.S wl_fpoly.c

$(OUT)/fsm_d60.elf: harness.S wl_fsm.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=905 -DCHUNKS=10 -DSLEEP_TICKS=4800454 -o $@ harness.S wl_fsm.c

$(OUT)/fsm_d30.elf: harness.S wl_fsm.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=452 -DCHUNKS=10 -DSLEEP_TICKS=8395226 -o $@ harness.S wl_fsm.c

$(OUT)/gcd_d60.elf: harness.S wl_gcd.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=418 -DCHUNKS=10 -DSLEEP_TICKS=4800919 -o $@ harness.S wl_gcd.c

$(OUT)/gcd_d30.elf: harness.S wl_gcd.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=209 -DCHUNKS=10 -DSLEEP_TICKS=8401607 -o $@ harness.S wl_gcd.c

$(OUT)/histogram_d60.elf: harness.S wl_histogram.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=929 -DCHUNKS=10 -DSLEEP_TICKS=4799419 -o $@ harness.S wl_histogram.c

$(OUT)/histogram_d30.elf: harness.S wl_histogram.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=464 -DCHUNKS=10 -DSLEEP_TICKS=8398984 -o $@ harness.S wl_histogram.c

$(OUT)/matmul_d60.elf: harness.S wl_matmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=242 -DCHUNKS=10 -DSLEEP_TICKS=4805500 -o $@ harness.S wl_matmul.c

$(OUT)/matmul_d30.elf: harness.S wl_matmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=121 -DCHUNKS=10 -DSLEEP_TICKS=8409625 -o $@ harness.S wl_matmul.c

$(OUT)/memcpy_d60.elf: harness.S wl_memcpy.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1677 -DCHUNKS=10 -DSLEEP_TICKS=4800692 -o $@ harness.S wl_memcpy.c

$(OUT)/memcpy_d30.elf: harness.S wl_memcpy.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=838 -DCHUNKS=10 -DSLEEP_TICKS=8398205 -o $@ harness.S wl_memcpy.c

$(OUT)/modpow_d60.elf: harness.S wl_modpow.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1317 -DCHUNKS=10 -DSLEEP_TICKS=4800611 -o $@ harness.S wl_modpow.c

$(OUT)/modpow_d30.elf: harness.S wl_modpow.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=658 -DCHUNKS=10 -DSLEEP_TICKS=8397243 -o $@ harness.S wl_modpow.c

$(OUT)/mulhash64_d60.elf: harness.S wl_mulhash64.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=3383 -DCHUNKS=10 -DSLEEP_TICKS=4799918 -o $@ harness.S wl_mulhash64.c

$(OUT)/mulhash64_d30.elf: harness.S wl_mulhash64.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1692 -DCHUNKS=10 -DSLEEP_TICKS=8401346 -o $@ harness.S wl_mulhash64.c

$(OUT)/mulhscale_d60.elf: harness.S wl_mulhscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=9652 -DCHUNKS=10 -DSLEEP_TICKS=4800064 -o $@ harness.S wl_mulhscale.c

$(OUT)/mulhscale_d30.elf: harness.S wl_mulhscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=4826 -DCHUNKS=10 -DSLEEP_TICKS=8400112 -o $@ harness.S wl_mulhscale.c

$(OUT)/radix_d60.elf: harness.S wl_radix.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1027 -DCHUNKS=10 -DSLEEP_TICKS=4801133 -o $@ harness.S wl_radix.c

$(OUT)/radix_d30.elf: harness.S wl_radix.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=514 -DCHUNKS=10 -DSLEEP_TICKS=8401983 -o $@ harness.S wl_radix.c

$(OUT)/sort_d60.elf: harness.S wl_sort.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=941 -DCHUNKS=10 -DSLEEP_TICKS=4799161 -o $@ harness.S wl_sort.c

$(OUT)/sort_d30.elf: harness.S wl_sort.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=471 -DCHUNKS=10 -DSLEEP_TICKS=8403884 -o $@ harness.S wl_sort.c

$(OUT)/trialdiv_d60.elf: harness.S wl_trialdiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1092 -DCHUNKS=10 -DSLEEP_TICKS=4798934 -o $@ harness.S wl_trialdiv.c

$(OUT)/trialdiv_d30.elf: harness.S wl_trialdiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=546 -DCHUNKS=10 -DSLEEP_TICKS=8398134 -o $@ harness.S wl_trialdiv.c

$(OUT)/vecscale_d60.elf: harness.S wl_vecscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=4663 -DCHUNKS=10 -DSLEEP_TICKS=4799987 -o $@ harness.S wl_vecscale.c

$(OUT)/vecscale_d30.elf: harness.S wl_vecscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=2332 -DCHUNKS=10 -DSLEEP_TICKS=8399978 -o $@ harness.S wl_vecscale.c


# --- duty de los 6 kernels nuevos (calculado del smoke-test) ---
DUTY_ELFS += $(OUT)/wmac_d60.elf $(OUT)/wmac_d30.elf $(OUT)/fir_d60.elf $(OUT)/fir_d30.elf $(OUT)/ratscale_d60.elf $(OUT)/ratscale_d30.elf $(OUT)/modmul_d60.elf $(OUT)/modmul_d30.elf $(OUT)/memfill_d60.elf $(OUT)/memfill_d30.elf $(OUT)/mulhstream_d60.elf $(OUT)/mulhstream_d30.elf

$(OUT)/wmac_d60.elf: harness.S wl_wmac.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=2540 -DCHUNKS=10 -DSLEEP_TICKS=4800864 -o $@ harness.S wl_wmac.c

$(OUT)/wmac_d30.elf: harness.S wl_wmac.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1270 -DCHUNKS=10 -DSLEEP_TICKS=8401512 -o $@ harness.S wl_wmac.c

$(OUT)/fir_d60.elf: harness.S wl_fir.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1815 -DCHUNKS=10 -DSLEEP_TICKS=4799667 -o $@ harness.S wl_fir.c

$(OUT)/fir_d30.elf: harness.S wl_fir.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=908 -DCHUNKS=10 -DSLEEP_TICKS=8404044 -o $@ harness.S wl_fir.c

$(OUT)/ratscale_d60.elf: harness.S wl_ratscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=953 -DCHUNKS=10 -DSLEEP_TICKS=4800296 -o $@ harness.S wl_ratscale.c

$(OUT)/ratscale_d30.elf: harness.S wl_ratscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=476 -DCHUNKS=10 -DSLEEP_TICKS=8391704 -o $@ harness.S wl_ratscale.c

$(OUT)/modmul_d60.elf: harness.S wl_modmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1634 -DCHUNKS=10 -DSLEEP_TICKS=4801136 -o $@ harness.S wl_modmul.c

$(OUT)/modmul_d30.elf: harness.S wl_modmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=817 -DCHUNKS=10 -DSLEEP_TICKS=8401988 -o $@ harness.S wl_modmul.c

$(OUT)/memfill_d60.elf: harness.S wl_memfill.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=7627 -DCHUNKS=10 -DSLEEP_TICKS=4800069 -o $@ harness.S wl_memfill.c

$(OUT)/memfill_d30.elf: harness.S wl_memfill.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=3813 -DCHUNKS=10 -DSLEEP_TICKS=8399019 -o $@ harness.S wl_memfill.c

$(OUT)/mulhstream_d60.elf: harness.S wl_mulhstream.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=510 -DCHUNKS=10 -DSLEEP_TICKS=4800000 -o $@ harness.S wl_mulhstream.c

$(OUT)/mulhstream_d30.elf: harness.S wl_mulhstream.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=255 -DCHUNKS=10 -DSLEEP_TICKS=8400000 -o $@ harness.S wl_mulhstream.c


# --- duty variants de los kernels DOMINANTES enteros (barrido de intensidad
# para anclar mul/mulh/div/ctrl con 3 puntos c/u). SLEEP estandar 4.8M/8.4M.
$(OUT)/dmul_d60.elf: harness.S wl_dmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1004 -DCHUNKS=10 -DSLEEP_TICKS=4800000 -o $@ harness.S wl_dmul.c
$(OUT)/dmul_d30.elf: harness.S wl_dmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=502 -DCHUNKS=10 -DSLEEP_TICKS=8400000 -o $@ harness.S wl_dmul.c
$(OUT)/dmulh_d60.elf: harness.S wl_dmulh.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=306 -DCHUNKS=10 -DSLEEP_TICKS=4800000 -o $@ harness.S wl_dmulh.c
$(OUT)/dmulh_d30.elf: harness.S wl_dmulh.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=153 -DCHUNKS=10 -DSLEEP_TICKS=8400000 -o $@ harness.S wl_dmulh.c
$(OUT)/ddiv_d60.elf: harness.S wl_ddiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=157 -DCHUNKS=10 -DSLEEP_TICKS=4800000 -o $@ harness.S wl_ddiv.c
$(OUT)/ddiv_d30.elf: harness.S wl_ddiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=78 -DCHUNKS=10 -DSLEEP_TICKS=8400000 -o $@ harness.S wl_ddiv.c
$(OUT)/dctrl_d60.elf: harness.S wl_dctrl.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1260 -DCHUNKS=10 -DSLEEP_TICKS=4800000 -o $@ harness.S wl_dctrl.c
$(OUT)/dctrl_d30.elf: harness.S wl_dctrl.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=630 -DCHUNKS=10 -DSLEEP_TICKS=8400000 -o $@ harness.S wl_dctrl.c
