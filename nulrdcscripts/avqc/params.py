#!/usr/bin/env python3

"""
Argument parser for avqc script
"""

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
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--audio",
    "-a",
    action="store_true",
    dest="audio",
    help="for audio projects",
)
group.add_argument(
    "--video",
    "-v",
    action="store_true",
    dest="video",
    help="for video projects",
)
group.add_argument(
    "--film",
    "-f",
    action="store_true",
    dest="film",
    help="for film projects",
)
parser.add_argument(
    "--skip_checksums",
    "-s",
    action="store_true",
    dest="skip_checksums",
    help="use to skip validating checksums",
)
parser.add_argument(
    "--play_access",
    action="store_true",
    dest="play_access",
    help="use to play a files along with p files",
)

args = parser.parse_args()
