#!/usr/bin/env python3

import sys
import os
import subprocess
from datetime import timedelta
import pandas as pd
import re
from operator import itemgetter
from itertools import *
from nulrdcscripts.aqc.parser import args

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

ASETNSAMPLES = 1024
FLAT_FACTOR_THRESH = 10
COOLDOWN = .02

def main():

    # setup paths
    if not os.path.isfile(args.infile):
        print("ERROR: " + args.infile + " could not be opened")
        quit()
    
    if not args.infile.endswith(".wav"):
        print("ERROR: input must be a .wav file")
        quit()

    infile = os.path.normpath(args.infile)
    outfile = os.path.splitext(infile)[0] + ".txt"
    
    # create txt with astats data and load txt into dataframe
    create_txt(infile, outfile)
    adf = load_txt(outfile)

    # find frames with clipping (flat factor being greater than a given threshold)
    flats = adf.index[adf['Overall.Flat_factor'] > FLAT_FACTOR_THRESH].tolist()
    # create groups of consecutive frames
    groups = []
    for k, g in groupby(enumerate(flats), lambda x: x[0]-x[1]):
        groups.append(list(map(itemgetter(1), g)))

    for group in groups:
        start_sec = adf['pts_time'][group[0]]
        end_sec = adf['pts_time'][group[-1]]
        # format times
        start_time = timedelta(seconds=start_sec)
        end_time = timedelta(seconds=end_sec)

        # for short durations, treat the clipping as a single event
        if end_sec - start_sec < COOLDOWN:
            print("Clipping at " + str(start_time))
        else:
            print("Clipping from " + str(start_time) + " to " + str(end_time))


        # print(flats)

def create_txt(infile, outfile):
    
    # replace backslashes to forward slashes 
    ff_outfile = outfile.replace("\\","/")
    # delimit any colons
    ff_outfile = ff_outfile.replace(":", "\\\\:")

    ffmpeg_command = [
        "ffmpeg",
        "-i",
        infile,
        "-af",
        "asetnsamples=" + str(ASETNSAMPLES) + ",astats=metadata=1:reset=1,ametadata=print:file=" + ff_outfile,
        "-f",
        "null",
        "-"
    ]
    subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def load_txt(file):
    # load frame data into a dict
    # this code akes more sense when you view the txt file
    frames = {}
    with open(file, "r") as f:
        for line in f:
            # add new frame
            if line.startswith("frame"):
                # each frame line has 3 numbers: frame, pts, and pts_time
                nums = re.findall(r'-?\d+\.?\d*', line)
                frame = int(nums[0])
                pts = int(nums[1])
                pts_time = float(nums[2])
                frames = {}
                frames.update({"pts": pts})
                frames.update({"pts_time": pts_time})
                frames.update({frame: frames})
            # add data to existing frame
            else:
                # fine value after equals sign
                value_string = re.search(r'=(.*)', line).group(1)
                if value_string == "nan":
                    value = None
                else:
                    value = float(value_string)
                # add to most recently added frame
                last = list(frames)[-1]
                key = re.search('lavfi.astats.(.*?)=', line).group(1)
                frames[last].update({key: value})

    return pd.DataFrame.from_dict(frames, orient='index')

def df_print(df):
    # print with my own settings
    with pd.option_context('display.max_rows', 8,
                    'display.max_columns', 4,
                    'display.precision', 2,
                    ):

        print(df)

if __name__ == "__main__":
    main()
