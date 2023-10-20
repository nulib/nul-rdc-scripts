"""
Argument parser for in-house file structure flattening script
"""

import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action = "store",
    dest = "input_path",
    type = str,
    help = "full path to input folder",
)
parser.add_argument(
    "--mode",
    "-m",
    action = "store",
    dest = "mode",
    type = str,
    help = "sets mode to single or batch"
)

args = parser.parse_args()