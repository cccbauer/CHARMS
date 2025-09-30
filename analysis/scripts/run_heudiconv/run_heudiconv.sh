#!/bin/bash

############################# run_heudiconv.sh ############################
# Description:
# 	Script to use heudiconv to convert raw dicoms to a BIDS directory for
# 	the MIND-BPD project. This script assumes you have installed heudiconv
# 	into a mamba environment "heudiconv" using the command:
#	"mamba create -n heudiconv -c conda-forge heudiconv"
#
# Usage:
# 	bash run_heudiconv.sh subject session
#
# Inputs:
#	subject: Subject ID (e.g., mindbpd2001)
#	session: Session (e.g., lo1, nf1)
#
# Notes:
#	dcmstack was throwing an error re: PixelSpacing in the dicom header
# 	being nested (see https://github.com/nipy/heudiconv/issues/821).
# 	This can be ignored, or the script can be appropriately modified.
# 
# Created by: MM Vandewouw
# Created on: June 24, 2025
#
# Modified by:
# Modified on: 

# User inputs
subject="$1"
session="$2"

# Hard code paths specific to MIND-BPD
main_dir='/vast/swglab/data/MIND-BPD'
dicom_dir=${main_dir}'/sourcedata/dicoms'
scripts_dir=${main_dir}'/scripts/run_heudiconv'

# Activate the conda environment
eval "$(mamba shell hook --shell bash)"
mamba activate heudiconv

# Call heudiconv
echo "Converting dicoms for: sub-${subject}_ses-${session}"
heudiconv --dbg --files ${dicom_dir}/sub-${subject}/sub-${subject}_ses-${session} -o ${main_dir}/rawdata -f ${scripts_dir}/heuristic_nf.py -c dcm2niix --bids -s ${subject} -ss ${session} --overwrite

# Change to correct permissions
find ${main_dir}/rawdata/sub-${subject}/ses-${session} -maxdepth 2 -type f -exec chmod 664 {} +

# Add in the "IntendedFor" field
cur_dir=`pwd`
cd ${main_dir}/rawdata/sub-${subject}
for i in $(ls ses-${session}/fmap/*json); do
line=$(grep -n '"EchoTime": 0.073,' ${i} | cut -d : -f 1)
next=1
lineout=$(($line + $next))
array=()
array=(`find ses-${session}/func/*bold.nii.gz -type f`)
var=$( IFS=$'\n'; printf "\"${array[*]}"\" )
filenames=$(echo $var | sed 's/ /", "/g')
textin=$(echo -e '"IntendedFor": ['$filenames'],')
sed -i "${lineout}i $textin " ${i}
done
cd ${cur_dir}



