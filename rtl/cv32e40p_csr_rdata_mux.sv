// Selects the data returned by the standard CSR block or the category bank.

module cv32e40p_csr_rdata_mux (
    input  logic        category_hit_i,
    input  logic [31:0] category_rdata_i,
    input  logic [31:0] standard_rdata_i,
    output logic [31:0] rdata_o
);

  always_comb begin
    rdata_o = category_hit_i ? category_rdata_i : standard_rdata_i;
  end

endmodule
