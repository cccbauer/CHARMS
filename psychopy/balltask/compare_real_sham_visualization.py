#!/usr/bin/env python3
"""
Visualization script to compare REAL vs SHAM participants
Shows what they saw (ball movement) vs their actual brain activity (DMN/CEN)

Usage:
    python compare_real_sham_visualization.py --real 2098 --sham 2099 --run 1
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
from pathlib import Path

def load_participant_data(participant_id, run_number, data_type='roi_outputs', study='auto'):
    """
    Load data for a participant
    
    Parameters:
    -----------
    participant_id : str or int
        Participant ID (e.g., 2098 for MIND-BPD, 098 for CHARMS)
    run_number : int
        Run number (e.g., 1, 2, 3)
    data_type : str
        'roi_outputs' for brain data or 'frames' for visual feedback
    study : str
        'charms', 'mindbpd', or 'auto' to auto-detect
    
    Returns:
    --------
    pd.DataFrame or None if file not found
    """
    participant_id = str(participant_id)
    
    # Auto-detect study based on participant ID
    if study == 'auto':
        if participant_id.startswith('2') and len(participant_id) == 4:
            study = 'mindbpd'
        else:
            study = 'charms'
    
    # Set prefix based on study (NO underscore between prefix and ID)
    if study == 'charms':
        prefix = 'sub-charms'
    else:
        prefix = 'sub-mindbpd'
    
    # Construct full subject ID string
    full_id = f'{prefix}{participant_id}'
    
    # Try multiple possible locations and patterns
    possible_paths = [
        f'data/{full_id}/{full_id}_DMN_feedback_{run_number}_{data_type}.csv',
        f'data/{full_id}/{full_id}_DMN_nofeedback_{run_number}_{data_type}.csv',
        f'feedback/{full_id}/{full_id}_DMN_feedback_{run_number}_{data_type}.csv',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                print(f"Loading: {path}")
                df = pd.read_csv(path)
                # Check if dataframe is empty
                if df.empty or len(df.columns) == 0:
                    print(f"Warning: File exists but is empty: {path}")
                    continue
                return df
            except pd.errors.EmptyDataError:
                print(f"Warning: File is empty or malformed: {path}")
                continue
            except Exception as e:
                print(f"Warning: Error reading {path}: {e}")
                continue
    
    print(f"Warning: Could not find valid {data_type} file for participant {participant_id}, run {run_number}")
    print(f"  Tried paths: {possible_paths}")
    return None


def create_comparison_figure(real_id, sham_id, run_number, output_file='real_vs_sham_comparison.png'):
    """
    Create comprehensive comparison figure between REAL and SHAM participants
    
    Parameters:
    -----------
    real_id : str or int
        REAL participant ID (e.g., 2098)
    sham_id : str or int  
        SHAM participant ID (e.g., 2099)
    run_number : int
        Run number to compare
    output_file : str
        Output filename for the figure
    """
    
    # Load data
    print(f"\n{'='*60}")
    print(f"Loading data for REAL participant {real_id} vs SHAM participant {sham_id}")
    print(f"Run number: {run_number}")
    print(f"{'='*60}\n")
    
    # Load brain activity data (roi_outputs)
    real_brain = load_participant_data(real_id, run_number, 'roi_outputs')
    sham_brain = load_participant_data(sham_id, run_number, 'roi_outputs')
    
    # Load visual feedback data (frames)
    real_visual = load_participant_data(real_id, run_number, 'frames')
    sham_visual = load_participant_data(sham_id, run_number, 'frames')
    
    if real_brain is None or sham_brain is None:
        print("ERROR: Could not load required brain activity data!")
        return
    
    # Filter to feedback period only
    real_brain_fb = real_brain[real_brain['stage'] == 'feedback'].copy()
    sham_brain_fb = sham_brain[sham_brain['stage'] == 'feedback'].copy()
    
    # Create figure with 6 subplots
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Color scheme
    color_real = '#2E7D32'  # Green
    color_sham = '#D32F2F'  # Red
    color_cen = '#FFA726'   # Orange
    color_dmn = '#42A5F5'   # Blue
    
    # ========================================================================
    # ROW 1: What they SAW (Ball Position)
    # ========================================================================
    
    # REAL participant - what they saw
    ax1 = fig.add_subplot(gs[0, 0])
    if real_visual is not None and 'ball_y' in real_visual.columns:
        ax1.plot(real_visual['time'], real_visual['ball_y'], 
                linewidth=2, color=color_real, alpha=0.8)
        ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.3, label='Center')
        ax1.set_ylabel('Ball Y Position', fontsize=12, fontweight='bold')
        ax1.set_title(f'REAL {real_id}: What They SAW (Actual Ball Movement)', 
                     fontsize=13, fontweight='bold', color=color_real)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(real_visual['time'].min(), real_visual['time'].max())
    else:
        # Use ball_y_position from roi_outputs as fallback
        ax1.plot(real_brain_fb['time'], real_brain_fb['ball_y_position'], 
                linewidth=2, color=color_real, alpha=0.8)
        ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.3, label='Center')
        ax1.set_ylabel('Ball Y Position', fontsize=12, fontweight='bold')
        ax1.set_title(f'REAL {real_id}: What They SAW (Actual Ball Movement)', 
                     fontsize=13, fontweight='bold', color=color_real)
        ax1.grid(True, alpha=0.3)
    
    # Add target zones
    if 'top_circle_y_position' in real_brain_fb.columns:
        top_target = real_brain_fb['top_circle_y_position'].iloc[0]
        bottom_target = real_brain_fb['bottom_circle_y_position'].iloc[0]
        ax1.axhline(y=top_target, color=color_cen, linestyle=':', alpha=0.5, linewidth=2, label='CEN Target')
        ax1.axhline(y=bottom_target, color=color_dmn, linestyle=':', alpha=0.5, linewidth=2, label='DMN Target')
        ax1.legend(loc='upper right', fontsize=9)
    
    # SHAM participant - what they saw (YOKED from REAL)
    ax2 = fig.add_subplot(gs[0, 1])
    
    # SHAM sees the SAME visual feedback as REAL (yoked)
    # So we display REAL's visual data for SHAM's display
    if real_visual is not None and 'ball_y' in real_visual.columns:
        ax2.plot(real_visual['time'], real_visual['ball_y'], 
                linewidth=2, color=color_sham, alpha=0.8)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.3, label='Center')
        ax2.set_ylabel('Ball Y Position', fontsize=12, fontweight='bold')
        ax2.set_title(f'SHAM {sham_id}: What They SAW (Yoked from REAL {real_id})', 
                     fontsize=13, fontweight='bold', color=color_sham)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(real_visual['time'].min(), real_visual['time'].max())
        
        # Add annotation explaining yoked feedback
        ax2.text(0.5, 0.95, 'IDENTICAL to REAL participant\'s display', 
                ha='center', va='top', transform=ax2.transAxes, 
                fontsize=10, style='italic', 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    else:
        # Fallback: use ball_y_position from REAL roi_outputs
        ax2.plot(real_brain_fb['time'], real_brain_fb['ball_y_position'], 
                linewidth=2, color=color_sham, alpha=0.8)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.3, label='Center')
        ax2.set_ylabel('Ball Y Position', fontsize=12, fontweight='bold')
        ax2.set_title(f'SHAM {sham_id}: What They SAW (Yoked from REAL {real_id})', 
                     fontsize=13, fontweight='bold', color=color_sham)
        ax2.grid(True, alpha=0.3)
        
        # Add annotation
        ax2.text(0.5, 0.95, 'IDENTICAL to REAL participant\'s display', 
                ha='center', va='top', transform=ax2.transAxes, 
                fontsize=10, style='italic', 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # Add target zones for SHAM (same as REAL since they see same display)
    if 'top_circle_y_position' in real_brain_fb.columns:
        top_target = real_brain_fb['top_circle_y_position'].iloc[0]
        bottom_target = real_brain_fb['bottom_circle_y_position'].iloc[0]
        ax2.axhline(y=top_target, color=color_cen, linestyle=':', alpha=0.5, linewidth=2, label='CEN Target')
        ax2.axhline(y=bottom_target, color=color_dmn, linestyle=':', alpha=0.5, linewidth=2, label='DMN Target')
        ax2.legend(loc='upper right', fontsize=9)
    
    # ========================================================================
    # ROW 2: What was RECORDED (Brain Activity - CEN vs DMN)
    # ========================================================================
    
    # REAL participant - brain activity
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(real_brain_fb['time'], real_brain_fb['cen'], 
            linewidth=2, color=color_cen, alpha=0.8, label='CEN')
    ax3.plot(real_brain_fb['time'], real_brain_fb['dmn'], 
            linewidth=2, color=color_dmn, alpha=0.8, label='DMN')
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    ax3.set_ylabel('Activation (z-score)', fontsize=12, fontweight='bold')
    ax3.set_title(f'REAL {real_id}: Brain Activity RECORDED (Controls Ball)', 
                 fontsize=13, fontweight='bold', color=color_real)
    ax3.legend(loc='upper right', fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(real_brain_fb['time'].min(), real_brain_fb['time'].max())
    
    # SHAM participant - brain activity
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(sham_brain_fb['time'], sham_brain_fb['cen'], 
            linewidth=2, color=color_cen, alpha=0.8, label='CEN')
    ax4.plot(sham_brain_fb['time'], sham_brain_fb['dmn'], 
            linewidth=2, color=color_dmn, alpha=0.8, label='DMN')
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    ax4.set_ylabel('Activation (z-score)', fontsize=12, fontweight='bold')
    ax4.set_title(f'SHAM {sham_id}: Brain Activity RECORDED (Does NOT Control Ball)', 
                 fontsize=13, fontweight='bold', color=color_sham)
    ax4.legend(loc='upper right', fontsize=10)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(sham_brain_fb['time'].min(), sham_brain_fb['time'].max())
    
    # ========================================================================
    # ROW 3: Cumulative Hits & PDA Comparison
    # ========================================================================
    
    # Cumulative hits comparison
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.plot(real_brain_fb['time'], real_brain_fb['cen_cumulative_hits'], 
            linewidth=2.5, color=color_cen, alpha=0.8, marker='o', markersize=4,
            label=f'REAL {real_id} CEN')
    ax5.plot(real_brain_fb['time'], real_brain_fb['dmn_cumulative_hits'], 
            linewidth=2.5, color=color_dmn, alpha=0.8, marker='s', markersize=4,
            label=f'REAL {real_id} DMN')
    ax5.plot(sham_brain_fb['time'], sham_brain_fb['cen_cumulative_hits'], 
            linewidth=2.5, color=color_cen, alpha=0.5, linestyle='--', marker='^', markersize=4,
            label=f'SHAM {sham_id} CEN (Virtual)')
    ax5.plot(sham_brain_fb['time'], sham_brain_fb['dmn_cumulative_hits'], 
            linewidth=2.5, color=color_dmn, alpha=0.5, linestyle='--', marker='v', markersize=4,
            label=f'SHAM {sham_id} DMN (Virtual)')
    ax5.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Cumulative Hits', fontsize=12, fontweight='bold')
    ax5.set_title('Cumulative Hits Over Time (REAL vs SHAM Virtual)', 
                 fontsize=13, fontweight='bold')
    ax5.legend(loc='upper left', fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # PDA (CEN - DMN) comparison
    ax6 = fig.add_subplot(gs[2, 1])
    real_pda = real_brain_fb['cen'] - real_brain_fb['dmn']
    sham_pda = sham_brain_fb['cen'] - sham_brain_fb['dmn']
    
    ax6.plot(real_brain_fb['time'], real_pda, 
            linewidth=2, color=color_real, alpha=0.8, label=f'REAL {real_id}')
    ax6.plot(sham_brain_fb['time'], sham_pda, 
            linewidth=2, color=color_sham, alpha=0.8, label=f'SHAM {sham_id}')
    ax6.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1.5)
    ax6.fill_between(real_brain_fb['time'], 0, real_pda, 
                     where=(real_pda > 0), alpha=0.2, color=color_cen, label='CEN Dominant')
    ax6.fill_between(real_brain_fb['time'], 0, real_pda, 
                     where=(real_pda < 0), alpha=0.2, color=color_dmn, label='DMN Dominant')
    ax6.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
    ax6.set_ylabel('PDA (CEN - DMN)', fontsize=12, fontweight='bold')
    ax6.set_title('Preferential Differential Activation (PDA)', 
                 fontsize=13, fontweight='bold')
    ax6.legend(loc='upper right', fontsize=9)
    ax6.grid(True, alpha=0.3)
    
    # Add overall title
    fig.suptitle(f'REAL Participant {real_id} vs SHAM Participant {sham_id} - Run {run_number}\n' + 
                 'SHAM sees yoked visual feedback but their brain activity is still recorded',
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Add summary statistics box
    real_cen_hits = real_brain_fb['cen_cumulative_hits'].max()
    real_dmn_hits = real_brain_fb['dmn_cumulative_hits'].max()
    sham_cen_hits = sham_brain_fb['cen_cumulative_hits'].max()
    sham_dmn_hits = sham_brain_fb['dmn_cumulative_hits'].max()
    
    stats_text = f"""
    SUMMARY STATISTICS
    ──────────────────────────────
    REAL {real_id}:
      • CEN Hits: {real_cen_hits}
      • DMN Hits: {real_dmn_hits}
      • Total: {real_cen_hits + real_dmn_hits}
      • Mean CEN: {real_brain_fb['cen'].mean():.3f}
      • Mean DMN: {real_brain_fb['dmn'].mean():.3f}
    
    SHAM {sham_id} (Virtual):
      • CEN Hits: {sham_cen_hits}
      • DMN Hits: {sham_dmn_hits}
      • Total: {sham_cen_hits + sham_dmn_hits}
      • Mean CEN: {sham_brain_fb['cen'].mean():.3f}
      • Mean DMN: {sham_brain_fb['dmn'].mean():.3f}
    """
    
    fig.text(0.02, 0.02, stats_text, fontsize=9, family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
             verticalalignment='bottom')
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n{'='*60}")
    print(f"Figure saved as: {output_file}")
    print(f"{'='*60}\n")
    
    # Print summary statistics to console
    print("\nSUMMARY STATISTICS:")
    print(f"REAL {real_id} - Total Hits: {real_cen_hits + real_dmn_hits} (CEN: {real_cen_hits}, DMN: {real_dmn_hits})")
    print(f"SHAM {sham_id} - Total Virtual Hits: {sham_cen_hits + sham_dmn_hits} (CEN: {sham_cen_hits}, DMN: {sham_dmn_hits})")
    print(f"\nREAL {real_id} - Mean Brain Activity: CEN={real_brain_fb['cen'].mean():.3f}, DMN={real_brain_fb['dmn'].mean():.3f}")
    print(f"SHAM {sham_id} - Mean Brain Activity: CEN={sham_brain_fb['cen'].mean():.3f}, DMN={sham_brain_fb['dmn'].mean():.3f}")
    
    plt.show()
    
    return fig


def main():
    """Main function to run from command line"""
    parser = argparse.ArgumentParser(
        description='Compare REAL vs SHAM participant neurofeedback data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # MIND-BPD (2XXX IDs)
  python compare_real_sham_visualization.py --real 2098 --sham 2099 --run 1
  
  # CHARMS (XXX IDs without leading 2)
  python compare_real_sham_visualization.py --real 098 --sham 099 --run 1
  
  # Custom output
  python compare_real_sham_visualization.py --real 098 --sham 099 --run 1 --output charms_comparison.png
        """)
    
    parser.add_argument('--real', required=True,
                       help='REAL participant ID (e.g., 2098 for MIND-BPD, 098 for CHARMS)')
    parser.add_argument('--sham', required=True,
                       help='SHAM participant ID (e.g., 2099 for MIND-BPD, 099 for CHARMS)')
    parser.add_argument('--run', type=int, default=1,
                       help='Run number to compare (default: 1)')
    parser.add_argument('--output', type=str, default='real_vs_sham_comparison.png',
                       help='Output filename (default: real_vs_sham_comparison.png)')
    parser.add_argument('--study', type=str, default='auto', choices=['auto', 'charms', 'mindbpd'],
                       help='Study name (default: auto-detect from ID)')
    
    args = parser.parse_args()
    
    # Create visualization
    create_comparison_figure(args.real, args.sham, args.run, args.output)


if __name__ == '__main__':
    main()
