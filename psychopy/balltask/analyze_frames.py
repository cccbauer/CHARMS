#!/usr/bin/env python3
"""
Analyze the frames and ROI output files to diagnose timing issues
"""

import pandas as pd
import numpy as np
import sys
import os

def analyze_run_files(base_filename):
    """
    Analyze both the frames file and ROI outputs file
    
    Parameters:
    -----------
    base_filename : str
        Base filename without extension (e.g., "data/sub-charms201/sub-charms201_DMN_feedback_1")
    """
    
    frames_file = base_filename + "_frames.csv"
    roi_file = base_filename + "_roi_outputs.csv"
    
    print("\n" + "="*80)
    print("ANALYZING NEUROFEEDBACK RUN FILES")
    print("="*80)
    
    # Check if files exist
    frames_exists = os.path.exists(frames_file)
    roi_exists = os.path.exists(roi_file)
    
    if frames_exists:
        print(f"\n✓ Found frames file: {frames_file}")
    else:
        print(f"\n✗ Frames file not found: {frames_file}")
        
    if roi_exists:
        print(f"✓ Found ROI file: {roi_file}")
    else:
        print(f"✗ ROI outputs file not found: {roi_file}")
    
    if not frames_exists and not roi_exists:
        print("\n❌ ERROR: Neither file found!")
        return None, None
    
    # Load the files
    df_frames = None
    df_roi = None
    
    if frames_exists:
        try:
            df_frames = pd.read_csv(frames_file)
            print(f"\n✓ Successfully loaded frames file")
        except Exception as e:
            print(f"\n❌ ERROR loading frames file: {e}")
    
    if roi_exists:
        try:
            df_roi = pd.read_csv(roi_file)
            print(f"✓ Successfully loaded ROI file")
        except Exception as e:
            print(f"❌ ERROR loading ROI file: {e}")
    
    # Analyze ROI outputs (these are the actual TRs/volumes)
    if df_roi is not None:
        print("\n" + "-"*80)
        print("ROI OUTPUTS (MURFI Data - One row per TR)")
        print("-"*80)
        
        print(f"\nTotal volumes recorded: {len(df_roi)}")
        print(f"Columns: {list(df_roi.columns)}")
        
        # Check stages
        if 'stage' in df_roi.columns:
            baseline_vols = len(df_roi[df_roi['stage'] == 'baseline'])
            feedback_vols = len(df_roi[df_roi['stage'] == 'feedback'])
            print(f"\nBaseline volumes: {baseline_vols}")
            print(f"Feedback volumes: {feedback_vols}")
            print(f"Total: {baseline_vols + feedback_vols}")
        
        # Check timing
        if 'time' in df_roi.columns:
            print(f"\nTiming:")
            print(f"  First volume time: {df_roi['time'].iloc[0]:.3f} s")
            print(f"  Last volume time: {df_roi['time'].iloc[-1]:.3f} s")
            print(f"  Total duration: {df_roi['time'].iloc[-1] - df_roi['time'].iloc[0]:.3f} s")
            
            # Calculate TR
            time_diffs = df_roi['time'].diff().dropna()
            mean_tr = time_diffs.mean()
            print(f"  Average TR: {mean_tr:.3f} s")
            print(f"  TR std dev: {time_diffs.std():.3f} s")
            print(f"  Min TR: {time_diffs.min():.3f} s")
            print(f"  Max TR: {time_diffs.max():.3f} s")
        
        # Check for expected volumes with TR=1.2
        if 'stage' in df_roi.columns and len(df_roi) > 0:
            # Get scale_factor from first row to infer TR
            if 'time' in df_roi.columns:
                expected_baseline = 30 / mean_tr  # 30 seconds baseline
                expected_feedback = 150 / mean_tr  # 150 seconds feedback
                expected_total = expected_baseline + expected_feedback
                
                print(f"\nExpected volumes (based on measured TR={mean_tr:.2f}s):")
                print(f"  Baseline: {expected_baseline:.1f} volumes")
                print(f"  Feedback: {expected_feedback:.1f} volumes")
                print(f"  Total: {expected_total:.1f} volumes")
                print(f"\n  Actual - Expected = {len(df_roi) - expected_total:.1f} volumes")
                
                if len(df_roi) < expected_total - 2:
                    print(f"  ⚠️  WARNING: Missing {expected_total - len(df_roi):.1f} volumes!")
                elif len(df_roi) > expected_total + 2:
                    print(f"  ⚠️  WARNING: {len(df_roi) - expected_total:.1f} extra volumes!")
                else:
                    print(f"  ✓ Volume count looks good!")
        
        # Check hits
        if 'cen_cumulative_hits' in df_roi.columns and 'dmn_cumulative_hits' in df_roi.columns:
            final_cen_hits = df_roi['cen_cumulative_hits'].max()
            final_dmn_hits = df_roi['dmn_cumulative_hits'].max()
            print(f"\nFinal hit counts:")
            print(f"  CEN hits: {final_cen_hits}")
            print(f"  DMN hits: {final_dmn_hits}")
            print(f"  Total hits: {final_cen_hits + final_dmn_hits}")
        
        # Show last few volumes
        print("\n" + "-"*80)
        print("LAST 5 VOLUMES (from ROI outputs)")
        print("-"*80)
        if 'volume' in df_roi.columns:
            print(df_roi[['volume', 'time', 'cen', 'dmn', 'stage']].tail(5).to_string(index=False))
        else:
            print(df_roi[['time', 'cen', 'dmn', 'stage']].tail(5).to_string(index=False))
    
    # Analyze frames file (display frames)
    if df_frames is not None:
        print("\n" + "-"*80)
        print("DISPLAY FRAMES (Visual feedback - Many rows per TR)")
        print("-"*80)
        
        print(f"\nTotal display frames: {len(df_frames)}")
        
        if 'time' in df_frames.columns:
            print(f"\nTiming:")
            print(f"  First frame time: {df_frames['time'].iloc[0]:.3f} s")
            print(f"  Last frame time: {df_frames['time'].iloc[-1]:.3f} s")
            print(f"  Total duration: {df_frames['time'].iloc[-1] - df_frames['time'].iloc[0]:.3f} s")
            
            # Calculate frame rate
            frame_diffs = df_frames['time'].diff().dropna()
            mean_frame_interval = frame_diffs.mean()
            frame_rate = 1.0 / mean_frame_interval if mean_frame_interval > 0 else 0
            print(f"  Average frame interval: {mean_frame_interval*1000:.2f} ms")
            print(f"  Estimated frame rate: {frame_rate:.1f} Hz")
            
            # Expected number of frames
            total_duration = df_frames['time'].iloc[-1] - df_frames['time'].iloc[0]
            expected_frames = total_duration * frame_rate
            print(f"\n  Expected frames at {frame_rate:.1f}Hz for {total_duration:.1f}s: {expected_frames:.0f}")
            print(f"  Actual frames: {len(df_frames)}")
            
            # Check if duration is too long
            if total_duration > 155:
                print(f"\n  ⚠️  WARNING: Frames duration ({total_duration:.1f}s) is longer than expected (~150s)!")
                print(f"     This will cause SHAM playback to run too long!")
        
        # Show last few frames
        print("\n" + "-"*80)
        print("LAST 5 DISPLAY FRAMES (from frames file)")
        print("-"*80)
        print(df_frames[['time', 'ball_x', 'ball_y']].tail(5).to_string(index=False))
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")
    
    return df_frames, df_roi


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_frames.py <base_filename>")
        print("\nExample:")
        print("  python analyze_frames.py data/sub-charms201/sub-charms201_DMN_feedback_1")
        print("\nOr with just the frames file:")
        print("  python analyze_frames.py data/sub-charms201/sub-charms201_DMN_feedback_1_frames.csv")
        sys.exit(1)
    
    base_filename = sys.argv[1]
    
    # Remove extension if provided
    if base_filename.endswith('_frames.csv'):
        base_filename = base_filename.replace('_frames.csv', '')
    elif base_filename.endswith('_roi_outputs.csv'):
        base_filename = base_filename.replace('_roi_outputs.csv', '')
    elif base_filename.endswith('.csv'):
        base_filename = base_filename.replace('.csv', '')
    
    df_frames, df_roi = analyze_run_files(base_filename)
