#!/usr/bin/env python3

"""
Argument parser for aqc.
"""

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    action="store",
    dest="inpath",
    type=str,
    help="full path to input file or directory",
)
parser.add_argument(
    "--lstats",
    "-l",
    action="store_true",
    dest="lstats",
    default=False,
    help="use to get loudness statistics",
)
parser.add_argument(
    "--plot",
    "-p",
    action="store_true",
    dest="plot",
    default=False,
    help="use to show plots of data",
)
parser.add_argument(
    "--find_clipping",
    "-c",
    action="store_true",
    dest="find_clipping",
    default=False,
    help="use to check for clipping",
)
parser.add_argument(
    "--find_silence",
    "-s",
    action="store_true",
    dest="find_silence",
    default=False,
    help="use to check for silence",
)
parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    dest="verbose",
    default=False,
    help="use to print stats to terminal ni addition to json file",
)
args = parser.parse_args()