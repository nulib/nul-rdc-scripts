#!/usr/bin/env python3

"""
Argument parser for iqc script
"""

import argparse
import sys
from pkg_resources import get_distribution

parser = argparse.ArgumentParser()

if parser.prog == "run.py":
    import os

    parser.prog = "iqc"
    version_file = open(os.path.join(os.path.dirname(__file__), "meta", "VERSION"))
    __version__ = version_file.read().strip()
else:
    __version__ = get_distribution("iqc").version

parser.add_argument(
    "--input",
    "-i",
    required=True,
    action="store",
    dest="input_path",
    type=str,
    help="full path to input folder containing TIFF images. Directory structure does not matter.",
)
parser.add_argument(
    "--output",
    "-o",
    action="store",
    dest="output_path",
    type=str,
    help="full path to output csv file. For debugging purposes currently.",
)
parser.add_argument(
    "--inventory",
    required=False,
    action="store",
    dest="inventory_path",
    type=str,
    help="Full path to folder containing inventories or full path to a single CSV inventory file.",
)
parser.add_argument(
    "--verify_checksums",
    "-c",
    required=False,
    nargs=1,
    action="store",
    dest="verify_checksums",
    help='Include to verify sidecar checksums. This argument must be followed by either "md5" or "sha1" to specify which type of checksum to verify',
)
parser.add_argument(
    "--verify_metadata",
    "-m",
    required="--strict" in sys.argv,
    action="store_true",
    dest="verify_metadata",
    help="Include to check if the embedded IPTC metadata appears in the inventory. By default truncated IPTC metadata will still pass.",
)
parser.add_argument(
    "--exiftool",
    action="store",
    dest="exiftool_path",
    default="exiftool",
    type=str,
    help="For setting a custom exiftool path",
)
parser.add_argument(
    "--strict",
    "-s",
    required=False,
    action="store_true",
    help="Use with --verify_metadata to enforce exact metadata matching. Will cause truncated IPTC fields to fail",
)
parser.add_argument(
    "--verify_techdata",
    "-t",
    required=False,
    action="store_true",
    dest="techdata",
    help="Verify technical metadata. This will check the bit depth and color profile of TIFF images.",
)
parser.add_argument(
    "--all",
    "-a",
    required=False,
    action="store_true",
    dest="all",
    help="This is equivalent to including the commands --verify_metadata --verify_techdata --verify checksums md5 -o /path/to/input/input-iqc_report.json",
)
parser.add_argument(
    "--version", "-v", action="version", version="%(prog)s " + __version__ + ""
)

args = parser.parse_args()

args.version = __version__

if args.all is True:
    args.verify_metadata = True
    args.verify_checksums = ["md5"]
    args.techdata = True
