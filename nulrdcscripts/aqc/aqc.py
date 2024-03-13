#!/usr/bin/env python3

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import re
import json
from colorama import Style, Fore
from progressbar import *
import nulrdcscripts.aqc.warnings as warnings
import nulrdcscripts.aqc.helpers as helpers
import nulrdcscripts.aqc.ff_helpers as ff_helpers
from nulrdcscripts.aqc.parser import args

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

"""
Global variables static throughout script.
Use to set/tweak parameters.
"""

# size (in samples) of audio chunk/frame analyzed in astats filter
ASETNSAMPLES = 48000
# lower threshold for flatness to be considered clipping
FLAT_FACTOR_THRESH = 15
# length that a warning is considered a duration instead of a single event
COOLDOWN = 5
# minimum length for a silent period to be counted
SILENCE_MIN_LENGTH = 5
# upper threshold for entropy to be considered silence
ENTROPY_THRESH = .3

def main():

    jsonfile = os.path.splitext(args.inpath)[0] + ".json"

    jsondata = {}

    if os.path.isfile(args.inpath):
        jsonfile = os.path.splitext(args.inpath)[0] + ".json"
        jsondata = {os.path.basename(args.inpath): qc_file(args.inpath)}
    elif os.path.isdir(args.inpath):
        jsonfile = os.path.join(args.inpath, os.path.basename(args.inpath) + ".json")
        dirs = helpers.get_immediate_subdirectories(args.inpath)
        for dirname in dirs:
            pdir = os.path.join(args.inpath, dirname, "p")
            if os.path.isdir(pdir):
                for path, dirs, filenames in os.walk(pdir):
                    for filename in filenames:
                        if filename.endswith(".mkv") or filename.endswith(".wav"):
                            file_data = qc_file(os.path.join(path, filename))
                            jsondata.update({filename: file_data})
    else:
        print("ERROR: " + args.inpath + " could not be opened")
        quit()

    print("\n***QC Finished***")
    with open(jsonfile, "w", encoding='utf-8') as f:
        print("output in " + jsonfile + "\n")
        json.dump(jsondata, f, ensure_ascii=False, indent=4)

def qc_file(file):

    infile = os.path.normpath(file)
    txtfile = os.path.splitext(infile)[0] + ".txt"


    infilename = os.path.basename(infile)
    print("\n" + Fore.LIGHTCYAN_EX + infilename + Style.RESET_ALL)

    sample_rate = ff_helpers.get_sample_rate(infile)

    jsondata = {}

    if args.find_clipping or args.find_silence:
        adf = get_astats(infile, txtfile)
        pt_time = ASETNSAMPLES / sample_rate
        silence_min_length = SILENCE_MIN_LENGTH / pt_time
    elif args.plot:
        args.plot = False

    if args.lstats:
        lstats = get_lstats(infile)
        if args.verbose:
            helpers.print_lstats(lstats)
        jsondata.update({"Loudness": lstats})
    
    if args.find_clipping:
        clipping = find_clipping(adf, pt_time)
        if clipping:
            jsondata.update({"Clipping": clipping})
            if args.verbose:
                helpers.print_warnings(clipping)

    if args.find_silence:
        silence = find_silence(adf, silence_min_length, pt_time)
        if silence:
            jsondata.update({"Silence": silence})
            if args.verbose:
                helpers.print_warnings(silence)

    if args.plot:
        graph_astats(adf)

    return jsondata

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
    ff_helpers.ff_progress_bar(command, "Generating astats")

    frames = parse_astats(outfile)

    return pd.DataFrame.from_dict(frames, orient='index')

def parse_astats(file):
    # load frame data into a dict
    # this code akes more sense when you view the txt file
    frames = {}

    with open(file, "r") as f:
        length = len(f.readlines())

    with ProgressBar(widgets=helpers.default_widgets("Parsing astats   "), max_value=length) as bar:
        with open(file, "r") as f:
            for i, line in enumerate(f):
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
                    # find value after equals sign
                    value_string = re.search(r'=(.*)', line).group(1)
                    if value_string == "nan":
                        value = None
                    else:
                        value = float(value_string)
                    # add to most recently added frame
                    last = list(frames)[-1]
                    key = re.search('lavfi.astats.(.*?)=', line).group(1)
                    frames[last].update({key: value})
                bar.update(i)

    return frames

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

    output = ff_helpers.ff_progress_bar(command, "Generating lstats", "[Parsed_loudnorm", "}")

    for line in output[2:-1]:
        if "normalization_type" in line:
            continue

        inquotes = re.findall(r'"(.+?)"', line)
        if len(inquotes) == 2:
            lstats.update({inquotes[0]: float(inquotes[1])})
    
    parsed_stats = {
        "Max TP":lstats["input_tp"],
        "LUFS-I":lstats["input_i"],
        "LRA":lstats["input_lra"],
    }

    return parsed_stats

def find_clipping(adf, pt_time):
    # find frames with clipping (flat factor being greater than a given threshold)
    flat_frames = adf.index[adf['Overall.Flat_factor'] > FLAT_FACTOR_THRESH].tolist()
    
    flats = warnings.group(flat_frames, pt_time, COOLDOWN)

    clips = {}

    for i, flat in enumerate(flats):

        if adf["Overall.Peak_level"][flat[0]] > -.0004:
            clips.update({"Potential digital clipping" + str(i): flat})
        else:
            clips.update({"Potential source clipping" + str(i): flat})

    clipping_data = warnings.parse(clips, pt_time, COOLDOWN)
    
    return clipping_data

def find_silence(adf, silence_min_length, pt_time):
    silent_frames = adf.index[adf['Overall.Entropy'] < ENTROPY_THRESH].tolist()

    silences = warnings.group(silent_frames, pt_time, COOLDOWN, silence_min_length)
    silences_dict = {}
    for i, s in enumerate(silences):
        key = "Potential silence" + str(i)
        silences_dict.update({key: s})
    silent_data = warnings.parse(silences_dict, pt_time, COOLDOWN)

    return silent_data

def graph_astats(adf):
    columns = [
        "Overall.Entropy", 
        "Overall.RMS_level",
        "Overall.RMS_difference",  
        "Overall.Mean_difference",
    ]
    adf.plot(x='pts_time',y=columns, subplots=True, layout=(2,2))
    plt.show()

if __name__ == "__main__":
    main()
