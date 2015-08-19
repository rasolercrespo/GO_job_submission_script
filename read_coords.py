# IMPORT VARIABLES FROM CALLING BASH SCRIPT
import os

# DETERMINE THE NUMBER OF LINES ASSOCIATED WITH
# THE FILE
line_header = int(os.environ["line"])
atom_line = line_header - 1

# OPEN THE OUTPUT FILE TO CARRY OUT THE FILE
# GENERATION PROCESS
input = open('input.coord', 'w')

# OPEN THE FILE CONTAINING THE COORDINATES
# AND JUMP TO DESIRED LINE
line_counter=0
with open(os.environ["filename"], 'r') as source:
 for line in source:
  line_counter = line_counter+1
  if line_counter >= atom_line:
   input.write(line)

input.close
