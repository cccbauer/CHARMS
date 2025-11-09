#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""This experiment was created using PsychoPy2 Experiment Builder (v1.81.03), Wed 04 Feb 2015 11:22:15 AM EST
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import time
import matplotlib.pyplot as plt
import matplotlib
import random
import csv
import math
import pandas as pd
import sys
import threading
import subprocess
import shlex
import locale
from bids_tsv_convert_balltask import *
import fnmatch  # for matching csv file names for given run for sham subjects
import numpy as np
import shutil

# button box mgh
left_button='1'
right_button='2'
enter_button='0'

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

##################################################################################
## PARSE COMMAND LINE ARGUMENTS TO AUTOFILL DIALOGUE BOX AT STARTUP (for runs 2+) ##
num_cmd_line_arguments = len(sys.argv)
if num_cmd_line_arguments >= 2:
    input_participant = sys.argv[1]
else:
    input_participant = ''

# cmd line arg 2 will be randomization number (NEW)
if num_cmd_line_arguments >= 3:
    input_randomization = sys.argv[2]
else:
    input_randomization = ''

# cmd line arg 3 will be run number (shifted from arg 2 to arg 3)
if num_cmd_line_arguments >= 4:
    input_run = sys.argv[3]
else:
    input_run = ''

# cmd line arg 4 will be feedback / no feedback (shifted from arg 3 to arg 4)
if num_cmd_line_arguments >= 5:
    if sys.argv[4] == 'Feedback':
        input_feedback = ['Feedback', 'No Feedback']
    else:
        input_feedback = ['No Feedback', 'Feedback']
else:
    input_feedback = ['', 'Feedback', 'No Feedback']

# cmd line arg 5 will be 15min vs 30min (shifted from arg 4 to arg 5)
if num_cmd_line_arguments >= 6:
    if sys.argv[5] == '15min':
        input_feedback_condition = ['15min', '30min']
    else:
        input_feedback_condition = ['30min', '15min']
else:
    input_feedback_condition = ['', '15min', '30min']

# cmd line arg 6+ will be anchor (shifted from arg 5+ to arg 6+)
if num_cmd_line_arguments >= 7:
    input_anchor = ' '.join(sys.argv[6:])
else:
    input_anchor = ''
#####################################################################################

# Store info about the experiment
expName = 'DMN_BallTask'  # from the Builder filename that created thi s script
expInfo = {'participant': input_participant, 'randomization': input_randomization, 
           'run': input_run, 'anchor': input_anchor, 'feedback_on': input_feedback,
           'feedback_condition': input_feedback_condition}
# MURFI fake for debugging
murfi_FAKE = True

# Add popup warning if murfi_FAKE is True
if murfi_FAKE:
    fake_warning = gui.Dlg(title='MURFI FAKE MODE WARNING', labelButtonOK='Continue', labelButtonCancel='Cancel')
    fake_warning.addText('WARNING: murfi_FAKE is currently set to True!')
    fake_warning.addText('This means no real MURFI data will be used.')
    fake_warning.addText('')  # blank line
    fake_warning.addField('', choices=['Keep FAKE mode ON', 'Turn FAKE mode OFF'])
    fake_warning_data = fake_warning.show()
    
    if not fake_warning.OK:
        core.quit()  # user pressed cancel
    else:
        # Update murfi_FAKE based on user choice
        if fake_warning_data[0] == 'Turn FAKE mode OFF':
            murfi_FAKE = False
            print('murfi_FAKE has been turned OFF')
            screen_size=True
        else:
            print('Continuing with murfi_FAKE = True')
            screen_size=False
else:
    print('Continuing with murfi_FAKE = False')
    screen_size=True

# Show dialogue box until all participant info has been entered
while (expInfo['feedback_on'] not in ['Feedback', 'No Feedback'] or 
       expInfo['randomization'] == '' or
       expInfo['feedback_condition'] not in ['15min', '30min']):
    expInfo['feedback_on'] = input_feedback
    expInfo['feedback_condition'] = input_feedback_condition
    dlg = gui.DlgFromDict(dictionary=expInfo, title=expName,
                          labels={'participant': 'Participant ID (2XX)',
                                  'randomization': 'Randomization Number (0XX)',
                                  'run': 'Run',
                                  'feedback_on': 'Display Feedback?',
                                  'feedback_condition': 'Session Length',
                                  'anchor': 'Participant Anchor'},
                          order=['participant', 'randomization', 'run', 'feedback_on', 'feedback_condition', 'anchor'])
    if dlg.OK == False:
        core.quit()  # user pressed cancel


# Hard code other experiment info
## Timestamp
expInfo['date'] = data.getDateStr()
expInfo['expName'] = expName
expInfo['No_of_ROIs'] = 2
expInfo['Level_1_2_3'] = 1
expInfo['Run_Time'] = 150
expInfo['pda_outlier_threshold'] = 2
circles_move_with_hits = False
circle_radius_shrink_with_hits = True
num_pda_outliers = 0
# Baseline time before feedback (seconds)
BaseLineTime = 30

# TR (seconds)
expInfo['tr'] = 1.2

# CHARMS changes

def update_participant_mapping(rand_num, participant_id):
    """Update the randomization to participant ID mapping file"""
    mapping_file = os.path.join('feedback', 'participant_mapping.txt')
    
    # Make sure feedback directory exists
    if not os.path.exists('feedback'):
        os.makedirs('feedback')
    
    # Read existing mappings
    if os.path.exists(mapping_file):
        mapping_df = pd.read_csv(mapping_file, sep='\t', dtype={'randomization_id': str, 'participant_id': str})
    else:
        mapping_df = pd.DataFrame(columns=['randomization_id', 'participant_id'])
    
    # Format both IDs as 3-digit strings
    rand_num_str = f"{rand_num:03d}"
    participant_id_str = f"{participant_id}" if isinstance(participant_id, str) else f"{participant_id:03d}"
    
    # Check if this randomization is already mapped
    if rand_num_str in mapping_df['randomization_id'].values:
        # Update existing entry
        mapping_df.loc[mapping_df['randomization_id'] == rand_num_str, 'participant_id'] = participant_id_str
    else:
        # Add new entry
        new_row = pd.DataFrame({'randomization_id': [rand_num_str], 'participant_id': [participant_id_str]})
        mapping_df = pd.concat([mapping_df, new_row], ignore_index=True)
    
    # Sort by randomization_id and save
    mapping_df = mapping_df.sort_values('randomization_id')
    mapping_df.to_csv(mapping_file, sep='\t', index=False)
    

'''RANDOMIZATION - IMPROVED VERSION FOR SHAM ASSIGNMENT'''

# Load in the randomization file with proper error handling
import os
import pandas as pd

# Try multiple possible file locations
possible_paths = [
    os.path.join('feedback', 'mgh_randlist.txt'),
    'mgh_randlist.txt',
    os.path.join('..', 'feedback', 'mgh_randlist.txt')
]

rand_list = None
for path in possible_paths:
    if os.path.exists(path):
        try:
            rand_list = pd.read_csv(path, sep='\t')
            print(f"Successfully loaded randomization file from: {path}")
            break
        except Exception as e:
            print(f"Failed to read {path}: {e}")

if rand_list is None:
    raise FileNotFoundError("Could not find mgh_randlist.txt")

# Get the randomization number for looking up SHAM/REAL status
rand_num = int(expInfo['randomization'])

# Find the matching row using randomization number
sub_row = rand_list.loc[rand_list['participant_id'] == rand_num]

if not sub_row.empty:
    if sub_row.iloc[0]['group'] == 'R':
        SHAM = False
    else:
        SHAM = True
    
    print(f"Using Participant ID {expInfo['participant']} for file naming")
else:
    raise ValueError(f"Randomization number {rand_num} not found in randomization list!")

