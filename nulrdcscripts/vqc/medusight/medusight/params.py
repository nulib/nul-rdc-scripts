#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(
    description="Allows input of files for video analysis statistics for automated quality control"
)

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    required=True,
    type=str,
    help="Enter the full path to input file folder",
)

parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    default="input",
    type=str,
    help="Enter the full path to where you want your output files",
)

# This may actually be able to come directly from video
parser.add_argument(
    "--videobitdepth",
    "-vbd",
    choices=["10", "10bit", "10Bit", "8", "8bit", "8Bit"],
    action="store",
    default="10bit",
    dest="videobitdepth",
    required=False,
    type=str,
    help="Use to specify what bit depth your video is",
)

parser.add_argument('--crop-mode', 
                   choices=['auto', 'combined', 'headswitching', 'off', 'none', 'manual'],
                   default='off',  # Default to 'off' to preserve existing behavior
                   help='''Crop mode for video input:
                   auto = detect black borders only
                   combined = black borders + headswitching noise
                   headswitching = headswitching noise only
                   off/none = no cropping (default)
                   manual = use --manual-crop value''')

parser.add_argument('--manual-crop',
                   type=str,
                   default=None,
                   help='Manual crop value (e.g., "1920:1080:0:0") - used with --crop-mode manual')

parser.add_argument('--sample-interval',
                   type=int,
                   default=900,
                   help='Frame sampling interval for crop auto-detection (default: 900)')
args = parser.parse_args()
