#!/bin/bash
#
#SBATCH -J fmriprep
#SBATCH --time=48:00:00
#SBATCH -n 1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=4G
#SBATCH --account=swgslurm
#SBATCH -p basic
# Outputs ----------------------------------
#SBATCH -o log/%x-%A-%a.out
#SBATCH -e log/%x-%A-%a.err
# ------------------------------------------

# Hard code paths specific to MIND-BPD
BIDS_DIR='/vast/swglab/data/MIND-BPD/rawdata'
DERIVS_DIR='/vast/swglab/data/MIND-BPD/derivatives/fmriprep-24.1.1'
LOCAL_FREESURFER_DIR='sourcedata/freesurfer'

# Prepare some writeable bind-mount points.
TEMPLATEFLOW_HOST_HOME=$HOME/.cache/templateflow
FMRIPREP_HOST_CACHE=$HOME/.cache/fmriprep
mkdir -p ${TEMPLATEFLOW_HOST_HOME}
mkdir -p ${FMRIPREP_HOST_CACHE}
mkdir -p ${DERIVS_DIR}/${LOCAL_FREESURFER_DIR}

# Make sure FS_LICENSE is defined in the container.
export SINGULARITYENV_FS_LICENSE=$HOME/.freesurfer.txt

# Designate a templateflow bind-mount point
export SINGULARITYENV_TEMPLATEFLOW_HOME="/templateflow"

# Create the singiularity command
SINGULARITY_CMD="singularity run --cleanenv -B $BIDS_DIR:/data -B ${TEMPLATEFLOW_HOST_HOME}:${SINGULARITYENV_TEMPLATEFLOW_HOME} -B /scratch:/work -B $DERIVS_DIR:/derivs /usr/pubsw/packages/fmriprep/24.1.1/fmriprep-24.1.1.simg"

# Parse the participants.tsv file and extract one subject ID from the line corresponding to this SLURM task.
subject=`sed -n "${SLURM_ARRAY_TASK_ID}p" participants_to_run.txt`

# Remove IsRunning files from FreeSurfer
find ${DERIVS_DIR}/${LOCAL_FREESURFER_DIR}/$subject/ -name "*IsRunning*" -type f -delete

# Compose the command line
cmd="${SINGULARITY_CMD} /data /derivs participant --participant-label $subject -w /work/ -vv --omp-nthreads 8 --nthreads 12 --mem_mb 30000 --fs-subjects-dir /derivs/${LOCAL_FREESURFER_DIR} --output-spaces MNI152NLin2009cAsym func"

# Setup done, run the command
echo Running task ${SLURM_ARRAY_TASK_ID}
echo Commandline: $cmd
eval $cmd
exitcode=$?

# Output results to a table
echo "sub-$subject   ${SLURM_ARRAY_TASK_ID}    $exitcode" \
      >> ${SLURM_JOB_NAME}.${SLURM_ARRAY_JOB_ID}.tsv
echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode
