# Variantes de ciclo de trabajo (barrido de intensidad estilo EfiMon).
# GENERADO: REPS = trabajo POR TANDA (el harness llama al kernel CHUNKS
# veces); activo ~12s (d60) / ~6s (d30); ventana total ~20 s.
DUTY_ELFS := $(OUT)/crc_d60.elf $(OUT)/crc_d30.elf $(OUT)/dotprod_d60.elf $(OUT)/dotprod_d30.elf $(OUT)/fpoly_d60.elf $(OUT)/fpoly_d30.elf $(OUT)/fsm_d60.elf $(OUT)/fsm_d30.elf $(OUT)/gcd_d60.elf $(OUT)/gcd_d30.elf $(OUT)/histogram_d60.elf $(OUT)/histogram_d30.elf $(OUT)/matmul_d60.elf $(OUT)/matmul_d30.elf $(OUT)/memcpy_d60.elf $(OUT)/memcpy_d30.elf $(OUT)/modpow_d60.elf $(OUT)/modpow_d30.elf $(OUT)/mulhash64_d60.elf $(OUT)/mulhash64_d30.elf $(OUT)/mulhscale_d60.elf $(OUT)/mulhscale_d30.elf $(OUT)/radix_d60.elf $(OUT)/radix_d30.elf $(OUT)/sort_d60.elf $(OUT)/sort_d30.elf $(OUT)/trialdiv_d60.elf $(OUT)/trialdiv_d30.elf $(OUT)/vecscale_d60.elf $(OUT)/vecscale_d30.elf


$(OUT)/crc_d60.elf: harness.S wl_crc.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=976 -DCHUNKS=10 -DSLEEP_TICKS=8000597 -o $@ harness.S wl_crc.c

$(OUT)/crc_d30.elf: harness.S wl_crc.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=488 -DCHUNKS=10 -DSLEEP_TICKS=14001046 -o $@ harness.S wl_crc.c

$(OUT)/dotprod_d60.elf: harness.S wl_dotprod.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=6015 -DCHUNKS=10 -DSLEEP_TICKS=7999952 -o $@ harness.S wl_dotprod.c

$(OUT)/dotprod_d30.elf: harness.S wl_dotprod.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=3008 -DCHUNKS=10 -DSLEEP_TICKS=14002244 -o $@ harness.S wl_dotprod.c

$(OUT)/fpoly_d60.elf: harness.S wl_fpoly.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=6438 -DCHUNKS=10 -DSLEEP_TICKS=8000288 -o $@ harness.S wl_fpoly.c

$(OUT)/fpoly_d30.elf: harness.S wl_fpoly.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=3219 -DCHUNKS=10 -DSLEEP_TICKS=14000505 -o $@ harness.S wl_fpoly.c

$(OUT)/fsm_d60.elf: harness.S wl_fsm.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1509 -DCHUNKS=10 -DSLEEP_TICKS=8000756 -o $@ harness.S wl_fsm.c

$(OUT)/fsm_d30.elf: harness.S wl_fsm.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=754 -DCHUNKS=10 -DSLEEP_TICKS=13992044 -o $@ harness.S wl_fsm.c

$(OUT)/gcd_d60.elf: harness.S wl_gcd.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=696 -DCHUNKS=10 -DSLEEP_TICKS=8001531 -o $@ harness.S wl_gcd.c

$(OUT)/gcd_d30.elf: harness.S wl_gcd.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=348 -DCHUNKS=10 -DSLEEP_TICKS=14002679 -o $@ harness.S wl_gcd.c

$(OUT)/histogram_d60.elf: harness.S wl_histogram.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1548 -DCHUNKS=10 -DSLEEP_TICKS=7999032 -o $@ harness.S wl_histogram.c

$(OUT)/histogram_d30.elf: harness.S wl_histogram.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=774 -DCHUNKS=10 -DSLEEP_TICKS=13998306 -o $@ harness.S wl_histogram.c

$(OUT)/matmul_d60.elf: harness.S wl_matmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=404 -DCHUNKS=10 -DSLEEP_TICKS=8009166 -o $@ harness.S wl_matmul.c

$(OUT)/matmul_d30.elf: harness.S wl_matmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=202 -DCHUNKS=10 -DSLEEP_TICKS=14016042 -o $@ harness.S wl_matmul.c

$(OUT)/memcpy_d60.elf: harness.S wl_memcpy.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=2795 -DCHUNKS=10 -DSLEEP_TICKS=8001153 -o $@ harness.S wl_memcpy.c

$(OUT)/memcpy_d30.elf: harness.S wl_memcpy.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1397 -DCHUNKS=10 -DSLEEP_TICKS=13997009 -o $@ harness.S wl_memcpy.c

$(OUT)/modpow_d60.elf: harness.S wl_modpow.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=2195 -DCHUNKS=10 -DSLEEP_TICKS=8001019 -o $@ harness.S wl_modpow.c

$(OUT)/modpow_d30.elf: harness.S wl_modpow.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1097 -DCHUNKS=10 -DSLEEP_TICKS=13995405 -o $@ harness.S wl_modpow.c

$(OUT)/mulhash64_d60.elf: harness.S wl_mulhash64.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=5639 -DCHUNKS=10 -DSLEEP_TICKS=7999863 -o $@ harness.S wl_mulhash64.c

$(OUT)/mulhash64_d30.elf: harness.S wl_mulhash64.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=2820 -DCHUNKS=10 -DSLEEP_TICKS=14002243 -o $@ harness.S wl_mulhash64.c

$(OUT)/mulhscale_d60.elf: harness.S wl_mulhscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=16086 -DCHUNKS=10 -DSLEEP_TICKS=8000106 -o $@ harness.S wl_mulhscale.c

$(OUT)/mulhscale_d30.elf: harness.S wl_mulhscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=8043 -DCHUNKS=10 -DSLEEP_TICKS=14000186 -o $@ harness.S wl_mulhscale.c

$(OUT)/radix_d60.elf: harness.S wl_radix.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1712 -DCHUNKS=10 -DSLEEP_TICKS=8001888 -o $@ harness.S wl_radix.c

$(OUT)/radix_d30.elf: harness.S wl_radix.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=856 -DCHUNKS=10 -DSLEEP_TICKS=14003305 -o $@ harness.S wl_radix.c

$(OUT)/sort_d60.elf: harness.S wl_sort.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1569 -DCHUNKS=10 -DSLEEP_TICKS=7998601 -o $@ harness.S wl_sort.c

$(OUT)/sort_d30.elf: harness.S wl_sort.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=785 -DCHUNKS=10 -DSLEEP_TICKS=14006473 -o $@ harness.S wl_sort.c

$(OUT)/trialdiv_d60.elf: harness.S wl_trialdiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1820 -DCHUNKS=10 -DSLEEP_TICKS=7998223 -o $@ harness.S wl_trialdiv.c

$(OUT)/trialdiv_d30.elf: harness.S wl_trialdiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=910 -DCHUNKS=10 -DSLEEP_TICKS=13996890 -o $@ harness.S wl_trialdiv.c

$(OUT)/vecscale_d60.elf: harness.S wl_vecscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=7772 -DCHUNKS=10 -DSLEEP_TICKS=7999979 -o $@ harness.S wl_vecscale.c

$(OUT)/vecscale_d30.elf: harness.S wl_vecscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=3886 -DCHUNKS=10 -DSLEEP_TICKS=13999963 -o $@ harness.S wl_vecscale.c

