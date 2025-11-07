#!/bin/bash
# Activate Anaconda environment
#source ~/anaconda3/bin/activate psychopy_env
source ~/psychopy_env/bin/activate

# Pass command line arguments to script
participant=$1
randomization=$2
run=$3
feedback_on=$4
condition=$5
anchor=$6

python rt-network_feedback_mgh.py "$participant" "$randomization" "$run" "$feedback_on" "$condition" "$anchor"
