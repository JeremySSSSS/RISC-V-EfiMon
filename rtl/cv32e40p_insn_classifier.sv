// Classifies retired instructions and produces increments for the counter bank.
// The bank itself is kept in cv32e40p_category_counter_bank.sv.

module cv32e40p_insn_classifier
  import cv32e40p_pkg::*;
(
    input logic clk_i,
    input logic rst_ni,

    input logic        retire_i,
    input logic        load_i,
    input logic        store_i,
    input logic        jump_i,
    input logic        branch_i,
    input logic        branch_taken_i,

    input logic        alu_en_i,
    input alu_opcode_e alu_operator_i,
    input logic        mult_en_i,
    input mul_opcode_e mult_operator_i,
    input logic        apu_en_i,
    input logic [5:0]  apu_op_i,

    input logic        csr_access_i,
    input logic        system_i,

    output logic [1:0] inc_o [CATEGORY_COUNT],
    output logic       divcyc_inc_o
);

  logic memory_insn;
  logic div_op;
  logic is_div;
  logic is_mulh;
  logic is_mul;
  logic count_en;
  logic branch_q1;

  logic fp_add_op;
  logic fp_mul_op;
  logic fp_fma_op;
  logic fp_div_op;
  logic fp_sqrt_op;
  logic fp_noncomp_op;
  logic fp_conv_op;
  logic fp_op_known;

  assign memory_insn = load_i | store_i;
  assign is_div      = alu_en_i && div_op;
  assign is_mulh     = mult_en_i && (mult_operator_i == MUL_H);
  assign is_mul      = mult_en_i && (mult_operator_i != MUL_H);
  assign count_en    = retire_i && !csr_access_i && !system_i;

  always_comb begin
    unique case (alu_operator_i)
      ALU_DIV, ALU_DIVU, ALU_REM, ALU_REMU: div_op = 1'b1;
      default:                              div_op = 1'b0;
    endcase
  end

  // apu_op_i is {vector, modifier, FPnew operation}; the low four bits are
  // the operation enum used by FPnew.
  always_comb begin
    fp_add_op     = 1'b0;
    fp_mul_op     = 1'b0;
    fp_fma_op     = 1'b0;
    fp_div_op     = 1'b0;
    fp_sqrt_op    = 1'b0;
    fp_noncomp_op = 1'b0;
    fp_conv_op    = 1'b0;
    fp_op_known   = 1'b0;

    if (apu_en_i) begin
      unique case (fpnew_pkg::operation_e'(apu_op_i[3:0]))
        fpnew_pkg::ADD: begin
          fp_add_op = 1'b1;
          fp_op_known = 1'b1;
        end
        fpnew_pkg::MUL: begin
          fp_mul_op = 1'b1;
          fp_op_known = 1'b1;
        end
        fpnew_pkg::FMADD, fpnew_pkg::FNMSUB: begin
          fp_fma_op = 1'b1;
          fp_op_known = 1'b1;
        end
        fpnew_pkg::DIV: begin
          fp_div_op = 1'b1;
          fp_op_known = 1'b1;
        end
        fpnew_pkg::SQRT: begin
          fp_sqrt_op = 1'b1;
          fp_op_known = 1'b1;
        end
        fpnew_pkg::SGNJ, fpnew_pkg::MINMAX,
        fpnew_pkg::CMP, fpnew_pkg::CLASSIFY: begin
          fp_noncomp_op = 1'b1;
          fp_op_known = 1'b1;
        end
        fpnew_pkg::F2F, fpnew_pkg::F2I,
        fpnew_pkg::I2F, fpnew_pkg::CPKAB,
        fpnew_pkg::CPKCD: begin
          fp_conv_op = 1'b1;
          fp_op_known = 1'b1;
        end
        default: begin
          // Keep the retired-instruction invariant for an unexpected APU op.
          fp_noncomp_op = 1'b1;
        end
      endcase
    end
  end

`ifndef SYNTHESIS
  always_ff @(posedge clk_i) begin
    if (rst_ni && count_en && apu_en_i) begin
      assert (fp_op_known)
          else $error("Unknown FPnew operation 0x%h", apu_op_i[3:0]);
    end
  end
`endif

  // Branch resolution arrives one cycle after the branch in EX.
  logic taken_inc;
  logic not_taken_inc;
  assign taken_inc     = branch_taken_i;
  assign not_taken_inc = branch_q1 && !branch_taken_i;

  always_comb begin
    for (int i = 0; i < CATEGORY_COUNT; i++) begin
      inc_o[i] = 2'd0;
    end

    if (count_en) begin
      if (memory_insn) begin
        inc_o[CAT_MEM] = 2'd1;
      end else if (branch_i) begin
        // Assigned on the following cycle as taken or not taken.
      end else if (jump_i) begin
        inc_o[CAT_CTRL] = 2'd1;
      end else if (apu_en_i) begin
        inc_o[CAT_FP_ADD]     = fp_add_op     ? 2'd1 : 2'd0;
        inc_o[CAT_FP_MUL]     = fp_mul_op     ? 2'd1 : 2'd0;
        inc_o[CAT_FP_FMA]     = fp_fma_op     ? 2'd1 : 2'd0;
        inc_o[CAT_FP_DIV]     = fp_div_op     ? 2'd1 : 2'd0;
        inc_o[CAT_FP_SQRT]    = fp_sqrt_op    ? 2'd1 : 2'd0;
        inc_o[CAT_FP_NONCOMP] = fp_noncomp_op ? 2'd1 : 2'd0;
        inc_o[CAT_FP_CONV]    = fp_conv_op    ? 2'd1 : 2'd0;
      end else if (is_div) begin
        inc_o[CAT_DIV] = 2'd1;
      end else if (is_mulh) begin
        inc_o[CAT_MULH] = 2'd1;
      end else if (is_mul) begin
        inc_o[CAT_MUL] = 2'd1;
      end else if (alu_en_i) begin
        inc_o[CAT_ALU] = 2'd1;
      end
    end

    // The current instruction and the previous branch resolution can both
    // increment ALU/CTRL during the same cycle.
    inc_o[CAT_ALU]  = inc_o[CAT_ALU] + not_taken_inc;
    inc_o[CAT_CTRL] = inc_o[CAT_CTRL] + taken_inc;
  end

  assign divcyc_inc_o = is_div;

  always_ff @(posedge clk_i, negedge rst_ni) begin
    if (!rst_ni) begin
      branch_q1 <= 1'b0;
    end else begin
      branch_q1 <= count_en && branch_i;
    end
  end

endmodule
