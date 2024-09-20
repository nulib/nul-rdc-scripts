#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="input_path",
    type=str,
    help="full path to input folder",
),
parser.add_argument(
    "--ffprobe_path",
    action="store",
    dest="ffprobe_path",
    type=str,
    default = "ffprobe"
)

args = parser.parse_args()
