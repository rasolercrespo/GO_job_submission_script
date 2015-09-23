import job_funcs

file_header = 'cell_opt_go_2_10'	# Project name in input file
step_init = 0;			# Last "stable" cell optimization step. Enter 0 if converged.

(cell, coord) = job_funcs.ReadRestart(file_header, step_init)

job_funcs.WriteCoords(coord)

job_funcs.WriteAutobash()

job_funcs.WritePullX(cell)
job_funcs.WritePullY(cell)
job_funcs.WritePullBoth(cell)

job_funcs.WriteJobScript()
