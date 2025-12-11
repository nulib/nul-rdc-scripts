#!/usr/bin/env python3

"""
Standardized argument parser for video processing script
Auto-detects batch mode and processes everything by default
"""

import argparse
import sys

parser = argparse.ArgumentParser(
    description="Video preservation file processing and QC workflow (auto-detects batch mode)"
)

# Core parameters
parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    type=str,
    help="Path to directory containing .mkv files (auto-detects batch vs single object)",
)
parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    type=str,
    help="Path to output directory (default: same as input)",
)
parser.add_argument(
    "--inventory",
    "-l",
    required=False,
    action="store",
    dest="source_inventory",
    help="Path to CSV inventory file (default: auto-detect in input directory)",
)

# Processing control
# By default: access copies=YES, spectrograms=YES, json=YES, qcli=NO
parser.add_argument(
    "--skip-ac",
    required=False,
    action="store_true",
    dest="skip_ac",
    help="Skip access copy transcoding (enabled by default)",
)
parser.add_argument(
    "--skip-spectrogram",
    required=False,
    action="store_true",
    dest="skip_spectrogram",
    help="Skip spectrogram generation (enabled by default)",
)
parser.add_argument(
    "--run-qcli",
    required=False,
    action="store_true",
    dest="run_qcli",
    help="Run QCTools report generation (disabled by default)",
)
parser.add_argument(
    "--mixdown",
    action="store",
    dest="mixdown",
    default="copy",
    type=str,
    help="Audio stream mapping: copy (default), 4to3, 4to2, 2to1",
)
parser.add_argument(
    "--keep-filename",
    required=False,
    action="store_true",
    dest="keep_filename",
    help="Preserve original filename (don't add _p suffix)",
)
parser.add_argument(
    "--embed-framemd5",
    required=False,
    action="store_true",
    dest="embed_framemd5",
    help="Remux preservation file to embed framemd5",
)

# Tool paths
parser.add_argument(
    "--ffmpeg",
    action="store",
    dest="ffmpeg_path",
    default="ffmpeg",
    type=str,
    help="Path to ffmpeg executable (default: ffmpeg)",
)
parser.add_argument(
    "--ffprobe",
    action="store",
    dest="ffprobe_path",
    default="ffprobe",
    type=str,
    help="Path to ffprobe executable (default: ffprobe)",
)
parser.add_argument(
    "--qcli",
    action="store",
    dest="qcli_path",
    default="qcli",
    type=str,
    help="Path to qcli executable (default: qcli)",
)
parser.add_argument(
    "--mediaconch",
    action="store",
    dest="mediaconch_path",
    default="mediaconch",
    type=str,
    help="Path to mediaconch executable (default: mediaconch)",
)

# Policy files
parser.add_argument(
    "--input-policy",
    required=False,
    action="store",
    dest="input_policy",
    help="Custom MediaConch policy for input files",
)
parser.add_argument(
    "--output-policy",
    required=False,
    action="store",
    dest="output_policy",
    help="Custom MediaConch policy for output files",
)

# Advanced options
parser.add_argument(
    "--slices",
    action="store",
    dest="ffv1_slice_count",
    default="16",
    choices=[4, 6, 9, 12, 16, 24, 30],
    type=int,
    help="FFV1 slice count for encoding (default: 16)",
)
parser.add_argument(
    "--verbose",
    "-v",
    required=False,
    action="store_true",
    dest="verbose",
    help="Display detailed ffmpeg output during transcoding",
)

# Hidden flag for backwards compatibility
parser.add_argument(
    "--batch",
    "-b",
    required=False,
    action="store_true",
    dest="batch",
    help=argparse.SUPPRESS,  # Hidden - auto-detected now
)

args = parser.parse_args()

# Set qcli flag (inverted - off by default, turned on with --run-qcli)
# Default run_qcli to False if not set
if not hasattr(args, 'run_qcli'):
    args.run_qcli = False
args.skip_qcli = not args.run_qcli

# Print usage info when no args
if len(sys.argv) == 1:
    print("\n" + "="*80)
    print("VIDEO PROCESSING - AUTO-DETECT MODE")
    print("="*80)
    print("\nAccepted input structures:")
    print("  1. Single object with MKV files:")
    print("     input_dir/*.mkv")
    print()
    print("  2. Batch: Multiple object folders:")
    print("     input_dir/object1/*.mkv")
    print("     input_dir/object2/*.mkv")
    print()
    print("  3. Already organized (preserves structure):")
    print("     input_dir/object1/p/*_p.mkv")
    print()
    print("The script will:")
    print("  ✓ Auto-detect batch vs single object mode")
    print("  ✓ Create p/, a/, meta/ folders automatically")
    print("  ✓ Rename files to add _p suffix if needed")
    print("  ✓ Process access copies, metadata, and spectrograms by default")
    print("  ✓ QCTools reports are OFF by default (use --run-qcli to enable)")
    print("  ✓ Look for inventory.csv in the input directory")
    print()
    print("Quick start:")
    print("  Process everything:           python vproc.py -i /path/to/video")
    print("  Skip access copies:           python vproc.py -i /path/to/video --skip-ac")
    print("  Enable QCTools reports:       python vproc.py -i /path/to/video --run-qcli")
    print("  Custom audio mixdown:         python vproc.py -i /path/to/video --mixdown 4to2")
    print("  Custom inventory:             python vproc.py -i /path/to/video -l /path/to/inventory.csv")
    print("\n" + "="*80 + "\n")
    parser.print_help()