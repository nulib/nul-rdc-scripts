#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(
    description="Allows input of files for video analysis statistics for automated quality control"
)

parser.add_argument(
    "--input",
    "-i",
    metavar="inputfile",
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
    type=str,
    required=True,
    help="Enter the full path to where you want your output files",
)

bitdepth = parser.add_mutually_exclusive_group(required=True)
bitdepth.add_argument(
    "--10bit",
    "-10",
    action="store_true",
    dest="_10bit",
    help="for 10 bit videos",
)
bitdepth.add_argument(
    "--8bit",
    "-8",
    action="store_true",
    dest="_8bit",
    help="for 8 bit videos",
)

color = parser.add_mutually_exclusive_group(required=True)
color.add_argument(
    "--color",
    "-c",
    action="store_true",
    dest="color",
    help="for color videos",
)
color.add_argument(
    "--blackandwhite",
    "-bw",
    action="store_true",
    dest="blackandwhite",
    help="for black and white videos",
)
args = parser.parse_args()