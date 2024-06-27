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
)

args = parser.parse_args()
