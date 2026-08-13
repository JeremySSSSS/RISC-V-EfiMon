/* Test del XADC (TFG): lee la temperatura del die por GPIO y la deja en globales.
 * Requiere el bitstream con el XADC funcionando (DRP con reintento). */
#include "pulp_temp.h"

volatile uint32_t g_temp_code;   /* codigo crudo de 12 bits (0..4095) */
volatile int32_t  g_temp_cC;     /* temperatura en centi-grados (C x 100) */
volatile uint32_t g_count;

void run_workload(void) {
  temp_init();
  for (int n = 0; n < 5000; n++) {
    g_temp_code = temp_read_code();
    g_temp_cC   = temp_read_centiC();
    g_count++;
    for (volatile int i = 0; i < 20000; i++) { }
  }
}
