#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', action='store', dest='input_path', type=str, help='full path to input folder')
#parser.add_argument('--output', '-o', action='store', dest='output_path', type=str, help='full path to output csv file')
parser.add_argument('--exiftool', action='store', dest='exiftool_path', default='exiftool', type=str, help='For setting a custom exiftool path')
parser.add_argument('--load_inventory', '-l', required=False, nargs='*', action='store', dest='source_inventory', help='Use to specify an object inventory. If not specified the script will look in the base folder of the input for object inventories. If no inventories are found the script will leave some fields blank.')
parser.add_argument('--verify_checksums', '-c', required=False, nargs=1, action='store', dest='verify_checksums', help='Include to verify sidecar checksums. This argument must be followed by either "md5" or "sha1" to specify which type of checksum to verify')

args = parser.parse_args()
