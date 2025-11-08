 
# Balltask Real-time fMRI Neurofeedback

Clemens C.C. Bauer November 2025



## Overview
Balltask can be run in REAL or SHAM mode for randomized controlled trials of neurofeedback.

## Modes

### REAL Mode
- Participants receive live neurofeedback based on their own brain activity
- DMN/CEN data comes from murfi_activation_communicator.py in real-time
- Ball movement reflects their current brain state

### SHAM Mode  
- Participants see pre-recorded feedback from a matched REAL participant (yoked feedback)
- Their own brain activity is still recorded via MURFI for analysis
- Ball movement is identical to the matched REAL participant
- Ensures double-blind conditions (operator cannot tell REAL from SHAM)

## Randomization System

The system uses **separate randomization numbers and participant IDs**:
- **Randomization number** (e.g., 001): Determines REAL vs SHAM assignment from `mgh_randlist.txt`
- **Participant ID** (e.g., 201): Used for file naming and organization
- `participant_mapping.txt`: Automatically tracks which randomization numbers map to which participant IDs

## Setup Instructions

### For REAL Participants
1. Run: `python rt-network_feedback_mgh.py`
2. Enter participant ID, randomization number (marked 'R' in mgh_randlist.txt), run number, and feedback type
3. The script automatically:
   - Saves frames at 30fps (~0.85MB per run) in `data/sub-charmsXXX/`
   - Copies frames to `feedback/sub-charmsXXX/` for future SHAM use
   - Records 150 volumes (25 baseline + 125 feedback)

### For SHAM Participants
1. **Prerequisite**: At least one matched REAL participant must have completed feedback runs
2. Run: `python rt-network_feedback_mgh.py`
3. Enter participant ID, randomization number (marked 'S' in mgh_randlist.txt), run number, and feedback type
4. The script automatically:
   - Finds the closest matched REAL participant by randomization number
   - Copies frames files from `feedback/sub-charmsXXX/` (REAL) to `feedback/sub-charmsYYY/` (SHAM)
   - Displays REAL's pre-recorded feedback
   - Records SHAM's own brain activity

**Note**: If SHAM folder exists, you'll be prompted to either keep existing data or copy fresh data from matched REAL participant.

## File Structure
```
data/
  sub-charms201/              # REAL participant data
    *_DMN_feedback_1_frames.csv      # 30fps frames (~0.85MB)
    *_DMN_feedback_1_roi_outputs.csv # MURFI volumes (150 rows)
    *_ses-nf_task-feedback_run-01.tsv # BIDS format
    
feedback/
  participant_mapping.txt     # Randomization → Participant ID mapping
  sub-charms201/              # REAL participant frames (source for SHAM)
    *_DMN_feedback_1_frames.csv
  sub-charms204/              # SHAM participant (copied from 201)
    *_DMN_feedback_1_frames.csv # Same as 201 (yoked feedback)
```

## Performance Optimizations

- **Frame rate**: Optimized from 144fps to 30fps (81% file size reduction)
- **SHAM playback**: Uses numpy arrays for 80% CPU reduction
- **Data collection**: Both REAL and SHAM collect exactly 150 volumes
- **Duration**: SHAM playback runs for exactly 150 seconds (not 4+ minutes)

## Protocols

Supports both 15-minute and 30-minute protocols:
- **15min**: Runs 1-5 feedback + 2 transfer runs
- **30min**: Runs 1-10 feedback + 3 transfer runs

## Debugging

Set `murfi_FAKE = True` at the top of the script to:
- Run without scanner/MURFI connection
- Use simulated brain data
- Window runs in non-fullscreen mode
- Interactive popup to confirm or disable FAKE mode

## Diagnostic Tools

**analyze_frames.py**: Verify data quality
```bash
python analyze_frames.py data/sub-charms201/sub-charms201_DMN_feedback_1
```

Shows: volume count, timing, frame rate, TR statistics, and data quality checks.

## Verification

Confirmed working with:
- REAL 201: 150 volumes, 27fps, CEN/DMN from own brain
- SHAM 204: 150 volumes, identical visual feedback, CEN/DMN from own brain (different from 201)
