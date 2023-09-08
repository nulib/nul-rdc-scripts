#!/usr/bin/env python3

"""
Argument parser for image ingest sheet script
"""

import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    "-i",
    required=True,
    action="store",
    dest="input_path",
    type=str,
    help="full path to input folder",
)
parser.add_argument(
    "--output",
    "-o",
    required=True,
    action="store",
    dest="output_path",
    type=str,
    help="full path to output csv file",
)
# parser.add_argument('--inventory', required=True, action='store', dest='inventory_path', type=str, help='path to folder containing inventories')
# parser.add_argument('--filter_list', action='store', dest='filter_list', help='Provide a text file with a list of files. Not implemented yet')


args = parser.parse_args()
