/* pulp_temp.h -- lee la temperatura del die (XADC) por GPIO en PULPissimo (TFG).
 *
 * El RTL del top FPGA (xilinx_pulpissimo.v) cablea el codigo de 12 bits del XADC
 * a las entradas GPIO io_19..io_30 (bit 0 -> io_19, bit 11 -> io_30). Aqui el
 * firmware: (1) muxea esos pads a funcion GPIO, (2) los pone como ENTRADA, (3) lee
 * el registro GPIO_IN y extrae los 12 bits, (4) convierte a grados.
 *
 * Conversion XADC on-chip (Xilinx UG480):
 *     T[C] = code * 503.975 / 4096 - 273.15
 *
 * OJO: requiere el bitstream con el XADC integrado (re-sintetizar). Direcciones
 * derivadas del map de PULPissimo; verificar en bring-up.
 */
#ifndef PULP_TEMP_H
#define PULP_TEMP_H
#include <stdint.h>

#define GPIO_EN        (*(volatile uint32_t *)0x1A101080u)  /* gpio IP: EN = 0x80, bit/pin */
#define GPIO_MODE1     (*(volatile uint32_t *)0x1A10100Cu)  /* modo pines 16-31, 2 bits/pin */
#define GPIO_IN        (*(volatile uint32_t *)0x1A101100u)  /* gpio IP: IN = 0x100 */

#define TEMP_IO_LO     19            /* io_19 = bit 0 del codigo */
#define TEMP_IO_HI     30            /* io_30 = bit 11 */

/* Como la temperatura se inyecta en s_gpio_in (RTL), NO hace falta configurar los
 * pads. Pero el gpio IP solo refleja un pin en GPIO_IN si gpio_en[pin]=1 Y el
 * modo del pin = 0 (input) -> hay que HABILITAR los pines 19..30 y ponerlos input. */
static inline void temp_init(void) {
  /* modo INPUT (00) para pines 19..30 en MODE1 (pines 16-31, 2 bits/pin) */
  uint32_t m = GPIO_MODE1;
  for (int io = TEMP_IO_LO; io <= TEMP_IO_HI; io++)
    m &= ~(3u << (2 * (io - 16)));
  GPIO_MODE1 = m;
  /* habilita los pines 19..30 (1 bit por pin en GPIO_EN) */
  GPIO_EN |= (0xFFFu << TEMP_IO_LO);
}

/* Devuelve el codigo crudo de 12 bits (0..4095). */
static inline uint32_t temp_read_code(void) {
  return (GPIO_IN >> TEMP_IO_LO) & 0xFFFu;
}

/* Temperatura en grados C x 100 (entero, sin float): (code*503975/4096 - 27315). */
static inline int32_t temp_read_centiC(void) {
  uint32_t code = temp_read_code();
  return (int32_t)((code * 50397ull) / 4096) - 27315;   /* ~centi-grados */
}

#endif /* PULP_TEMP_H */
