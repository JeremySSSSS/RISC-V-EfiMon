open_project pulpissimo-nexys.xpr
# Agrega el modulo XADC (temperatura del die, TFG) si aun no esta en el proyecto.
if {[llength [get_files -quiet xadc_temp.v]] == 0} {
  add_files -norecurse rtl/xadc_temp.v
  puts ">>> xadc_temp.v agregado al proyecto."
}
set_property STEPS.SYNTH_DESIGN.TCL.POST "" [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.TCL.PRE "" [get_runs synth_1]
set_property STEPS.INIT_DESIGN.TCL.PRE "" [get_runs impl_1]
set_property AUTO_INCREMENTAL_CHECKPOINT 0 [get_runs synth_1]
set_property INCREMENTAL_CHECKPOINT "" [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.INCREMENTAL_MODE off [get_runs synth_1]
set_param general.maxThreads 6
set_property STEPS.SYNTH_DESIGN.ARGS.FLATTEN_HIERARCHY none [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.DIRECTIVE RuntimeOptimized [get_runs synth_1]
update_compile_order -fileset sources_1
reset_run synth_1
puts ">>> Lanzando sintesis con 6 threads..."
launch_runs synth_1 -jobs 6
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] != "100%"} { puts "ERROR: Sintesis fallo"; exit 1 }
puts ">>> Sintesis completada."
open_run synth_1 -name netlist_1
set_property needs_refresh false [get_runs synth_1]
remove_cell i_pulpissimo/i_padframe/i_pulpissimo_pads/i_all_pads/i_all_pads_pads/i_pad_bootsel*
disconnect_net -objects [get_nets i_pulpissimo/i_soc_domain/bootsel_i*]
connect_net -objects [get_nets i_pulpissimo/i_soc_domain/bootsel_i*] -net i_pulpissimo/<const0>
remove_cell i_pulpissimo/i_padframe/i_pulpissimo_pads/i_all_pads/i_all_pads_pads/i_pad_hyper*
disconnect_net -objects [get_nets i_pulpissimo/i_soc_domain/pad_to_hyper_i*]
connect_net -objects [get_nets i_pulpissimo/i_soc_domain/pad_to_hyper_i*] -net i_pulpissimo/<const0>
remove_cell i_pulpissimo/i_padframe/i_pulpissimo_pads/i_all_pads/i_all_pads_pads/i_pad_jtag_trst*
disconnect_net -objects [get_nets i_pulpissimo/i_soc_domain/jtag_trst_ni]
connect_net -objects [get_nets i_pulpissimo/i_soc_domain/jtag_trst_ni] -net i_pulpissimo/<const1>
puts ">>> Netlist limpiado."
set_property "steps.opt_design.args.directive" "RuntimeOptimized" [get_runs impl_1]
set_property "steps.place_design.args.directive" "RuntimeOptimized" [get_runs impl_1]
set_property "steps.route_design.args.directive" "RuntimeOptimized" [get_runs impl_1]
set_property STEPS.WRITE_BITSTREAM.ARGS.BIN_FILE true [get_runs impl_1]
puts ">>> Lanzando implementacion..."
launch_runs impl_1 -jobs 6
wait_on_run impl_1
launch_runs impl_1 -jobs 6 -to_step write_bitstream
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] != "100%"} { puts "ERROR: Implementacion fallo"; exit 1 }
puts ">>> Bitstream generado. Listo."
