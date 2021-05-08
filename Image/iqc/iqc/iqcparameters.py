#!/usr/bin/env python3

'''
Argument parser for iqc script
'''

import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', required=True, action='store', dest='input_path', type=str, help='full path to input folder containing TIFF images. Directory structure does not matter.')
parser.add_argument('--output', '-o', action='store', dest='output_path', type=str, help='full path to output csv file. For debugging purposes currently.')
parser.add_argument('--inventory', required=False, action='store', dest='inventory_path', type=str, help='Full path to folder containing inventories or full path to a single CSV inventory file.')
parser.add_argument('--verify_checksums', '-c', required=False, nargs=1, action='store', dest='verify_checksums', help='Include to verify sidecar checksums. This argument must be followed by either "md5" or "sha1" to specify which type of checksum to verify')
parser.add_argument('--verify_metadata', '-m', required='--strict' in sys.argv, action='store_true', dest='verify_metadata', help='Include to check if the embedded IPTC metadata appears in the inventory. By default truncated IPTC metadata will still pass.')
parser.add_argument('--exiftool', action='store', dest='exiftool_path', default='exiftool', type=str, help='For setting a custom exiftool path')
parser.add_argument('--strict', '-s', required=False, action='store_true', help='Use with --verify_metadata to enforce exact metadata matching. Will cause truncated IPTC fields to fail')
parser.add_argument('--verify_techdata', '-t', required=False, action='store_true', dest='techdata', help='Verify technical metadata. This will check the bit depth and color profile of TIFF images.')
parser.add_argument('--all', '-a', required=False, action='store_true', dest='all', help='')
#parser.add_argument('--filter_list', action='store', dest='filter_list', help='Provide a text file with a list of files. Not implemented yet')

args = parser.parse_args()

if args.all is True:
    args.verify_metadata = True
    args.verify_checksums = ['md5']
    args.techdata = True
