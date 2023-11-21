#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(
    description="Allows input of files for video analysis statistics for automated quality control"
)

parser.add_argument(
    "--input",
    "-i",
    metavar = 'inputfile',
    action="store",
    dest="input_path",
    required = True,
    type=str,
    help="Enter the full path to input file folder"
)

parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    type=str,
    required = True,
    help="Enter the full path to where you want your output files",
)

#This may actually be able to come directly from video
parser.add_argument('videobitdepth', choices = ['-10', '--10bit', '-8, --8bit'],
    action="store",
    default="--10bit",
    dest = "videobitdepth",
    required = True,
    type=str,
    help="Use to specify what bit depth your video is",
)

#Need to add one for B/W or Color video option

parser.add_argument('videotype', choices = ['-bw', '--blackandwhite', '-c', '-color'],
    action = "store",
    required = True,
    dest = "videotype",
    help = "Tells script what video type to run: black and white or color"
    )
args = parser.parse_args()
