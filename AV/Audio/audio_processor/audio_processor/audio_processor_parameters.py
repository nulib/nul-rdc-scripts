#!/usr/bin/env python3

'''
Argument parser for in-house AJA v210/mov to ffv1/mkv script
'''

import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', action='store', dest='input_path', type=str, help='full path to input folder')
parser.add_argument('--output', '-o', action='store', dest='output_path', type=str, help='full path to output folder')
parser.add_argument('--ffmpeg', action='store', dest='ffmpeg_path', default='ffmpeg', type=str, help='For setting a custom ffmpeg path')
parser.add_argument('--ffprobe', action='store', dest='ffprobe_path', default='ffprobe', type=str, help='For setting a custom ffprobe path')
parser.add_argument('--qcli', action='store', dest='qcli_path', default='qcli', type=str, help='For setting a custom qcli path')
parser.add_argument('--mediaconch', action='store', dest='mediaconch_path', default='mediaconch', type=str, help='For setting a custom mediaconch path')
parser.add_argument('--verbose', required=False, action='store_true', help='view ffmpeg output when transcoding')
parser.add_argument('--mixdown', action='store', dest='mixdown', default='copy', type=str, help='How the audio streams will be mapped for the access copy. If excluded, this will default to copying the stream configuration of the input. Inputs include: copy, 4to3, and 4to2. 4to3 takes 4 mono tracks and mixes tracks 1&2 to stereo while leaving tracks 3&4 mono. 4to2 takes 4 mono tracks and mixes tracks 1&2 and 3&4 to stereo.')
parser.add_argument('--slices', action='store', dest='ffv1_slice_count', default='16', choices=[4,6,9,12,16,24,30], type=int, help='Set the FFV1 slice count used by ffmpeg when losslessly transcoding files. Default is 16.')
parser.add_argument('--skipac', required=False, action='store_true', dest='skip_ac', help='skip access copy transcoding')
parser.add_argument('--skipqcli', required=False, action='store_true', dest='skip_qcli', help='skip generating qc tools report')
parser.add_argument('--skipspectrogram', required=False, action='store_true', dest='skip_spectrogram', help='skip generating spectrograms')
parser.add_argument('--keep_filename', required=False, action='store_true', dest='keep_filename', help='MKV preservation master will have the same filename as the source MOV file')
parser.add_argument('--embed_framemd5', required=False, action='store_true', dest='embed_framemd5', help='remux preservation file to embed framemd5')
parser.add_argument('--input_policy', required=False, action='store', dest='input_policy', help='Mediaconch policy for input files')
parser.add_argument('--output_policy', required=False, action='store', dest='output_policy', help='Mediaconch policy for output files')

args = parser.parse_args()
