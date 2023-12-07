#!/usr/bin/env python3

"""
Argument parser for in-house AJA v210/mov to ffv1/mkv script  
"""

import argparse

parser = argparse.ArgumentParser()

script = parser.add_mutually_exclusive_group(required=True)
script.add_argument(
    "--ingest",
    "-i",
    action="store_true",
    dest="ingest",
    help="choose to test ingest script",
)
script.add_argument(
    "--vproc",
    "-v",
    action="store_true",
    dest="vproc",
    help="choose to test vproc script",
)
script.add_argument(
    "--aproc",
    "-a",
    action="store_true",
    dest="aproc",
    help="choose to test aproc script",
)

args = parser.parse_args()