# Update the participant mapping file
update_participant_mapping(rand_num, expInfo['participant'])
#
roi_number = str('%s') % (expInfo['No_of_ROIs'])
roi_number = int(roi_number)

'''
Minimum and maximum number of "hits" to targets for which scale factor won't be adjusted
Fewer hits than min_hits --> scale factor goes up and ball moves faster
More hits than max_hits (in either direction) --> scale factor goes down and ball moves more slowly
'''
min_hits = 3
max_hits = 5

# default scale factor (higher means ball moves up/down faster)
default_scale_factor = 10

# another interal scale factor to make sure scaling of feedback is appropriate (higher means ball moves up/down more SLOWLY)
internal_scaler = 10

# CHARMS change
filename_prefix = "sub-charms"
foldername = os.path.join('data', filename_prefix + expInfo['participant'])

# Setup files for saving
if not os.path.isdir('data'):
    os.makedirs('data')  # if this fails (e.g. permissions) we will get error

if not os.path.exists(foldername):
    os.mkdir(foldername)

print("expInfo['feedback_on'] =", expInfo['feedback_on'])

# output file string (different depending on if feedback is being offered)
if expInfo['feedback_on'] == 'Feedback':
    filename = foldername + os.path.sep + '%s%s_DMN_feedback_%s' % (
    filename_prefix, expInfo['participant'], expInfo['run'])
elif expInfo['feedback_on'] == 'No Feedback':
    filename = foldername + os.path.sep + '%s%s_DMN_nofeedback_%s' % (
    filename_prefix, expInfo['participant'], expInfo['run'])

# if filepath already exists, stop run and check with user
# Allow choice of moving to next run or overwriting the current one
while os.path.exists(filename + '_roi_outputs.csv'):
    warning_box = gui.Dlg(title='WARNING')
    warning_box.addText(
        f'Already have data for {expInfo["participant"]} run {expInfo["run"]}!\n'
        f'Click OK to write to Run {int(expInfo["run"]) + 1} instead\n'
        f'To overwrite run {expInfo["run"]}, select this option from the dropdown menu\n'
        f'Or, click Cancel to exit'
    )
    warning_box.addField(
        'Choose Run #',  # This is the label (first positional argument)
        choices=[f"Run {int(expInfo['run']) + 1}", f"Overwrite Run {int(expInfo['run'])}"]
    )
    warning_box_data = warning_box.show()

    if not warning_box.OK:
        core.quit()

    # If not canceling, set filename
    else:
        run_choice = warning_box_data[0].strip()
        # If not overwriting, set filename to next run
        # if f"Overwrite Run {int(expInfo['run'])}" not in warning_box_data:
        if run_choice != f"Overwrite Run {expInfo['run']}":
            expInfo['run'] = int(expInfo['run']) + 1
            filename = foldername + os.path.sep + '%s%s_DMN_feedback_%s' % (
            filename_prefix, expInfo['participant'], expInfo['run'])
        # If overwriting, keep current filename
        # elif f"Overwrite Run {int(expInfo['run'])}" in warning_box_data:
        elif run_choice == f"Overwrite Run {expInfo['run']}":
            print('OVERWRITE')
            print(filename)
            # Remove files only if they exist
            import glob
            pattern = f'{filename}*'
            files_to_remove = glob.glob(pattern)
            for file in files_to_remove:
                try:
                    os.remove(file)
                    print(f'Removed: {file}')
                except Exception as e:
                    print(f'Could not remove {file}: {e}')
            break

# If first run, use default scale factor
# Otherwise, adjust scale factor up/down if needed
if int(expInfo['run']) == 1:
    print('Run 1: starting with default scale scale factor')
    expInfo['scale_factor'] = default_scale_factor
else:
    try:

        # loop through prior runs, starting at most recent, until the most recent prior run with at least 140 volumes is found
        # label this most recent run with 140+ volumes as the "last run" to pull parameters from
        last_run_complete = False
        last_run_counter = 1
        while last_run_complete == False and last_run_counter < int(expInfo['run']):
            last_run_filename = filename.replace("feedback_" + str(expInfo['run']),
                                                 "feedback_" + str(
                                                     int(expInfo['run']) - last_run_counter)) + '_roi_outputs.csv'
            print(last_run_filename)
            print(expInfo['run'])
            print(expInfo['participant'])
            last_run_info = pd.read_csv(last_run_filename)
            if last_run_info.shape[0] > 140:
                last_run_complete = True
            else:
                last_run_counter += 1

        # ONLY update scale factor if there is a prior COMPLETE run to use to do this
        if last_run_complete:
            # Max values in cumulative hits columns give the total number of hits each in the last run
            last_run_cen_hits = last_run_info.cen_cumulative_hits.max()
            last_run_dmn_hits = last_run_info.dmn_cumulative_hits.max()

            print('Last run volumes: ', last_run_info.shape[0], ' Last run filename: ', last_run_filename)
            print('Last run CEN hits: ', last_run_cen_hits, ' Last run DMN hits: ', last_run_dmn_hits)

            # last_run_scale_factor
            last_run_scale_factor = last_run_info.scale_factor[0]

            # if 5+ hits in either direction, decrease scale factor
            if last_run_dmn_hits > max_hits or last_run_cen_hits > max_hits:
                expInfo['scale_factor'] = last_run_scale_factor * 0.75

            # if not enough hits, increase scale factor
            elif last_run_cen_hits + last_run_dmn_hits < min_hits:
                expInfo['scale_factor'] = last_run_scale_factor * 1.25

            # otherwise, keep scale factor the same
            else:
                expInfo['scale_factor'] = last_run_scale_factor

            print('Last run scale factor: ', last_run_scale_factor, ' This run scale factor: ', expInfo['scale_factor'])
        else:
            print('WARNING: no prior complete runs. Settting to default scale factor.')
            expInfo['scale_factor'] = default_scale_factor

    # If this breaks (no prior runs) use default scale factor
    except Exception as error:
        print(error)
        print('ERROR: could not pull scale factor from previous run. Settting to default scale factor.')
        expInfo['scale_factor'] = default_scale_factor

