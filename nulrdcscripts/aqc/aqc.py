#!/usr/bin/env python3

import sys
import os
import subprocess
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import re
import json
from operator import itemgetter
from itertools import *
from nulrdcscripts.aqc.parser import args

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

ASETNSAMPLES = 96000
FLAT_FACTOR_THRESH = 15
COOLDOWN = 5
SILENCE_MIN_LENGTH = 5
ENTROPY_THRESH = .5

def main():

    # setup paths
    if not os.path.isfile(args.infile):
        print("ERROR: " + args.infile + " could not be opened")
        quit()
    
    if not args.infile.endswith(".wav"):
        print("ERROR: input must be a .wav file")
        quit()

    infile = os.path.normpath(args.infile)
    txtfile = os.path.splitext(infile)[0] + ".txt"
    jsonfile = os.path.splitext(infile)[0] + ".json"

    jsondata = {}

    adf = get_astats(infile, txtfile)

    if False:
        lstats = get_lstats(infile)
        jsondata.update(print_lstats(lstats))

    jsondata.update(find_clipping(adf))
    jsondata.update(find_silence(adf))

    with open(jsonfile, "w", encoding='utf-8') as f:
        json.dump(jsondata, f, ensure_ascii=False, indent=4)

    graph_astats(adf)

def get_astats(infile, outfile):
    
    # replace backslashes to forward slashes 
    ff_outfile = outfile.replace("\\","/")
    # delimit any colons
    ff_outfile = ff_outfile.replace(":", "\\\\:")

    command = [
        "ffmpeg",
        "-i",
        infile,
        "-af",
        "asetnsamples=" + str(ASETNSAMPLES) + ",astats=metadata=1:reset=1,ametadata=print:file=" + ff_outfile,
        "-f",
        "null",
        "-"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # load frame data into a dict
    # this code akes more sense when you view the txt file
    frames = {}
    with open(outfile, "r") as f:
        for line in f:
            # add new frame
            if line.startswith("frame"):
                # each frame line has 3 numbers: frame, pts, and pts_time
                nums = re.findall(r'-?\d+\.?\d*', line)
                frame_num = int(nums[0])
                pts = int(nums[1])
                pts_time = float(nums[2])
                frame = {}
                frame.update({"pts": pts})
                frame.update({"pts_time": pts_time})
                frames.update({frame_num: frame})
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

def get_lstats(infile):

    lstats = {}

    command = [
        "ffmpeg",
        "-i",
        infile,
        "-af",
        "loudnorm=print_format=json",
        "-f",
        "null",
        "-"
    ]
    output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode().splitlines()
    start_index = -1
    for index, line in enumerate(output):
        if line.startswith("[Parsed_loudnorm"):
            start_index = index + 2
    
    for line in output[start_index:start_index + 10]:
        if "normalization_type" in line:
            continue

        inquotes = re.findall(r'"(.+?)"', line)
        lstats.update({inquotes[0]: float(inquotes[1])})
    
    return lstats

def print_lstats(lstats):

    print("Loudness")
    print("----------------------")
    print(f"Max TP:\t{lstats["input_tp"]:9.2f} dBTP")
    print(f"LUFS-I:\t{lstats["input_i"]:9.2f} LUFS")
    print(f"LRA:\t{lstats["input_lra"]:9.2f} LU\n")

    loudness_dict = {
        "Loudness": {
            "Max TP":lstats["input_tp"],
            "LUFS-I":lstats["input_i"],
            "LRA":lstats["input_lra"],
        }
    }

    return loudness_dict

def find_clipping(adf):
    # find frames with clipping (flat factor being greater than a given threshold)
    flats = adf.index[adf['Overall.Flat_factor'] > FLAT_FACTOR_THRESH].tolist()
    
    digi_clips = []
    source_clips  = []

    for flat in flats:
        if adf["Overall.Peak_level"][flat] > -.0004:
            digi_clips.append(flat)
        else:
            source_clips.append(flat)

    clipping_data = {}
    digi_clip_data = print_warnings(digi_clips, "Potential digital clipping", adf)
    if(digi_clip_data):
        clipping_data.update(digi_clip_data)
    source_clip_data = print_warnings(source_clips, "Potential source clipping", adf)
    if(source_clip_data):
        clipping_data.update(source_clip_data)

    return {
        "Clipping": clipping_data
    }

def find_silence(adf):
    silences = adf.index[adf['Overall.Entropy'] < ENTROPY_THRESH].tolist()

    silent_data = print_warnings(silences, "Potential silence", adf, SILENCE_MIN_LENGTH)

    return {
        "Silence": silent_data
    }
    

def print_warnings(timestamps, warning, adf, min_length=0):

    warnings = {}

    # create groups of consecutive frames
    groups = []
    for k, g in groupby(enumerate(timestamps), lambda x: x[0]-x[1]):
        groups.append(list(map(itemgetter(1), g)))

    if not groups:
        return
    
    long_groups = []
    for group in groups:
        if len(group) >=  min_length:
            long_groups.append(group)
        
    groups = long_groups

    for group in groups:
        start_sec = adf['pts_time'][group[0]]
        end_sec = adf['pts_time'][group[-1]]
        # format times
        start_time = sec2time(start_sec)
        end_time = sec2time(end_sec)

        # for short durations, treat the clipping as a single event
        if end_sec - start_sec < COOLDOWN:
            print(warning + ": " + start_time)
            warnings.update({start_time: warning})
        else:
            print(warning + ": " + start_time + " to " + end_time)
            warnings.update({(start_time + " - " + end_time): warning})

    print()
    return warnings

def graph_astats(adf):
    columns = [
        "Overall.RMS_level", 
        "Overall.Entropy",  
    ]
    adf.plot(x='pts_time',y=columns, subplots=True, layout=(2,1))
    plt.show()

def df_print(df):
    # print with my own settings
    with pd.option_context('display.max_rows', 8,
                    'display.max_columns', 4,
                    'display.precision', 2,
                    ):

        print(df)

def sec2time(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60

    return f"{h:02d}:{m:02d}:{s:02d}"

def sec2mstime(seconds):
    h = int(seconds // 3600)
    m = int(seconds % 3600 // 60)
    s = seconds % 3600 % 60

    return f"{h:02d}:{m:02d}:{s:05.2f}"

if __name__ == "__main__":
    main()
