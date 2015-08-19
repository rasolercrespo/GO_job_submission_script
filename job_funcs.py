import os
import math

def ReadRestart(file_header, step_init):
        # Open the restart file, and read all the lines. Store only the contents of the sections named
        # CELL and COORD for further parsing of the system.
        
	# Open the file, based on the selected case
	if step_init == 0:
                with open(file_header + '-1.restart') as file:
                        content = file.read().splitlines()
        else:
                with open(file_header + '-1_' + str(step_init) + '.restart') as file:
                        content = file.read().splitlines()
	
	# Strip the lines of pesky separators
	content = map(str.lstrip, content)
	#print content	

	# Initialize data saving arrays
	cell = []
	coord = []
	cell_flag = 0
	coord_flag = 0

	# Strip only the CELL and COORD sections
	for line in range (0, len(content)):
		if content[line] == '&CELL':
			cell_flag = 1
		if content[line] == '&END CELL':
			cell_flag = 0
		if content[line] == '&COORD':
			coord_flag = 1
		if content[line] == '&END COORD':
			coord_flag = 0
		if cell_flag == 1:
			cell.append(content[line])
		if coord_flag == 1:
			coord.append(content[line])

	# Return the information	
	return (cell, coord)

def WriteCoords(coord):
	# Grab the coordinate list COORD, and write the input.coord file neccessary to run the
	# calculations in the system 
	
	# Remove header from COORD list
	del coord[0]

	# Calculate the number of atoms
	num_at = len(coord)

	# Open the output file and write header information
	file = open('input.coord', 'w')
	file.write(str(num_at) + '\n\n')
	
	# Write the coordinates based on the list COORD
	for line in range (0, len(coord)):
		file.write(coord[line] + '\n')	

	# Close the file upon finishing
	file.close()

def WriteJobScript():
	# Write the job submission script for this calculation set
	# Can be modified to take inputs later on
	
	# Open file for printing
	file = open('job.sh', 'w')

	# Print the file contents
	file.write('#!/bin/bash\n')
	file.write('\n')
	file.write('#SBATCH -J CP2K_Tension_X\n')
	file.write('#SBATCH -o out\n')
	file.write('#SBATCH -n 32\n')
	file.write('#SBATCH -p normal\n')
	file.write('#SBATCH -t 08:00:00\n')
	file.write('#SBATCH --mail-user=rasolercrespo@u.northwestern.edu\n')
	file.write('#SBATCH --mail-type=ALL\n')
	file.write('#SBATCH -A TG-MSS140028\n')
	file.write('module load intel/14.0.1.106\n')
	file.write('module load mvapich2/2.0b\n')
	file.write('module load cp2k\n')
	file.write('\n')
	file.write('export MV2_USE_OLD_BCAST=0\n')
	file.write('. autoexec.bash')

	# Close the file upon finishing
	file.close()

def WriteAutobash():
	# Writes a bash file containing the path for job execution and automatization of CP2K
	# calculations, as per usage of BASH and Python scripts

	# Determine current path
	path = os.path.dirname(os.path.abspath(__file__))
	
	# Open file for printing
	file = open('autoexec.bash', 'w')

	# Print the autoexec script
	file.write('#!/bin/bash\n')
	file.write('\n')
	file.write('for strain_incr in {0..50}\n')
	file.write(' do\n')
	file.write('  export strain_incr\n')
	file.write('  mkdir  step_"$strain_incr"\n')
	file.write('  mv $PWD/input.coord $PWD/step_"$strain_incr"/\n')
	file.write('  cd     step_"$strain_incr"\n')
	file.write('  python ' + str(path) + '/write_input_x.py\n')
	file.write('  ibrun cp2k.popt -i dftb.inp -o output.log\n')
	file.write('  sleep 30\n\n')
	file.write('  process="cp2k.popt"\n')
	file.write('  result=`pgrep ${process}`\n')
	file.write('   while [ "${result:-null}" != null ]\n')
	file.write('    do\n')
	file.write('     sleep 60\n')
	file.write('     result=`pgrep ${process}`\n')
	file.write('    done\n\n')
	file.write('   mv input.coord old_input.coord\n')
	file.write('   location=`grep -n "i =" *.xyz | tail --lines=1`\n')
	file.write('''   line=`echo $location | sed -r 's/^([^.]+).*$/\\1/; s/^[^0-9]*([0-9]+).*$/\\1/'`\n''')
	file.write('   export line\n')
	file.write('''   filename=`ls | grep 'xyz'`\n''')
	file.write('   export filename\n')
	file.write('   python ' + str(path) + '/read_coords.py\n')
	file.write('   mv input.coord ../input.coord\n')
	file.write('   mv old_input.coord input.coord\n')
	file.write('   cd ..\n')
	file.write('  done')

	# Close the file upon finishing
	file.close()

