#!/bin/bash

############################# run_fmriprep.sh ############################
# Description:
# 	Script to run fmriprep on participants from the MIND-BPD project. The 
# script expects that you have a FreeSurfer license in 
#	$HOME/.freesurfer.txt. It also expects that you have a list of participants
# 	you want to process in this directory called "participants_to_run.txt".
#
# Usage:
# 	bash run_fmriprep.sh slurm
#
# Inputs:
#	slurm: Whether or not to run on a slurm cluster
# 		   0 = False, 1 = True 	
#
# Notes:
# 
# Created by: MM Vandewouw
# Created on: June 24, 2025
#
# Modified by:
# Modified on:

# Extract slurm
slurm="$1"

# Extract how many participant's we're running
num_lines=$(wc -l < "participants_to_run.txt")

# Check if running locally
if [ $slurm == '0' ]; then # Local

	# Iterate across the participants
	for i in $(seq 1 $num_lines); do
		export SLURM_ARRAY_TASK_ID=$i
		bash sbatch.slurm
	done

elif [ $slurm == '1']; then # Slurm

	# Submit a job
	sbatch --array=1-$num_lines sbatch.slurm

fi 