''' PREPARE THE SHAM PARTICIPANT BY COPYING THE MATCHED OR RANDOM REAL PARTICIPANT'''
if SHAM:
    mapping_file = os.path.join('feedback', 'participant_mapping.txt')
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(
            f"Participant mapping file not found at {mapping_file}.\n"
            f"This file is created automatically when REAL participants are run.\n"
            f"Please run at least one REAL participant first."
        )

    mapping_df = pd.read_csv(mapping_file, sep='\t', dtype={'randomization_id': str, 'participant_id': str})

    # Get list of REAL randomization IDs from the randomization list (as strings)
    real_rand_ids = [f"{x:03d}" for x in rand_list[rand_list['group'] == 'R']['participant_id'].tolist()]

    # Filter mapping to only include REAL participants
    real_mappings = mapping_df[mapping_df['randomization_id'].isin(real_rand_ids)]

    if real_mappings.empty:
        raise ValueError(
            f"No REAL participants found in mapping file.\n"
            f"Please run at least one REAL participant first."
        )
    
    # Function to check if a participant's dataset is complete
    def is_dataset_complete(participant_id, min_runs=1):
        """Check if a real participant has complete data"""
        data_path = os.path.join("data", filename_prefix + participant_id)
        feedback_path = os.path.join("feedback", filename_prefix + participant_id)
        
        # Check if either directory exists
        if not os.path.exists(data_path) and not os.path.exists(feedback_path):
            return False
        
        # Check for feedback frame files (indicator of completed runs)
        complete_runs = 0
        for path in [data_path, feedback_path]:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if 'feedback' in file and 'frames.csv' in file:
                        try:
                            df = pd.read_csv(os.path.join(path, file))
                            if len(df) > 100:
                                complete_runs += 1
                        except:
                            pass
        
        return complete_runs >= min_runs
    
    # Sort real mappings to prioritize matching by randomization number
    real_mappings = real_mappings.copy()
    real_mappings['distance'] = real_mappings['randomization_id'].apply(lambda x: abs(int(x) - rand_num))
    real_mappings = real_mappings.sort_values('distance')
        
    # Find a suitable REAL participant with complete data
    matched_participant_id = None
    matched_rand_id = None
    for _, row in real_mappings.iterrows():
        participant_id = row['participant_id']
        if is_dataset_complete(participant_id):
            matched_participant_id = participant_id
            matched_rand_id = row['randomization_id']
            break
    
    if matched_participant_id is None:
        raise ValueError(
            f"No complete REAL participant datasets found for SHAM participant {expInfo['participant']}.\n"
            f"Please ensure at least one REAL participant has been run completely."
        )
    
    # Use the matched participant ID for copying data
    sub_match = matched_participant_id
    
    # Check both possible locations for the matching data
    match_feedback_csv_path_data = os.path.join("data", filename_prefix + sub_match)
    match_feedback_csv_path_feedback = os.path.join("feedback", filename_prefix + sub_match)
    
    # Actual subject directory for this SHAM participant
    feedback_csv_path = os.path.join("feedback", filename_prefix + expInfo['participant'])
    

    # Copy from REAL participant if folder doesn't exist
    if not os.path.exists(feedback_csv_path):
        if os.path.exists(match_feedback_csv_path_feedback):
            shutil.copytree(match_feedback_csv_path_feedback, feedback_csv_path)
            print(f"Copied data from feedback directory: {match_feedback_csv_path_feedback}")
        elif os.path.exists(match_feedback_csv_path_data):
            os.makedirs(feedback_csv_path, exist_ok=True)
            for file in os.listdir(match_feedback_csv_path_data):
                if 'feedback' in file and 'frames.csv' in file:
                    shutil.copy2(os.path.join(match_feedback_csv_path_data, file),
                               os.path.join(feedback_csv_path, file))
            print(f"Copied data from data directory: {match_feedback_csv_path_data}")
        else:
            raise FileNotFoundError(
                f"Cannot find data for matched REAL participant {sub_match}."
            )

if SHAM and expInfo['feedback_on'] == 'Feedback':
    # Construct the folder path dynamically
    feedback_csv_path = os.path.join("feedback", filename_prefix + expInfo['participant'])

    # Ensure the folder exists
    if not os.path.exists(feedback_csv_path):
        raise FileNotFoundError(f"Folder '{feedback_csv_path}' does not exist.")

    # Use fnmatch to match filenames like "*feedback_<run>_frames.csv"
    pattern = f"*feedback_{expInfo['run']}_frames.csv"
    matching_files = [f for f in os.listdir(feedback_csv_path) if fnmatch.fnmatch(f, pattern)]
    print(matching_files)

    # Ensure exactly one match exists
    if len(matching_files) == 0:
        raise FileNotFoundError(f"CSV file error '{feedback_csv_path}' matching pattern '{pattern}'")
    elif len(matching_files) > 1:
        raise ValueError(f"Multiple CSV file error '{feedback_csv_path}' matching pattern '{pattern}'")

    # Read CSV file
    csv_file = os.path.join(feedback_csv_path, matching_files[0])
    df_csv = pd.read_csv(csv_file)
    print(f"csv file: {csv_file}")

RUN_TIME = str('%s') % (expInfo['Run_Time'])
RUN_TIME = int(RUN_TIME)
RUN_TIME = RUN_TIME

# Convert scale factor and position to pixel space
position_distance=expInfo['Level_1_2_3']
position_distance=int(position_distance)
scale_factor_z2pixels=expInfo['scale_factor']
scale_factor_z2pixels=int(scale_factor_z2pixels)
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

# Column headers for outfile
with open(filename+'_roi_outputs.csv', 'a') as csvfile:
    stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    stim_writer.writerow(['volume', 'scale_factor', 'time', 'time_plus_1.2', 'cen', 'dmn', 'stage', 'cen_cumulative_hits', 'dmn_cumulative_hits', 'pda_outlier', 'ball_y_position', 'top_circle_y_position', 'bottom_circle_y_position'])       

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=True,
    dataFileName=filename)
#save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file
endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation
# Setup the Window
win = visual.Window(size=(1080,1080), fullscr=screen_size, screen=1, allowGUI=False, allowStencil=False,#1024, 1024
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )

# store frame rate of monitor if we can measure it successfully
expInfo['frameRate']=win.getActualFrameRate()
if expInfo['frameRate']!=None:
    frameDur = 1.0/expInfo['frameRate']
else:
    print('FRAME RATE GUESSING')
    frameDur = 1.0/60.0 # couldn't get a reliable measure so guess

# Approximately how many frames does the monitor refresh per volume?
tr_to_frame_ratio = expInfo['tr']/frameDur

# Create csv output file for post-run slider questions
run_questions_file = filename + '_slider_questions.csv'
with open(run_questions_file, 'a') as csvfile:
    stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    stim_writer.writerow(["id", "run", 'feedback_on', "question_text", "response", "rt"])  

slider_instruction = visual.TextStim(win=win, ori=0, name='text',
        text="You'll see a few slider questions next\nPress the left and right buttons to move the slider\nAnd the top button to enter your response\nPress any button to continue", font=u'Arial',
        pos=[0, 0.2], height=0.06, wrapWidth=1.2,
        color=u'white', colorSpace='rgb', opacity=1,
        depth=0.0)


def run_slider(question_text='Default Text', left_label='left', right_label='right'):
    slider_question = visual.TextStim(win=win, ori=0, name='text',
        text=question_text, font=u'Arial',
        pos=[0, 0.2], height=0.06, wrapWidth=1.2,
        color=u'white', colorSpace='rgb', opacity=1,
        depth=0.0)

    vas = visual.Slider(win,
                size=(0.85, 0.1),
                ticks=(1, 9),
                labels=(left_label, right_label),
                granularity=1,
                color='white',
                fillColor='white',
                font=u'Arial',
                labelHeight=0.06)

    event.clearEvents('keyboard')
    vas.markerPos = 5
    vas.draw()
    slider_question.draw()
    win.flip()
    continueRoutine = True
    while continueRoutine:
        keys = event.getKeys(keyList=[left_button, right_button, enter_button])
        if len(keys):
            if left_button in keys:
                vas.markerPos = vas.markerPos - 1
            elif right_button in keys:
                vas.markerPos = vas.markerPos  + 1 
            elif enter_button in keys:
                vas.rating=vas.markerPos
                continueRoutine=False
            vas.draw()
            slider_question.draw()
            win.flip()
            print(keys)

    print(f'Rating: {vas.rating}, RT: {vas.rt}')
    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  question_text, vas.rating, vas.rt])   

    
    return(vas.rating)

