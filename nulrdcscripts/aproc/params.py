#!/usr/bin/env python3

"""
Standardized argument parser for audio processing script
Processes all steps by default unless flags disable them
"""

import argparse
import sys

parser = argparse.ArgumentParser(
    description="Audio preservation file processing and QC workflow (processes everything by default)"
)

# Core parameters
parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    type=str,
    help="Path to directory containing .wav files (auto-detects batch vs single object)",
)
parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    type=str,
    help="Path to output CSV file for QC results (default: <input_dir>/<basename>-qc_log.csv)",
)
parser.add_argument(
    "--inventory",
    "-l",
    required=False,
    nargs="*",
    action="store",
    dest="source_inventory",
    help="Path to CSV inventory file (default: auto-detect .csv files in input directory)",
)

# Processing control
# By default: transcode=YES, metadata=YES, json=YES, spectrogram=YES
parser.add_argument(
    "--skip-transcode",
    required=False,
    action="store_true",
    dest="skip_transcode",
    help="Skip creating access copies (enabled by default)",
)
parser.add_argument(
    "--skip-metadata",
    required=False,
    action="store_true",
    dest="skip_metadata",
    help="Skip embedding BWF metadata (enabled by default)",
)
parser.add_argument(
    "--skip-json",
    required=False,
    action="store_true",
    dest="skip_json",
    help="Skip creating JSON metadata files (enabled by default)",
)
parser.add_argument(
    "--skip-spectrogram",
    required=False,
    action="store_true",
    dest="skip_spectrogram",
    help="Skip generating spectrograms (enabled by default)",
)

# Tool paths
parser.add_argument(
    "--sox",
    action="store",
    dest="sox_path",
    default="sox",
    type=str,
    help="Path to sox executable (default: sox)",
)
parser.add_argument(
    "--bwfmetaedit",
    action="store",
    dest="metaedit_path",
    default="bwfmetaedit",
    type=str,
    help="Path to BWF MetaEdit executable (default: bwfmetaedit)",
)
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
    "--mediaconch",
    action="store",
    dest="mediaconch_path",
    default="mediaconch",
    type=str,
    help="Path to mediaconch executable (default: mediaconch)",
)

# Policy files
parser.add_argument(
    "--p-policy",
    required=False,
    action="store",
    dest="input_policy",
    help="Custom MediaConch policy for preservation files",
)
parser.add_argument(
    "--a-policy",
    required=False,
    action="store",
    dest="output_policy",
    help="Custom MediaConch policy for access files",
)

# Advanced options
parser.add_argument(
    "--skip-coding-history",
    default=False,
    required=False,
    action="store_true",
    dest="skip_coding_history",
    help="Skip coding history creation in BWF metadata",
)
parser.add_argument(
    "--verbose",
    "-v",
    required=False,
    action="store_true",
    dest="verbose",
    help="Display detailed processing information",
)

args = parser.parse_args()

# Set processing flags (inverted from skip flags)
# By default, everything is TRUE unless --skip flag is used
args.transcode = not args.skip_transcode
args.write_bwf_metadata = not args.skip_metadata
args.write_json = not args.skip_json
args.spectrogram = not args.skip_spectrogram

# Legacy compatibility
args.all = args.transcode and args.write_bwf_metadata and args.write_json and args.spectrogram

# Print usage info when no args
if len(sys.argv) == 1:
    print("\n" + "="*80)
    print("AUDIO PROCESSING - AUTO-DETECT MODE")
    print("="*80)
    print("\nAccepted input structures:")
    print("  1. Single object with WAV files:")
    print("     input_dir/*.wav")
    print()
    print("  2. Batch: Multiple object folders:")
    print("     input_dir/object1/*.wav")
    print("     input_dir/object2/*.wav")
    print()
    print("  3. Already organized (preserves structure):")
    print("     input_dir/object1/p/*_p.wav")
    print()
    print("The script will:")
    print("  ✓ Auto-detect batch vs single object mode")
    print("  ✓ Create p/, a/, meta/ folders automatically")
    print("  ✓ Process ALL steps by default (transcode, metadata, json, spectrogram)")
    print("  ✓ Look for inventory.csv in the input directory")
    print()
    print("Quick start:")
    print("  Process everything:           python aproc.py -i /path/to/audio")
    print("  Skip access copies:           python aproc.py -i /path/to/audio --skip-transcode")
    print("  Skip spectrograms:            python aproc.py -i /path/to/audio --skip-spectrogram")
    print("  Custom inventory:             python aproc.py -i /path/to/audio -l /path/to/inventory.csv")
    print("\n" + "="*80 + "\n")
    parser.print_help()