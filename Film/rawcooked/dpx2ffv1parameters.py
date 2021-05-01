#!/usr/bin/env python3

import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.30')


parser.add_argument('--framerate', required=False, action='store', dest='framerate', help='Sets framerate for dpx2ffv1 conversion script. Defaults to 24 if not specified')


parser.add_argument('--input', '-i', action='store', dest='input_path', type=str, help='full path to input folder')
parser.add_argument('--output', '-o', action='store', dest='output_path', type=str, help='full path to output folder')
parser.add_argument('--subfolder_identifier', action='store', dest='subfolder_identifier', type=str, help='Specifies the folder identifier if files are located in a subfolder. For example, a pm folder within an object folder.')
parser.add_argument('--limit', action='store', dest='textlimit', type=str, help='Defines a string that limits which folders batch commands run on.  If not used, commands will run on all immediate subdirectories of the input')
parser.add_argument('--filter_list', action='store', dest='filter_list', type=str, help='Pull list of files to process from a text file')


parser.add_argument('--dpxcheck', action='store', dest='dpxcheck_path', type=str, help='Full path to a location where DPX files will be decoded from FFV1 files.  If left blank, this will default to the folder where the FFV1 file being decoded is located.')
#TO DO: implement ffv1 decode
parser.add_argument('--decodeffv1', required=False, action='store_true', help='For each folder in input, generate a decode the FFV1 file back to a dpx sequence, check md5 checksums and compare file size of FFV1 file and DPX sequence')
#TO DO: implement mkv verification
parser.add_argument('--verifymkv', required=False, action='store_true', help='')


parser.add_argument('--check_runtime', action='store_true', required=False, help='checks ffv1 runtime against access copy runtime after transcode')
#parser.add_argument('--notparanoid', action='store_true', required=False, help='Include in dpx2ffv1 conversion to skip decoding ffv1 sequence back to dpx and generating verification logs')


parser.add_argument('--rawcooked', action='store', dest='rawcooked_path', default='rawcooked', type=str, help='The full path to RAWcooked. Use if you need to specify a custom path to rawcooked.')
parser.add_argument('--ffmpeg', action='store', dest='ffmpeg_path', default='ffmpeg', type=str, help='The full path to ffmpeg. Use if you need to specify a custom path to ffmpeg.')
parser.add_argument('--ffprobe', action='store', dest='ffprobe_path', default='ffprobe', type=str, help='The full path to ffprobe. Use if you need to specify a custom path to ffprobe.')

args = parser.parse_args()
