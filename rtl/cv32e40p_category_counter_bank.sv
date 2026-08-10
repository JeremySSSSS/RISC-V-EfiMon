// Register bank for the instruction-category counters.
//
// Keeping storage and CSR access in a separate module makes the classifier
// purely responsible for deciding which category increments each cycle.

module cv32e40p_category_counter_bank
  import cv32e40p_pkg::*;
(
    input logic clk_i,
    input logic rst_ni,

    // inc_i[CAT_DIVCYC] is reserved for a uniform array shape and is not
    // used; DIVCYC has its own cycle increment input below.
    input logic [1:0] inc_i [CATEGORY_COUNT],
    input logic       divcyc_inc_i,

    // n_fetch: cruces de bloque en el fetch a L2 (proxy de switching de fetch).
    input logic        fetch_valid_i,   // fetch a L2 aceptado (req & gnt)
    input logic [31:0] fetch_addr_i,    // su direccion

    input  csr_num_e    csr_addr_i,
    input  csr_opcode_e csr_op_i,
    input  logic [31:0] csr_wdata_i,
    output logic        csr_hit_o,
    output logic [31:0] csr_rdata_o
);

  logic [63:0] counter_q [CATEGORY_COUNT];
  // Rango de direcciones de fetch (min/max) -> footprint del codigo tocado.
  // SW lee range = max - min. Escribir a estos CSR los REINICIA (min=all1s, max=0).
  logic [31:0] fetch_min_q, fetch_max_q;

  logic csr_write;

  always_comb begin
    csr_hit_o   = 1'b1;
    csr_rdata_o = 32'h0;

    unique case (csr_addr_i)
      CSR_CAT_ALU_LO:        csr_rdata_o = counter_q[CAT_ALU][31:0];
      CSR_CAT_ALU_HI:        csr_rdata_o = counter_q[CAT_ALU][63:32];
      CSR_CAT_MUL_LO:        csr_rdata_o = counter_q[CAT_MUL][31:0];
      CSR_CAT_MUL_HI:        csr_rdata_o = counter_q[CAT_MUL][63:32];
      CSR_CAT_MULH_LO:       csr_rdata_o = counter_q[CAT_MULH][31:0];
      CSR_CAT_MULH_HI:       csr_rdata_o = counter_q[CAT_MULH][63:32];
      CSR_CAT_DIV_LO:        csr_rdata_o = counter_q[CAT_DIV][31:0];
      CSR_CAT_DIV_HI:        csr_rdata_o = counter_q[CAT_DIV][63:32];
      CSR_CAT_MEM_LO:        csr_rdata_o = counter_q[CAT_MEM][31:0];
      CSR_CAT_MEM_HI:        csr_rdata_o = counter_q[CAT_MEM][63:32];
      CSR_CAT_CTRL_LO:       csr_rdata_o = counter_q[CAT_CTRL][31:0];
      CSR_CAT_CTRL_HI:       csr_rdata_o = counter_q[CAT_CTRL][63:32];
      CSR_CAT_FP_ADD_LO:     csr_rdata_o = counter_q[CAT_FP_ADD][31:0];
      CSR_CAT_FP_ADD_HI:     csr_rdata_o = counter_q[CAT_FP_ADD][63:32];
      CSR_CAT_FP_MUL_LO:     csr_rdata_o = counter_q[CAT_FP_MUL][31:0];
      CSR_CAT_FP_MUL_HI:     csr_rdata_o = counter_q[CAT_FP_MUL][63:32];
      CSR_CAT_FP_FMA_LO:     csr_rdata_o = counter_q[CAT_FP_FMA][31:0];
      CSR_CAT_FP_FMA_HI:     csr_rdata_o = counter_q[CAT_FP_FMA][63:32];
      CSR_CAT_FP_DIV_LO:     csr_rdata_o = counter_q[CAT_FP_DIV][31:0];
      CSR_CAT_FP_DIV_HI:     csr_rdata_o = counter_q[CAT_FP_DIV][63:32];
      CSR_CAT_FP_SQRT_LO:    csr_rdata_o = counter_q[CAT_FP_SQRT][31:0];
      CSR_CAT_FP_SQRT_HI:    csr_rdata_o = counter_q[CAT_FP_SQRT][63:32];
      CSR_CAT_FP_NONCOMP_LO: csr_rdata_o = counter_q[CAT_FP_NONCOMP][31:0];
      CSR_CAT_FP_NONCOMP_HI: csr_rdata_o = counter_q[CAT_FP_NONCOMP][63:32];
      CSR_CAT_FP_CONV_LO:    csr_rdata_o = counter_q[CAT_FP_CONV][31:0];
      CSR_CAT_FP_CONV_HI:    csr_rdata_o = counter_q[CAT_FP_CONV][63:32];
      CSR_CAT_DIVCYC_LO:     csr_rdata_o = counter_q[CAT_DIVCYC][31:0];
      CSR_CAT_DIVCYC_HI:     csr_rdata_o = counter_q[CAT_DIVCYC][63:32];
      CSR_CAT_FETCH_LO:      csr_rdata_o = fetch_min_q;
      CSR_CAT_FETCH_HI:      csr_rdata_o = fetch_max_q;
      default: begin
        csr_hit_o   = 1'b0;
        csr_rdata_o = 32'h0;
      end
    endcase
  end

  assign csr_write = csr_hit_o && (csr_op_i != CSR_OP_READ);

  always_ff @(posedge clk_i, negedge rst_ni) begin
    if (!rst_ni) begin
      for (int i = 0; i < CATEGORY_COUNT; i++) begin
        counter_q[i] <= 64'h0;
      end
      fetch_min_q <= 32'hFFFFFFFF;
      fetch_max_q <= 32'h0;
    end else begin
      for (int i = 0; i < CAT_DIVCYC; i++) begin
        counter_q[i] <= counter_q[i] + {{62{1'b0}}, inc_i[i]};
      end
      counter_q[CAT_DIVCYC] <= counter_q[CAT_DIVCYC] + {{63{1'b0}}, divcyc_inc_i};
      if (fetch_valid_i) begin
        if (fetch_addr_i < fetch_min_q) fetch_min_q <= fetch_addr_i;
        if (fetch_addr_i > fetch_max_q) fetch_max_q <= fetch_addr_i;
      end

      if (csr_write) begin
        unique case (csr_addr_i)
          CSR_CAT_ALU_LO:        counter_q[CAT_ALU][31:0]        <= csr_wdata_i;
          CSR_CAT_ALU_HI:        counter_q[CAT_ALU][63:32]       <= csr_wdata_i;
          CSR_CAT_MUL_LO:        counter_q[CAT_MUL][31:0]        <= csr_wdata_i;
          CSR_CAT_MUL_HI:        counter_q[CAT_MUL][63:32]       <= csr_wdata_i;
          CSR_CAT_MULH_LO:       counter_q[CAT_MULH][31:0]       <= csr_wdata_i;
          CSR_CAT_MULH_HI:       counter_q[CAT_MULH][63:32]      <= csr_wdata_i;
          CSR_CAT_DIV_LO:        counter_q[CAT_DIV][31:0]        <= csr_wdata_i;
          CSR_CAT_DIV_HI:        counter_q[CAT_DIV][63:32]       <= csr_wdata_i;
          CSR_CAT_MEM_LO:        counter_q[CAT_MEM][31:0]        <= csr_wdata_i;
          CSR_CAT_MEM_HI:        counter_q[CAT_MEM][63:32]       <= csr_wdata_i;
          CSR_CAT_CTRL_LO:       counter_q[CAT_CTRL][31:0]       <= csr_wdata_i;
          CSR_CAT_CTRL_HI:       counter_q[CAT_CTRL][63:32]      <= csr_wdata_i;
          CSR_CAT_FP_ADD_LO:     counter_q[CAT_FP_ADD][31:0]     <= csr_wdata_i;
          CSR_CAT_FP_ADD_HI:     counter_q[CAT_FP_ADD][63:32]    <= csr_wdata_i;
          CSR_CAT_FP_MUL_LO:     counter_q[CAT_FP_MUL][31:0]     <= csr_wdata_i;
          CSR_CAT_FP_MUL_HI:     counter_q[CAT_FP_MUL][63:32]    <= csr_wdata_i;
          CSR_CAT_FP_FMA_LO:     counter_q[CAT_FP_FMA][31:0]     <= csr_wdata_i;
          CSR_CAT_FP_FMA_HI:     counter_q[CAT_FP_FMA][63:32]    <= csr_wdata_i;
          CSR_CAT_FP_DIV_LO:     counter_q[CAT_FP_DIV][31:0]     <= csr_wdata_i;
          CSR_CAT_FP_DIV_HI:     counter_q[CAT_FP_DIV][63:32]    <= csr_wdata_i;
          CSR_CAT_FP_SQRT_LO:    counter_q[CAT_FP_SQRT][31:0]    <= csr_wdata_i;
          CSR_CAT_FP_SQRT_HI:    counter_q[CAT_FP_SQRT][63:32]   <= csr_wdata_i;
          CSR_CAT_FP_NONCOMP_LO: counter_q[CAT_FP_NONCOMP][31:0] <= csr_wdata_i;
          CSR_CAT_FP_NONCOMP_HI: counter_q[CAT_FP_NONCOMP][63:32] <= csr_wdata_i;
          CSR_CAT_FP_CONV_LO:    counter_q[CAT_FP_CONV][31:0]    <= csr_wdata_i;
          CSR_CAT_FP_CONV_HI:    counter_q[CAT_FP_CONV][63:32]   <= csr_wdata_i;
          CSR_CAT_DIVCYC_LO:     counter_q[CAT_DIVCYC][31:0]     <= csr_wdata_i;
          CSR_CAT_DIVCYC_HI:     counter_q[CAT_DIVCYC][63:32]    <= csr_wdata_i;
          CSR_CAT_FETCH_LO:      fetch_min_q <= 32'hFFFFFFFF;  // write => reset
          CSR_CAT_FETCH_HI:      fetch_max_q <= 32'h0;
          default: ;
        endcase
      end
    end
  end

endmodule
