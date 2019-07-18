#!/bin/bash
echo 'Executing myprogram'
# Setting the x flag will echo every
# command onto stderr. This is
# for debugging, so we can see what's
# going on.
set -x
echo ==ENV=============
# The env command prints out the
# entire execution environment. This
# is also present for debugging purposes.
env
echo ==PWD=============
# We also print out the execution
# directory. Again, for debugging purposes.
pwd

echo ==AGAVE_JOB_ID===
echo ${AGAVE_JOB_ID}

echo ==SLURM_JOB_ID===
echo ${SLURM_JOB_ID}

echo ==Input Files====
echo ${geoFile}
echo ${yamlFile}
mv ${geoFile} ${AGAVE_JOB_ID}.geo
mv ${yamlFile} ${AGAVE_JOB_ID}.yaml

# Convert .geo to .gen
ml gmsh
gmsh -2 -format msh2 ${AGAVE_JOB_ID}.geo
gmsh2exo.py ${AGAVE_JOB_ID}.msh ${AGAVE_JOB_ID}.gen

# Run vDef
srun vDef -geometry ${AGAVE_JOB_ID}.gen -result ${AGAVE_JOB_ID}_out.gen -options_file_yaml ${AGAVE_JOB_ID}.yaml 

# Create image
ml visit
visit -cli -nowin -s ${MEF90_DIR}/bin/plotCrack2DPNG.py ${AGAVE_JOB_ID}_out.gen
mv *.png ${AGAVE_JOB_ID}.png
