#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(
    description="Allows input of files and the output of files"
)

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    type=str,
    help="full path to input folder",
)

parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    type=str,
    help="full path to output folder",
)

parser.add_argument(
    "--8bit",
    "--8",
    "--10" "--10bit",
    action="store",
    default="--10bit",
    type=str,
    help="Use to specify what bit depth your video is",
)

args = parser.parse_args()
