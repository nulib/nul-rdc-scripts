#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="infile",
    type=str,
    help="full path to input file",
)

args = parser.parse_args()