# Initialize components for Routine "instructions"
instructionsClock = core.Clock()
text = visual.TextStim(win=win, ori=0, name='text',
    text='',font=u'Arial',
    pos=[0, 0], height=0.06, wrapWidth=1.2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "trigger"
triggerClock = core.Clock()
waiting_for_trigger_text = visual.TextStim(win=win, ori=0, name='waiting_for_trigger_text',
    text=u'waiting for scanner',    font=u'Arial',
    pos=[0, 0], height=0.1, wrapWidth=2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "baseline"
baselineClock = core.Clock()
text_2 = visual.TextStim(win=win, ori=0, name='text_2',
    text=u'+',    font=u'Arial',
    pos=[0, 0], height=0.3, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)


text_relax = visual.TextStim(win=win, ori=0, name='text_relax',
    text=u'Relax',    font=u'Arial',
    pos=[0, -.2], height=0.07, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "feedback"
feedbackClock = core.Clock()

text_4 = visual.TextStim(win=win, ori=0, name='text_4',
    text='default text',    font=u'Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-3.0)

#prepare the targets
colors=['yellow','lightblue','red','green','cyan','magenta','black','honeydew','indigo','maroon']
roi_names_list=['cen','dmn']
print (roi_names_list)
n_roi = roi_number
tau = 2 * np.pi
theta = np.zeros((n_roi))
for i in range(n_roi):
    theta[i] = (i * tau)/float(n_roi)

positions = np.exp((0-1j) * theta)
positions=positions*position_distance
positions = [1, -1]

# target_positions:
roi_pos = np.zeros((n_roi, 2))
for i in range(n_roi):
    roi_pos[i, :] = [(np.real(positions[i]))/3, (np.imag(positions[i]))/3]

# scale based on aspect ratio
scale=[win.size[1]/win.size[0], 1]

target_circles=[]
target_circles_id=[]
hit_counter=[]
home=[]
for i in range(n_roi):
    roi_circle_i = visual.Circle(win, pos=(roi_pos[i, 1],roi_pos[i, 0]), 
                                 radius=0.15,fillColor=None, 
                                 lineColor=colors[i], lineWidth=3)
    roi_circle_i.size *= scale
    target_circles.append(roi_circle_i)
    hit_counter.append(0)
    print (hit_counter)

starting_point = visual.Circle(win, pos=(0,0), radius=0.005,fillColor='white', lineColor='white')
home.append(starting_point)

# function to check whether ball is in a given circle
def in_circle(center_x, center_y, radius, x, y):
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2


# checks if ball has gone out of bounds above/below the middle of a circle
def further_than_circles(position, circle_center, ball_center):
    # if ball is above center of top circle
    if position == 0:
        further = ball_center > circle_center
    # if ball is below center of bottom circle
    elif position == 1:
        further = ball_center < circle_center
    return(further)


def wait_for_keypress(key_list:list):
    continueRoutine = True
    while continueRoutine:
        theseKeys = event.getKeys(keyList=key_list)
        if len(theseKeys) > 0:  # at least one key was pressed
                # a response ends the routine
                continueRoutine = False


def run_instructions(instruct_text):
    instruct_text.draw()
    win.flip()
    wait_for_keypress(['space'])

def quit_psychopy():
    """Close everything and exit nicely (ending the experiment)
    """
    logging.flush()

    # properly shutdown ioHub server
    from psychopy.iohub.client import ioHubConnection

    if ioHubConnection.ACTIVE_CONNECTION:
        ioHubConnection.ACTIVE_CONNECTION.quit()

    for thisThread in threading.enumerate():
        if hasattr(thisThread, 'stop') and hasattr(thisThread, 'running'):
            # this is one of our event threads - kill it and wait for success
            thisThread.stop()
            while thisThread.running == 0:
                pass  # wait until it has properly finished polling

ball = visual.Circle(win, 
                    pos=(0,0), 
                    radius=0.03,
                    fillColor='white',
                    lineColor='white',
                    lineWidth=3)

ball.size *= scale

def calculate_ball_position(circle_reference_position, activation, ball_x_position, ball_y_position, outlier):
    # New cursor position (of ball) will be dot product of position (negative if DMN, positive if CEN) and activity (always positive)
    cursor_position = np.dot(circle_reference_position, activation)

    # only update ball position if the PDA metric isn't an outlier
    if not outlier:
        # The position of the target circle cumulatively adds the scaled cursor position on each frame
        ball_y_position =ball_y_position+ (np.real(cursor_position) * (scale_factor_z2pixels/internal_scaler) / tr_to_frame_ratio) 
        ball_x_position=ball_x_position+ (np.imag(cursor_position) * scale_factor_z2pixels/internal_scaler / tr_to_frame_ratio )
    
    ball_position=(ball_x_position,ball_y_position)
    return(ball_position)    


instruct_text = visual.TextStim(win=win, ori=0, name='instruct_text',
    text=u'replace me', font=u'Arial',
    pos=[0, 0], height=0.06, wrapWidth=1.2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "finish"
finishClock = core.Clock()
thank_you_end_run_text = visual.TextStim(win=win, ori=0, name='thank_you_end_run_text',
    text=u'thank you!',    font=u'Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

no_feedback_run1_text = f"Next, you will get to continue the Mindful Describing practice you just learned.\
    \n\nBefore, you mentioned using your {expInfo['anchor']} as an anchor for your Describing Practice. \
Try to continue using this as your anchor, but it is also okay to switch anytime.\
\n\nYou will see 2 circles with a white ball in the middle, but they won't move for now."

ready_text="You will see the plus sign (+) for 30 seconds at the start. \
Whenever you see the plus +, please don't practice Describing - just relax.\
\n\nOnce the circles appear, please start the Describing practice. \
This practice will last 2.5 min."

ready_text2="When you see the plus sign (+), just relax.\
\n\nOnce the circles appear, please start the Describing practice. \
This scan will last 2.5 min."

feedback_run1_text1 = "Great job! Now, you'll get to try moving the ball with your mindful describing practice! \
\n\nYou will see the 2 circles and white ball again. \
When the white ball moves up towards the top yellow circle, this means you are in a mindful brain state with your describing practice. \
\nIf the ball reaches either of the circles, it will move back to the center."

feedback_later_runs_text = "Great job! Now, you're going practice Mindful Describing for another 2.5min with more brain feedback from the ball. \
\n\nWhen the ball moves upwards, that corresponds to the describing practice."

no_feedback_later_runs_text = "Great job! Next, you'll get to practice Describing for another 2.5min. \
\nThis time the ball and circles will not move, so you don't need to check them."

# Depending on whether feedback is offered/which run it is -- show different instruction slides
if expInfo['feedback_on'] == "No Feedback":
    if int(expInfo['run']) == 1: 
        instruction_slide_list = [no_feedback_run1_text, ready_text]
    else:
        instruction_slide_list = [no_feedback_later_runs_text, ready_text2]
elif expInfo['feedback_on'] == 'Feedback':
    if int(expInfo['run']) == 1: 
        instruction_slide_list = [feedback_run1_text1, ready_text2]
    else:
        instruction_slide_list = [feedback_later_runs_text, ready_text2]


for instructions_slide in instruction_slide_list:
    instruct_text.setText(instructions_slide)
    run_instructions(instruct_text)


 #murfi communicator
from murfi_activation_communicator import MurfiActivationCommunicator
roi_names = ['cen', 'dmn']
# REPLACE THIS IP WITH THE MURFI COMPUTER'S IP 192.168.2.5, EXTERNAL STIMULUS COMPUTER IS 196.168.2.6, FOR RUNNING ALL ON THE SYSTEM76 COMPUTER USE INTERNAL IP 127.0.0.1
communicator = MurfiActivationCommunicator('127.0.0.1',
                                               15001, 210,
                                               roi_names,expInfo['tr'],murfi_FAKE)
print ("murfi communicator ok")

thisExp.addData('temporal_resolution', expInfo['tr'])


#------Prepare to start Routine "trigger"-------
t = 0
triggerClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
key_resp_3 = event.BuilderKeyResponse()  # create an object of type KeyResponse
key_resp_3.status = NOT_STARTED
# keep track of which components have finished
triggerComponents = []
triggerComponents.append(waiting_for_trigger_text)
triggerComponents.append(key_resp_3)
for thisComponent in triggerComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "trigger"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = triggerClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *waiting_for_trigger_text* updates
    if t >= 0.0 and waiting_for_trigger_text.status == NOT_STARTED:
        # keep track of start time/frame for later
        waiting_for_trigger_text.tStart = t  # underestimates by a little under one frame
        waiting_for_trigger_text.frameNStart = frameN  # exact frame index
        waiting_for_trigger_text.setAutoDraw(True)
    
    # *key_resp_3* updates
    if t >= 0.0 and key_resp_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_3.tStart = t  # underestimates by a little under one frame
        key_resp_3.frameNStart = frameN  # exact frame index
        key_resp_3.status = STARTED
        # keyboard checking is just starting
        key_resp_3.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if key_resp_3.status == STARTED:
        theseKeys = event.getKeys(keyList=['t','+','5', 5, 'equal', 'shift+=','num_equal','='])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            key_resp_3.keys = theseKeys[-1]  # just the last key pressed
            key_resp_3.rt = key_resp_3.clock.getTime()
            # a response ends the routine
            continueRoutine = False

            # reset trigger clock -- now it is keeping track of time relative to trigger!
            triggerClock.reset()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in triggerComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()
    else:  # this Routine was not non-slip safe so reset non-slip timer
        routineTimer.reset()

#-------Ending Routine "trigger"-------
for thisComponent in triggerComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if key_resp_3.keys in ['', [], None]:  # No response was made
   key_resp_3.keys=None
# store data for thisExp (ExperimentHandler)
thisExp.addData('key_resp_3.keys',key_resp_3.keys)
if key_resp_3.keys != None:  # we had a response
    thisExp.addData('key_resp_3.rt', key_resp_3.rt)
thisExp.nextEntry()

# BASELINE: wait for 30s before delivering feedback
#------Prepare to start Routine "baseline"-------
t = 0
baselineClock.reset()  # clock 
frameN = -1
frame = 0
routineTimer.addTime(BaseLineTime)
# update component parameters for each repeat
# keep track of which components have finished
baselineComponents = []
baselineComponents.append(text_2)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "baseline"-------
continueRoutine = True
print("starting baseline")
while continueRoutine and routineTimer.getTime() > 0:
    # During baseline period, we still want to record MURFI outputs
    # get current time
    communicator.update()
    roi_raw_activations=[]

    # Where ROI activation first comes in
    # CEN, DMN
    try:
        for i in range(n_roi):
            roi_raw_i=communicator.get_roi_activation(roi_names_list[i], frame)
            roi_raw_activations.append(roi_raw_i)
    except:
        print (f"Did not get data for frame {frame}")
        roi_raw_activations = [np.nan, np.nan]

    # check for any missing values (nan) in the roi_raw_activations pulled for the current frame
    # If there is a nan value, this most likely indicates that data hasn't been acquired yet for the current volume.
    # In this case, continue, and keep trying to acquire roi_raw_activations from MURFI (without advancing the frame)
    if np.isnan(roi_raw_activations[0]) or np.isnan(roi_raw_activations[1]):
        pass
    else:
        # If there is a new volume of output from MURFI, record it, and advance frame
        with open(filename+'_roi_outputs.csv', 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            print(([frame, triggerClock.getTime(), roi_raw_activations[0], roi_raw_activations[1]]))
            stim_writer.writerow([frame, expInfo['scale_factor'], triggerClock.getTime(), triggerClock.getTime() + 1.2, roi_raw_activations[0], roi_raw_activations[1], 'baseline', 0, 0, np.nan, np.nan, np.nan, np.nan])
        frame +=1


    t = baselineClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_2* updates
    if t >= 0.0 and text_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_2.tStart = t  # underestimates by a little under one frame
        text_2.frameNStart = frameN  # exact frame index
        text_2.setAutoDraw(True)
        text_relax.setAutoDraw(True)
    if text_2.status == STARTED and t >= (0.0 + (BaseLineTime-win.monitorFramePeriod*0.75)): #most of one frame period left
        pass
        
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in baselineComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "baseline"-------
text_2.setAutoDraw(False)
text_relax.setAutoDraw(False)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

#------Prepare to start Routine "feedback"-------
t = 0
feedbackClock.reset()  # clock 
frameN = -1
frame_save_counter = 0  # NEW: Track frames for selective saving

# update component parameters for each repeat
subject_key_target = event.BuilderKeyResponse()  # create an object of type KeyResponse
subject_key_target.status = NOT_STARTED
subject_key_reset = event.BuilderKeyResponse()  # create an object of type KeyResponse
subject_key_reset.status = NOT_STARTED
routineTimer.addTime(RUN_TIME)


# Initialize parameters before feedback
activity = 0
direction=0

# Draw initial stim positions
for i in range(n_roi):
    target_circles[i].draw()
ball.draw()
win.flip()

pda_outlier=False
frame_data = []  # List to store all frame details
#-------Start Routine "feedback"-------
# initialize last_acquired_frame_time
last_acquired_frame_time = feedbackClock.getTime()
continueRoutine = True
# Loop keeps going until RUN_TIME is up
while not (SHAM and expInfo['feedback_on'] == 'Feedback') and continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = feedbackClock.getTime()
    run_stop_time=t
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *subject_key_target* updates
    if t >= 0.0 and subject_key_target.status == NOT_STARTED:
        # keep track of start time/frame for later
        subject_key_target.tStart = t  # underestimates by a little under one frame
        subject_key_target.frameNStart = frameN  # exact frame index
        subject_key_target.status = STARTED
        # keyboard checking is just starting
        subject_key_target.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if subject_key_target.status == STARTED:
        theseKeys = event.getKeys(keyList=['escape'])
        theseKeys_num=theseKeys

        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            subject_key_target.keys = theseKeys[-1]  # just the last key pressed
            subject_key_target.rt = subject_key_target.clock.getTime()
    
    # get updated data from MURFI    
    communicator.update()
    roi_raw_activations=[]

    # Where ROI activation first comes in
    # CEN, DMN
    for i in range(n_roi):
        roi_raw_i=communicator.get_roi_activation(roi_names_list[i], frame)
        roi_raw_activations.append(roi_raw_i)
       
    '''
    Check for any missing values (nan) from MURFI on the current frame. If there is a nan value, this most likely
    indicates that data hasn't been acquired yet for the current volume. In this case, continue, and keep trying to acquire
    roi_raw_activations from MURFI (without advancing the frame). This will happen several times for each volume before the data 
    for the next volume are available. 
    '''
    if np.isnan(roi_raw_activations[0]) or np.isnan(roi_raw_activations[1]):
        # get timestamp
        non_new_data_time=feedbackClock.getTime()

        # if time is more than 10s after last_acquired_frame_time, quit task (this means no more data is flowing in)
        if non_new_data_time - last_acquired_frame_time > 10:
            print('ERROR: NO DATA ARRIVING FROM MURFI! Is this a MoCo issue?')
            print(f'quit at {non_new_data_time} since there were no new frames since {last_acquired_frame_time}')
            continueRoutine=False
 

    # a list of [CEN, DMN] for the current frame
    else:
        roi_activities=roi_raw_activations

        # get a timestamp for last_acquired_frame_time
        last_acquired_frame_time = feedbackClock.getTime()
        print(last_acquired_frame_time)

        if np.nanmax(np.abs(roi_activities)) > expInfo['pda_outlier_threshold']:
            pda_outlier=True
            num_pda_outliers+=1
        else:
            pda_outlier=False

        print('time: ', routineTimer.getTime())
        print ("got feedback at frame : ",  frame, roi_raw_activations, roi_names_list)
        
        '''
        Loop through ROIs. Depending on which one has higher activity, change direction parameter 
        1 - upwards (when CEN higher)
        -1 = downwards (when DMN higher)
        '''
        for i in range(n_roi):
            target_circles[i].fillColor=None
            # for each ROI, look for the index -- see whether that ROI has the highest activity
            if roi_activities.index(np.nanmax(roi_activities))==i and np.nanmean(roi_activities)!=0:
                # Activity=absolute difference between ROI activations (always positive)
                activity=abs(np.nanmax(roi_activities)-(np.nanmin(roi_activities)))/10
                print ("activity",activity, " roi_activities",roi_activities)

                # activity will always be positive (PDA)
                # positions refers to either CEN position positions[0] or DMN position positions[1]
                print('Circle positions:', target_circles[0].pos[1], target_circles[1].pos[1])
                print ("direction -->", roi_names_list[i])
                print (roi_names_list[0],"hits: ",hit_counter[0], '   ', roi_names_list[1],"hits: ",hit_counter[1])
                direction = positions[i]

            # if the ball has passed the middle of either target circle, put position back to 0
            if further_than_circles(position=i, 
                circle_center=target_circles[i].pos[1], 
                ball_center=ball.pos[1]):

                # increment hit count
                hit_counter[i]=hit_counter[i]+1
                print('HIT', roi_names_list[i])
                ball.pos = (0,0)

                # for each hit, position of target circle moves away from the middle (up to a point)
                if circles_move_with_hits:
                    if np.abs(target_circles[i].pos[1]) + target_circles[i].radius + 0.1 < 1:
                        target_circles[i].pos=((target_circles[i].pos[0]*1.1), (target_circles[i].pos[1]*1.1))
                if circle_radius_shrink_with_hits:
                    target_circles[i].radius = np.maximum(target_circles[i].radius*.9, 0.03)

                target_circles[i].fillColor='white'


        # Save info to outfile for each volume       
        with open(filename+'_roi_outputs.csv', 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if frame % 10 == 0:  # Print every 10th frame
                print(([frame, triggerClock.getTime(), roi_raw_activations[0], roi_raw_activations[1]]))
            stim_writer.writerow([frame, expInfo['scale_factor'], triggerClock.getTime(), triggerClock.getTime() + 1.2, roi_raw_activations[0], roi_raw_activations[1], 'feedback', hit_counter[0], hit_counter[1], pda_outlier, ball.pos[1], target_circles[0].pos[1], target_circles[1].pos[1]])

        # Increment the frame
        frame += 1
    
    # calculate next ball position
    pause_ball_movement=False
    for i in range(n_roi):
        if further_than_circles(position=i, 
                    circle_center=target_circles[i].pos[1], 
                    ball_center=ball.pos[1]):
            pause_ball_movement=True

    if not pause_ball_movement:
        ball.pos = calculate_ball_position(circle_reference_position=direction, activation=activity, ball_x_position=ball.pos[0], ball_y_position=ball.pos[1], outlier=pda_outlier)             

    # Draw stimuli (if on feedback mode)
    if expInfo['feedback_on'] == 'Feedback':
        for i in range(n_roi):
            target_circles[i].draw()
        ball.draw()
        
        # flip window
        win.flip()
        
        # OPTIMIZATION: Only save every 5th frame (~30fps instead of 144fps)
        # This reduces file size by 80% with no perceptible visual difference
        frame_save_counter += 1
        if frame_save_counter % 5 == 0:
            frame_info = {}
            # Store frame data including details for all circles and the ball
            # Save ball attributes as before
            frame_info["time"] = globalClock.getTime()
            frame_info["ball_x"] = ball.pos[0]
            frame_info["ball_y"] = ball.pos[1]
            frame_info["ball_radius"] = ball.radius
            
            # Here, if ball.fillColor is a string, save it as is:
            if ball.fillColor is None:
                ball_fill = [-1, -1, -1]  # black
            else:
                ball_fill = ball.fillColor
            frame_info["ball_color_r"] = ball_fill[0]
            frame_info["ball_color_g"] = ball_fill[1]
            frame_info["ball_color_b"] = ball_fill[2]
            
            # Save details for each of the ROIs (target circles)
            for i, roi in enumerate(target_circles):
                frame_info[f"roi{i + 1}_x"] = roi.pos[0]
                frame_info[f"roi{i + 1}_y"] = roi.pos[1]
                frame_info[f"roi{i + 1}_radius"] = roi.radius
                
                # Fill Color
                if roi.fillColor is None:
                    # Force black for 'no fill' to ensure no mid-gray
                    fill_color = [-1, -1, -1]
                else:
                    fill_color = roi.fillColor
                    
                # If fill_color is [0,0,0] for some reason, also force it to black
                if (fill_color[0] == 0 and fill_color[1] == 0 and fill_color[2] == 0):
                    fill_color = [-1, -1, -1]
                    
                frame_info[f"roi{i + 1}_color_r"] = fill_color[0]
                frame_info[f"roi{i + 1}_color_g"] = fill_color[1]
                frame_info[f"roi{i + 1}_color_b"] = fill_color[2]
                
                # Line Color
                line_color = roi.lineColor
                frame_info[f"roi{i + 1}_lineColor_r"] = line_color[0]
                frame_info[f"roi{i + 1}_lineColor_g"] = line_color[1]
                frame_info[f"roi{i + 1}_lineColor_b"] = line_color[2]
            
            frame_data.append(frame_info)
    
    # quit if escape pressed
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    

#END OF FEEDBACK LOOP

# OPTIMIZED SHAM feedback display - Smooth interpolation with correct timing and VIRTUAL HIT COUNTING
if SHAM and expInfo['feedback_on'] == 'Feedback':
    # Load the sham feedback CSV
    df_sham = pd.read_csv(csv_file)
    
    # Compute offset: first frame's time value
    time_offset = df_sham.iloc[0]["time"]
    
    # DEBUG: Check timing
    print(f"First frame time: {df_sham.iloc[0]['time']:.3f}s")
    print(f"Last frame time: {df_sham.iloc[-1]['time']:.3f}s")
    print(f"Time offset: {time_offset:.3f}s")
    print(f"Adjusted duration: {df_sham.iloc[-1]['time'] - time_offset:.3f}s")
    
    # Set run_stop_time to pass the check for slider questions
    run_stop_time = 100
    
    # Start a dedicated playback clock
    playbackClock = core.Clock()
    playbackClock.reset()
    
    # OPTIMIZATION: Downsample to 60Hz for smooth playback
    frame_diffs = df_sham['time'].diff()
    avg_frame_interval = frame_diffs.mean()
    current_fps = 1.0 / avg_frame_interval if avg_frame_interval > 0 else 144
    
    if current_fps > 90:
        downsample_factor = int(current_fps / 60)
        df_sham = df_sham.iloc[::downsample_factor].reset_index(drop=True)
        print(f"Downsampled from {current_fps:.1f}Hz to ~60Hz")
        print(f"Reduced from {len(df_sham)*downsample_factor} to {len(df_sham)} frames")
    
    # Pre-convert to numpy arrays for faster access
    ball_data = {
        'x': df_sham['ball_x'].values,
        'y': df_sham['ball_y'].values,
        'radius': df_sham['ball_radius'].values,
        'color_r': df_sham['ball_color_r'].values,
        'color_g': df_sham['ball_color_g'].values,
        'color_b': df_sham['ball_color_b'].values
    }
    
    roi_data = []
    for i in range(n_roi):
        roi_data.append({
            'x': df_sham[f'roi{i+1}_x'].values,
            'y': df_sham[f'roi{i+1}_y'].values,
            'radius': df_sham[f'roi{i+1}_radius'].values,
            'color_r': df_sham[f'roi{i+1}_color_r'].values,
            'color_g': df_sham[f'roi{i+1}_color_g'].values,
            'color_b': df_sham[f'roi{i+1}_color_b'].values,
            'line_r': df_sham[f'roi{i+1}_lineColor_r'].values,
            'line_g': df_sham[f'roi{i+1}_lineColor_g'].values,
            'line_b': df_sham[f'roi{i+1}_lineColor_b'].values
        })
    
    frame_times = df_sham['time'].values - time_offset
    
    # Filter to include all frames (let MURFI collection continue until data stops)
    num_valid_frames = len(df_sham)  # Use all downsampled frames
    max_playback_time = frame_times[-1]  # Will run for full duration
    
    print(f"Filtered to {num_valid_frames} frames within {max_playback_time:.1f}s")
    print(f"Starting SHAM playback with VIRTUAL hit counting")
    
    # NEW: Initialize virtual hit counters for SHAM
    sham_virtual_cen_hits = 0
    sham_virtual_dmn_hits = 0
    
    # NEW: Track virtual ball position based on SHAM's actual brain activity
    virtual_ball_y = 0.0
    virtual_ball_x = 0.0
    
    # Loop only over valid frames (within 150s window)
    for idx in range(num_valid_frames):
        
        # Check if Esc was pressed
        if event.getKeys(keyList=["escape"]):
            core.quit()
        
        # Check MURFI on every iteration to ensure we don't miss volumes
        communicator.update()
        roi_raw_activations = []
        
        try:
            for i in range(n_roi):
                roi_raw_i = communicator.get_roi_activation(roi_names_list[i], frame)
                roi_raw_activations.append(roi_raw_i)
        except:
            roi_raw_activations = [np.nan, np.nan]
        
        # Check for valid data
        if len(roi_raw_activations) >= 2 and not (np.isnan(roi_raw_activations[0]) or np.isnan(roi_raw_activations[1])):
            
            # NEW: Calculate what WOULD happen with SHAM's actual brain activity
            roi_activities = roi_raw_activations
            
            # Check for outlier
            if np.nanmax(np.abs(roi_activities)) > expInfo['pda_outlier_threshold']:
                pda_outlier_sham = True
            else:
                pda_outlier_sham = False
            
            # Calculate virtual ball movement based on SHAM's actual brain activity
            # (Same logic as REAL mode, matching frame-by-frame updates)
            if not pda_outlier_sham:
                # Determine direction and activity
                max_roi_idx = roi_activities.index(np.nanmax(roi_activities))
                if np.nanmean(roi_activities) != 0:
                    activity_sham = abs(np.nanmax(roi_activities) - np.nanmin(roi_activities)) / 10
                    direction_sham = positions[max_roi_idx]
                    
                    # Calculate virtual cursor position
                    cursor_position_sham = np.dot(direction_sham, activity_sham)
                    
                    # Simulate frame-by-frame updates to match REAL mode exactly
                    # In REAL mode, the ball updates every frame (~60 Hz)
                    # We need to simulate tr_to_frame_ratio frames of movement
                    num_frames_per_tr = int(tr_to_frame_ratio)
                    delta_per_frame_y = (np.real(cursor_position_sham) * 
                                        (scale_factor_z2pixels/internal_scaler) / tr_to_frame_ratio)
                    delta_per_frame_x = (np.imag(cursor_position_sham) * 
                                        scale_factor_z2pixels/internal_scaler / tr_to_frame_ratio)
                    
                    # Apply the movement across all frames in this TR
                    for frame_idx in range(num_frames_per_tr):
                        virtual_ball_y += delta_per_frame_y
                        virtual_ball_x += delta_per_frame_x
                        
                        # Check for virtual hits after each simulated frame (matching REAL mode)
                        # CEN (top circle, position 0) - check if virtual ball is above center
                        if virtual_ball_y > target_circles[0].pos[1]:
                            sham_virtual_cen_hits += 1
                            print(f'VIRTUAL HIT: CEN (frame {frame}, simulated frame {frame_idx})')
                            virtual_ball_y = 0.0  # Reset virtual ball
                            virtual_ball_x = 0.0
                            break  # Stop simulating frames in this TR after hit
                        
                        # DMN (bottom circle, position 1) - check if virtual ball is below center  
                        elif virtual_ball_y < target_circles[1].pos[1]:
                            sham_virtual_dmn_hits += 1
                            print(f'VIRTUAL HIT: DMN (frame {frame}, simulated frame {frame_idx})')
                            virtual_ball_y = 0.0  # Reset virtual ball
                            virtual_ball_x = 0.0
                            break  # Stop simulating frames in this TR after hit
            
            # Save to CSV with VIRTUAL hit counts
            with open(filename + '_roi_outputs.csv', 'a') as csvfile:
                stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                print([frame, triggerClock.getTime(), roi_raw_activations[0], 
                       roi_raw_activations[1], f'Virtual hits: CEN={sham_virtual_cen_hits}, DMN={sham_virtual_dmn_hits}'])
                stim_writer.writerow(
                    [frame, expInfo['scale_factor'], triggerClock.getTime(), triggerClock.getTime() + 1.2,
                     roi_raw_activations[0], roi_raw_activations[1], 'feedback', 
                     sham_virtual_cen_hits, sham_virtual_dmn_hits,  # <-- VIRTUAL hit counts!
                     pda_outlier_sham, virtual_ball_y, target_circles[0].pos[1], target_circles[1].pos[1]])
            frame += 1
        
        # Update ball using numpy arrays - SMOOTH 60Hz interpolation
        # This is the VISUAL feedback (yoked from matched participant)
        ball.pos = (ball_data['x'][idx], ball_data['y'][idx])
        ball.radius = ball_data['radius'][idx]
        ball.fillColor = [
            ball_data['color_r'][idx],
            ball_data['color_g'][idx],
            ball_data['color_b'][idx]
        ]
        
        # Update circles using numpy arrays
        for i, circle in enumerate(target_circles):
            circle.pos = (roi_data[i]['x'][idx], roi_data[i]['y'][idx])
            circle.radius = roi_data[i]['radius'][idx]
            circle.fillColor = [
                roi_data[i]['color_r'][idx],
                roi_data[i]['color_g'][idx],
                roi_data[i]['color_b'][idx]
            ]
            circle.lineColor = [
                roi_data[i]['line_r'][idx],
                roi_data[i]['line_g'][idx],
                roi_data[i]['line_b'][idx]
            ]
        
        # Draw all elements (YOKED visual feedback)
        for circle in target_circles:
            circle.draw()
        ball.draw()
        win.flip()
        
        # Timing control for smooth playback
        target_time = frame_times[idx]
        current_time = playbackClock.getTime()
        wait_time = target_time - current_time
        if wait_time > 0:
            core.wait(wait_time)
    
    actual_playback_time = playbackClock.getTime()
    print(f"SHAM visual playback complete in {actual_playback_time:.1f}s")
    print(f"SHAM VIRTUAL HITS: CEN={sham_virtual_cen_hits}, DMN={sham_virtual_dmn_hits}")
    print(f"Waiting for final MURFI volumes...")
    
    # Wait for last MURFI volumes to arrive (up to 5 TRs worth of time)
    wait_start = playbackClock.getTime()
    max_wait_time = expInfo['tr'] * 5  # 6 seconds for TR=1.2
    target_volumes = 150  # We want exactly 150 total volumes
    
    while (playbackClock.getTime() - wait_start < max_wait_time) and (frame < target_volumes):
        communicator.update()
        roi_raw_activations = []
        
        try:
            for i in range(n_roi):
                roi_raw_i = communicator.get_roi_activation(roi_names_list[i], frame)
                roi_raw_activations.append(roi_raw_i)
        except:
            roi_raw_activations = [np.nan, np.nan]
        
        if len(roi_raw_activations) >= 2 and not (np.isnan(roi_raw_activations[0]) or np.isnan(roi_raw_activations[1])):
            
            # Continue virtual hit counting in post-playback phase
            roi_activities = roi_raw_activations
            
            if np.nanmax(np.abs(roi_activities)) > expInfo['pda_outlier_threshold']:
                pda_outlier_sham = True
            else:
                pda_outlier_sham = False
            
            if not pda_outlier_sham:
                max_roi_idx = roi_activities.index(np.nanmax(roi_activities))
                if np.nanmean(roi_activities) != 0:
                    activity_sham = abs(np.nanmax(roi_activities) - np.nanmin(roi_activities)) / 10
                    direction_sham = positions[max_roi_idx]
                    
                    cursor_position_sham = np.dot(direction_sham, activity_sham)
                    
                    # Simulate frame-by-frame updates to match REAL mode
                    num_frames_per_tr = int(tr_to_frame_ratio)
                    delta_per_frame_y = (np.real(cursor_position_sham) * 
                                        (scale_factor_z2pixels/internal_scaler) / tr_to_frame_ratio)
                    delta_per_frame_x = (np.imag(cursor_position_sham) * 
                                        scale_factor_z2pixels/internal_scaler / tr_to_frame_ratio)
                    
                    for frame_idx in range(num_frames_per_tr):
                        virtual_ball_y += delta_per_frame_y
                        virtual_ball_x += delta_per_frame_x
                        
                        if virtual_ball_y > target_circles[0].pos[1]:
                            sham_virtual_cen_hits += 1
                            print(f'VIRTUAL HIT: CEN (frame {frame}, simulated frame {frame_idx})')
                            virtual_ball_y = 0.0
                            virtual_ball_x = 0.0
                            break
                        elif virtual_ball_y < target_circles[1].pos[1]:
                            sham_virtual_dmn_hits += 1
                            print(f'VIRTUAL HIT: DMN (frame {frame}, simulated frame {frame_idx})')
                            virtual_ball_y = 0.0
                            virtual_ball_x = 0.0
                            break
            
            with open(filename + '_roi_outputs.csv', 'a') as csvfile:
                stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                print([frame, triggerClock.getTime(), roi_raw_activations[0], roi_raw_activations[1]])
                stim_writer.writerow(
                    [frame, expInfo['scale_factor'], triggerClock.getTime(), triggerClock.getTime() + 1.2,
                     roi_raw_activations[0], roi_raw_activations[1], 'feedback', 
                     sham_virtual_cen_hits, sham_virtual_dmn_hits, 
                     pda_outlier_sham, virtual_ball_y, target_circles[0].pos[1], target_circles[1].pos[1]])
            frame += 1
        
        core.wait(0.1)  # Small wait between checks
    
    print(f"SHAM playback complete. Collected {frame} volumes total")
    print(f"FINAL SHAM VIRTUAL HITS: CEN={sham_virtual_cen_hits}, DMN={sham_virtual_dmn_hits}")
    if frame < target_volumes:
        print(f"WARNING: Expected {target_volumes} volumes but only got {frame}")

# End SHAM feedback loop

# If feedback was displayed, save frame data
if expInfo['feedback_on'] == 'Feedback':
    df = pd.DataFrame(frame_data)
    csv_filename = filename+'_frames.csv'
    df.to_csv(csv_filename, index=False)
    print(f"Feedback frames saved to {csv_filename}")
    
    # If REAL participant, copy to feedback directory for SHAM use
    if not SHAM:
        feedback_dir = os.path.join('feedback', filename_prefix + expInfo['participant'])
        if not os.path.exists(feedback_dir):
            os.makedirs(feedback_dir)
        
        feedback_frames_file = os.path.join(feedback_dir, os.path.basename(csv_filename))
        shutil.copy2(csv_filename, feedback_frames_file)
        print(f"Copied frames to feedback directory: {feedback_frames_file}")

#------Prepare to start Routine "baseline"-------
t = 0
baselineClock.reset()  # clock 
frameN = -1
routineTimer.addTime(1.00000)
# update component parameters for each repeat
# keep track of which components have finished
baselineComponents = []
baselineComponents.append(text_2)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "baseline"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = baselineClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *text_2* updates
    if t >= 0.0 and text_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_2.tStart = t  # underestimates by a little under one frame
        text_2.frameNStart = frameN  # exact frame index
        text_2.setAutoDraw(True)
    if text_2.status == STARTED and t >= (0.0 + (1-win.monitorFramePeriod*0.75)): #most of one frame period left
        text_2.setAutoDraw(False)

# check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in baselineComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

# check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()

# refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "baseline"-------
for thisComponent in baselineComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
    
  
 
#------Prepare to start Routine "finish"-------
t = 0
finishClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
# keep track of which components have finished
finishComponents = []
finishComponents.append(thank_you_end_run_text)
for thisComponent in finishComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# Ask slider questions only if halfway through the run or more (60s into feedback)
if run_stop_time >= 60:
    slider_instruction.draw()
    win.flip()
    wait_for_keypress(key_list=[right_button, left_button, enter_button])

    run_slider(question_text='How often were you using the Mindful Describing practice?',
                    left_label='Never', right_label='Always')
    run_slider(question_text='How often did you check the position of the ball?',
                    left_label='Never', right_label='All the time')
    run_slider(question_text='How difficult was it to apply Mindful Describing?',
                    left_label='Not at all', right_label='Very Difficult')
    run_slider(question_text='How calm do you feel right now?',
                    left_label='Not at all', right_label='Very calm')
    if expInfo['run'] == '5' and expInfo['feedback_on'] == 'Feedback':  # last feedback run
        run_slider(question_text='The ball seemed to move up while I was practicing Mindful Describing',
                   left_label='False', right_label='True')
        run_slider(question_text='The ball seemed to move down while my mind was wandering.',
                   left_label='False', right_label='True')
        run_slider(question_text='The ball seemed to move down while I was trying to control it.',
                   left_label='False', right_label='True')
else:
    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How often were you using the Mindful Describing practice?', np.nan, np.nan])

    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How often did you check the position of the ball?', np.nan, np.nan])  
    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How difficult was it to apply Mindful Describing', np.nan, np.nan])

    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How calm do you feel right now?', np.nan, np.nan])

    if expInfo['run'] == '5' and expInfo['feedback_on'] == 'Feedback':  # last feedback run
        with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'The ball seemed to move up while I was practicing Mindful Describing', np.nan,
                                  np.nan])

        with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'The ball seemed to move down while my mind was wandering.', np.nan, np.nan])

        with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'The ball seemed to move down while I was trying to control it.', np.nan, np.nan])


# Convert csv output to BIDS-format tsv
convert_balltask_csv_to_bids(infile = f'{filename}_roi_outputs.csv')

# display ending text and close window
thank_you_end_run_text.draw()
win.flip()
core.wait(3)
win.close()


# Set variables for the next run
if expInfo['run'] == '1' and expInfo['feedback_on'] == 'No Feedback':
    next_run =1
    next_feedback= 'Feedback'
elif expInfo['run'] == '2' and expInfo['feedback_on'] == 'No Feedback': 
    next_run =6
    next_feedback = 'Feedback'
elif expInfo['run'] == '5':
    next_run =2
    next_feedback='No'
elif expInfo['run'] == '10':
    next_run =3
    next_feedback='No'
else:
    next_run = int(expInfo['run']) + 1
    next_feedback='Feedback'

next_participant=expInfo['participant']
anchor = expInfo['anchor']
next_feedback_condition = expInfo['feedback_condition']

# Shut down psychopy before starting next run
quit_psychopy()


next_randomization = expInfo['randomization']

if expInfo['feedback_condition'] == '15min':
    if next_run < 6:
        subprocess.Popen(["bash", "reopen_balltask_mgh.sh", str(next_participant), str(next_randomization),
            str(next_run), str(next_feedback), str(next_feedback_condition), str(anchor)])
    else:
        print('Syncing complete. Study session finished.')
elif expInfo['feedback_condition'] == '30min':
    subprocess.Popen(["bash", "reopen_balltask_mgh.sh", str(next_participant), str(next_randomization),
        str(next_run), str(next_feedback), str(next_feedback_condition), str(anchor)])

# Quit python
sys.exit('Done with run')
