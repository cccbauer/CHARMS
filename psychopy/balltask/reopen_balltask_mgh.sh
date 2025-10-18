#!/bin/bash
# Activate Anaconda environment
#source ~/anaconda3/bin/activate psychopy_env
source ~/psychopy_env/bin/activate

# Pass command line arguments to script
participant=$1
run=$2
feedback_on=$3
condition=$4
anchor=$5

python rt-network_feedback_mgh.py "$participant" "$run" "$feedback_on" "$condition" "$anchor"

