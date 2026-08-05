/* Conversion RGB -> luminancia (escala de grises) por pixel, en float:
 * y = 0.299 r + 0.587 g + 0.114 b. Codigo real de imagen, con el MISMO patron
 * por elemento que las cargas float probadas en hardware (ycbcr/vecscale):
 * operandos frescos por pixel, arbol corto de mul/add, sin cadenas seriales
 * largas ni fdiv/fsqrt. Se compila con -ffp-contract=off para que no aparezca
 * fmadd, que esta fuera del conjunto probado de la FPU. */
#ifndef REPS
#define REPS 8000
#endif

#define NPX 1024

static unsigned RGB[NPX];        /* 0x00RRGGBB */
static unsigned char GRIS[NPX];

void run_workload(void) {
  volatile unsigned sink = 0;
  unsigned s = 0xC01234u;
  for (int i = 0; i < NPX; i++) {
    s = s * 1103515245u + 12345u;
    RGB[i] = s & 0xFFFFFFu;
  }
  for (int r = 0; r < REPS; r++) {
    for (int i = 0; i < NPX; i++) {
      unsigned p = RGB[i];
      float fr = (float)((p >> 16) & 255u);
      float fg = (float)((p >> 8)  & 255u);
      float fb = (float)(p & 255u);
      float y = 0.299f * fr + 0.587f * fg + 0.114f * fb;
      GRIS[i] = (unsigned char)(int)y;
    }
    sink += GRIS[(r * 13u) & (NPX - 1)];
    RGB[(r * 7u) & (NPX - 1)] ^= 0x0f0f0fu;
  }
}
