// xadc_temp.v -- Lector de temperatura del die con el XADC del Artix-7 (TFG).
//
// Instancia el primitivo XADC y lee por DRP el registro de temperatura on-chip
// (direccion 0x00) de forma continua, latcheando el codigo de 12 bits en temp_o.
//
// Conversion a grados (Xilinx UG480, sensor on-chip):
//     T[C] = temp_o * 503.975 / 4096 - 273.15
//
// Claves para que ande (depuradas en bring-up):
//  - Reset de ARRANQUE: RESET alto ~256 ciclos tras configurar, luego bajo.
//  - DRP con REINTENTO: si DRDY no llega en 127 ciclos, re-emite DEN (el primer
//    pedido tras el reset se perdia y la FSM quedaba colgada esperando DRDY).
//  - DCLK = reloj de placa (100 MHz); ADCCLK = DCLK/8 (INIT_42=0x0800) < 26 MHz.
//
// OJO: requiere sintesis con Vivado (el XADC es un hard-macro Xilinx).

module xadc_temp (
  input  wire        clk_i,        // DCLK / reloj de la FSM (100 MHz en Nexys)
  input  wire        rst_ni,       // no usado (se usa reset de arranque interno)
  output wire [11:0] temp_o,       // codigo de temperatura de 12 bits
  output wire        valid_o       // 1 tras la primera lectura DRP valida
);

  localparam [6:0] TEMP_ADDR = 7'h00;
  wire [6:0]  daddr = TEMP_ADDR;
  reg         den = 1'b0;
  wire [15:0] do_data;
  wire        drdy;
  wire        eos;
  wire        busy;

  // reset de arranque del XADC (~256 ciclos alto, luego bajo)
  reg [8:0] rst_cnt  = 9'd0;
  reg       xadc_rst = 1'b1;
  always @(posedge clk_i) begin
    if (rst_cnt[8]) xadc_rst <= 1'b0;
    else            rst_cnt  <= rst_cnt + 1'b1;
  end

  // FSM de lectura DRP continua, con TIMEOUT/reintento en la espera de DRDY
  localparam ST_IDLE = 2'd0, ST_REQ = 2'd1, ST_WAIT = 2'd2;
  reg [1:0]  state    = ST_IDLE;
  reg [11:0] temp_raw = 12'd0;
  reg        valid_st = 1'b0;
  reg [6:0]  wcnt     = 7'd0;

  always @(posedge clk_i) begin
    den <= 1'b0;
    case (state)
      ST_IDLE: if (!xadc_rst) state <= ST_REQ;
      ST_REQ: begin den <= 1'b1; wcnt <= 7'd0; state <= ST_WAIT; end
      ST_WAIT: begin
        wcnt <= wcnt + 1'b1;
        if (drdy) begin
          temp_raw <= do_data[15:4];
          valid_st <= 1'b1;
          state    <= ST_REQ;
        end else if (&wcnt) begin     // timeout (127 ciclos) -> reintenta
          state <= ST_REQ;
        end
      end
      default: state <= ST_IDLE;
    endcase
  end

  assign temp_o  = temp_raw;
  assign valid_o = valid_st;

  XADC #(
    .INIT_40(16'h0000), .INIT_41(16'h0000), .INIT_42(16'h0800),
    .INIT_48(16'h0100), .INIT_49(16'h0000),
    .INIT_4A(16'h0000), .INIT_4B(16'h0000), .INIT_4C(16'h0000),
    .INIT_4D(16'h0000), .INIT_4E(16'h0000), .INIT_4F(16'h0000),
    .SIM_MONITOR_FILE("design.txt")
  ) i_xadc (
    .DCLK(clk_i), .RESET(xadc_rst),
    .DADDR(daddr), .DEN(den), .DI(16'h0000), .DWE(1'b0),
    .DO(do_data), .DRDY(drdy),
    .CONVST(1'b0), .CONVSTCLK(1'b0),
    .VP(1'b0), .VN(1'b0), .VAUXP(16'h0000), .VAUXN(16'h0000),
    .ALM(), .OT(), .BUSY(busy), .CHANNEL(), .EOC(), .EOS(eos),
    .JTAGBUSY(), .JTAGLOCKED(), .JTAGMODIFIED(), .MUXADDR()
  );

endmodule
