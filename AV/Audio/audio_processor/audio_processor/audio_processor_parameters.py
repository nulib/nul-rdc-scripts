#!/usr/bin/env python3

'''
Argument parser for in-house AJA v210/mov to ffv1/mkv script
'''

import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', action='store', dest='input_path', type=str, help='full path to input folder')
parser.add_argument('--output', '-o', action='store', dest='output_path', type=str, help='full path to output folder')
parser.add_argument('--sox', action='store', dest='sox_path', default='sox', type=str, help='For setting a custom sox path')
parser.add_argument('--bwfmetaedit', action='store', dest='metaedit_path', default='bwfmetaedit', type=str, help='For setting a custom BWF Metaedit path')
parser.add_argument('--ffmpeg', action='store', dest='ffmpeg_path', default='ffmpeg', type=str, help='For setting a custom ffmpeg path')
parser.add_argument('--ffprobe', action='store', dest='ffprobe_path', default='ffprobe', type=str, help='For setting a custom ffprobe path')
parser.add_argument('--mediaconch', action='store', dest='mediaconch_path', default='mediaconch', type=str, help='For setting a custom mediaconch path')
parser.add_argument('--verbose', required=False, action='store_true', help='view ffmpeg output when transcoding')
parser.add_argument('--transcode', '-t', required=False, action='store_true', dest='transcode', help='Transcode access files')
parser.add_argument('--write_metadata', '-w', required=False, action='store_true', dest='write_bwf_metadata', help='Write Broadcast WAVE metadata to Preservation file')
parser.add_argument('--reset_Timereference', '-r', required=False, action='store_true', dest='reset_timereference', help='Reset the time reference of a BWF file to 00:00:00.000')
#parser.add_argument('--skipac', required=False, action='store_true', dest='skip_ac', help='skip access copy transcoding')
parser.add_argument('--skipspectrogram', required=False, action='store_true', dest='skip_spectrogram', help='skip generating spectrograms')
parser.add_argument('--p_policy', required=False, action='store', dest='input_policy', help='Mediaconch policy for preservation files')
parser.add_argument('--a_policy', required=False, action='store', dest='output_policy', help='Mediaconch policy for access files')


args = parser.parse_args()