def WritePullX(cell):
	# Write the x-direction pulling script for the MM calculation involved in this work
	# based on the CELL section of the CELL_OPT restart file
	
	# Remove header from CELL list
	del cell[0]

	# Store A, B and C cell vectors
	a = float(cell[0].split()[1])
	b = float(cell[1].split()[2])
	c = float(cell[2].split()[3])

	# Open the file to write
	script = open('write_input_x.py', 'w')
	
	# Write the Python script for pulling
	script.write('a = ' + str(a) + '\n')
	script.write('b = ' + str(b) + '\n')
	script.write('c = ' + str(c) + '\n')
	script.write('\n')
	script.write('strain = 1 + 0.005*int(os.environ["strain_incr"])\n')
	script.write('\n')
	script.write('pts_x = math.floor(a*strain)\n')
	script.write('pts_y = math.floor(b)\n')
	script.write('pts_z = math.floor(c)\n')
	script.write('pts_x = int(pts_x)\n')
	script.write('pts_y = int(pts_y)\n')
	script.write('pts_z = int(pts_z)\n')
	script.write('\n')
	script.write('''input = open('dftb.inp', 'w')\n''')
	script.write('\n')
	script.write('''\ninput.write('&GLOBAL')''')
	script.write('''\ninput.write('\\n PROJECT\\tgeo_opt_go_patch')''')
	script.write('''\ninput.write('\\n RUN_TYPE\\tGEO_OPT')''')
	script.write('''\ninput.write('\\n PRINT_LEVEL\\tLOW')''')
	script.write('''\ninput.write('\\n&END GLOBAL\\n')''')       
	script.write('\n')
	script.write('''\ninput.write('\\n&MOTION')''')
	script.write('''\ninput.write('\\n &GEO_OPT')''')       
	script.write('''\ninput.write('\\n  MAX_ITER\\t1000')''')
	script.write('''\ninput.write(' \\n &END GEO_OPT')''')
	script.write('''\ninput.write('\\n &PRINT')''')
	script.write('''\ninput.write('\\n  &STRESS')''')             
	script.write('''\ninput.write('\\n  &END STRESS')''')             
	script.write('''\ninput.write('\\n &END PRINT')''')
	script.write('''\ninput.write('\\n&END MOTION\\n')''')
	script.write('\n')
	script.write('''\ninput.write('\\n&FORCE_EVAL')''')         
	script.write('''\ninput.write('\\n STRESS_TENSOR\\tDIAGONAL_ANALYTICAL')''')
	script.write('''\ninput.write('\\n &DFT')''')   
	script.write('''\ninput.write('\\n  &QS')''')
	script.write('''\ninput.write('\\n   METHOD DFTB')''')                  
	script.write('''\ninput.write('\\n   &DFTB')''')
	script.write('''\ninput.write('\\n    SELF_CONSISTENT\\tT')''')
	script.write('''\ninput.write('\\n    DO_EWALD\\t\\tT')''')         
	script.write('''\ninput.write('\\n    DISPERSION\\t\\tF')''')        
	script.write('''\ninput.write('\\n    &PARAMETER')''')
	script.write('''\ninput.write('\\n     PARAM_FILE_PATH\\t/home1/03260/rscrespo/dftb_parameter_sets/cp2k/scc/')''')
	script.write('''\ninput.write('\\n     PARAM_FILE_NAME\\tparameter_table')''')
	script.write('''\ninput.write('\\n     UFF_FORCE_FIELD\\tuff_table')''')
	script.write('''\ninput.write('\\n    &END PARAMETER')''')
	script.write('''\ninput.write('\\n   &END DFTB')''')   
	script.write('''\ninput.write('\\n  &END QS')''')   
	script.write('''\ninput.write('\\n  &SCF')''')
	script.write('''\ninput.write('\\n   SCF_GUESS\\tATOMIC')''')     
	script.write('''\ninput.write('\\n   MAX_SCF\\t200')''') 
	script.write('''\ninput.write('\\n   &OT ON')''')   
	script.write('''\ninput.write('\\n    LINESEARCH\\t\\t3PNT')''')   
	script.write('''\ninput.write('\\n    PRECONDITIONER\\tFULL_SINGLE')''')
	script.write('''\ninput.write('\\n   &END OT')''')
	script.write('''\ninput.write('\\n  &END SCF')''')                
	script.write('''\ninput.write('\\n  &POISSON')''')        
	script.write('''\ninput.write('\\n   &EWALD')''')        
	script.write('''\ninput.write('\\n    EWALD_TYPE\\tSPME')''')
	script.write('''\ninput.write('\\n    GMAX\\t' + str(pts_x)+ ' ' + str(pts_y) + ' ' + str(pts_z))''')
	script.write('''\ninput.write('\\n   &END EWALD')''')  
	script.write('''\ninput.write('\\n   POISSON_SOLVER\\tANALYTIC')''')
	script.write('''\ninput.write('\\n   PERIODIC\\t\\tXYZ')''')
	script.write('''\ninput.write('\\n  &END POISSON')''')  
	script.write('''\ninput.write('\\n &END DFT')''')     
	script.write('''\ninput.write('\\n &PRINT')''')
	script.write('''\ninput.write('\\n  &STRESS_TENSOR')''')      
	script.write('''\ninput.write('\\n   FILENAME\\t\\t__STD_OUT__')''')
	script.write('''\ninput.write('\\n   LOG_PRINT_KEY\\tTRUE')''')
	script.write('''\ninput.write('\\n   ADD_LAST\\t\\tNUMERIC')''')
	script.write('''\ninput.write('\\n   &EACH')''')
	script.write('''\ninput.write('\\n    GEO_OPT 1')''')                  
	script.write('''\ninput.write('\\n   &END EACH')''')
	script.write('''\ninput.write('\\n  &END STRESS_TENSOR')''')
	script.write('''\ninput.write('\\n &END PRINT')''')
	script.write('''\ninput.write('\\n &SUBSYS')''')
	script.write('''\ninput.write('\\n  &CELL')''')
	script.write('''\ninput.write('\\n   ABC\\t\\t\\t' + str(a*strain) + ' ' + str(b) + ' ' + str(c))''')
	script.write('''\ninput.write('\\n   ALPHA_BETA_GAMMA\\t90 90 90')''')
	script.write('''\ninput.write('\\n   PERIODIC\\t\\tXYZ')''')               
	script.write('''\ninput.write('\\n   SYMMETRY\\t\\tORTHORHOMBIC')''')
	script.write('''\ninput.write('\\n  &END CELL')''')   
	script.write('''\ninput.write('\\n  &TOPOLOGY')''')
	script.write('''\ninput.write('\\n   COORD_FILE_NAME\\tinput.coord')''')
	script.write('''\ninput.write('\\n   COORD_FILE_FORMAT\\tXYZ')''')
	script.write('''\ninput.write('\\n  &END TOPOLOGY')''')
	script.write('''\ninput.write('\\n &END SUBSYS')''')
	script.write('''\ninput.write('\\n&END FORCE_EVAL')''')
	script.write('\n')
	script.write('''\ninput.close''')
	# Close the file upon finishing
	script.close()
