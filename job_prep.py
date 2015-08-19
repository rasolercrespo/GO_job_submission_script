import job_funcs

file_header = 'geo_opt_graph_chem'	# Project name in input file
step_init = 129;			# Last "stable" cell optimization step. Enter 0 if converged.

(cell, coord) = job_funcs.ReadRestart(file_header, step_init)

job_funcs.WriteCoords(coord)

job_funcs.WriteAutobash()

job_funcs.WritePullX(cell)

job_funcs.WriteJobScript()
