#!/usr/bin/env python3

import sys
import os
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import re
import datetime
import json
from colorama import Style, Fore
from progressbar import *
from operator import itemgetter
from itertools import *
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
        dirs = get_immediate_subdirectories(args.inpath)
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

    jsondata = {}

    infilename = os.path.basename(infile)
    print("\n" + Fore.LIGHTCYAN_EX + infilename + Style.RESET_ALL)

    if args.find_clipping or args.find_silence:
        sample_rate, seconds, adf = get_astats(infile, txtfile)
        pt_time = ASETNSAMPLES / sample_rate
        silence_min_length = SILENCE_MIN_LENGTH / pt_time
    elif args.plot:
        args.plot = False

    if args.lstats:
        lstats = get_lstats(infile)
        if args.verbose:
            print_lstats(lstats)
        jsondata.update({"Loudness": lstats})
    
    if args.find_clipping:
        clipping = find_clipping(adf, pt_time)
        if clipping:
            jsondata.update({"Clipping": clipping})
            if args.verbose:
                print_warnings(clipping)

    if args.find_silence:
        silence = find_silence(adf, silence_min_length, pt_time)
        if silence:
            jsondata.update({"Silence": silence})
            if args.verbose:
                print_warnings(silence)

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
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    line = ""
    seconds = -1
    with ProgressBar(widgets=default_widgets("Generating astats"), max_value=100) as bar:
        while True:
            out = process.stdout.read(1)
            if out == b'' and process.poll() is not None:
                break
            if out == b'\n' or out == b'\r':
                # if re.search(r'Stream #(\d):(\d): Video', line):
                #     frame_rate = float(re.search(r'(\d+\.\d+) fps', line).group(1))
                if re.search(r'Stream #(\d):(\d): Audio', line):
                    sample_rate = int(re.search(r'(\d+) Hz', line).group(1))
                if "Duration" in line:
                    time = re.search(r'Duration: (.*?),', line).group(1)
                    seconds = get_total_seconds(time)
                if re.search(r'(^size=|frame=)', line):
                    current_time = re.search(r'time=(.*) bi', line).group(1)
                    current_seconds = get_total_seconds(current_time)
                    percent = current_seconds/seconds * 100
                    if percent <= 100:
                        bar.update(current_seconds/seconds * 100)
                line = ""
            elif out != '':
                line = line + out.decode('utf-8')

    # load frame data into a dict
    # this code akes more sense when you view the txt file
    frames = {}

    with open(outfile, "r") as f:
        length = len(f.readlines())

    with ProgressBar(widgets=default_widgets("Parsing astats   "), max_value=length) as bar:
        with open(outfile, "r") as f:
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

    return sample_rate, seconds, pd.DataFrame.from_dict(frames, orient='index')

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
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output = []
    line = ""
    seconds = -1
    writing = False
    with ProgressBar(widgets=default_widgets("Generating lstats"), max_value=100) as bar:
        while True:
            out = process.stdout.read(1)
            if out == b'' and process.poll() is not None:
                break
            if out == b'\n' or out == b'\r':
                if "Duration" in line:
                    time = re.search(r'Duration: (.*?), ', line).group(1)
                    seconds = get_total_seconds(time)
                if re.search(r'(size=|frame=)', line):
                    current_time = re.search(r'time=(.*) bi', line).group(1)
                    current_seconds = get_total_seconds(current_time)
                    percent = current_seconds/seconds * 100
                    if percent <= 100:
                        bar.update(current_seconds/seconds * 100)
                if line.startswith("[Parsed_loudnorm"):
                    writing = True
                if line.startswith("}"):
                    writing = False
                if writing:
                    output.append(line)
                line = ""
            elif out != b'':
                line = line + out.decode('utf-8')

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

def print_lstats(lstats):

    print(f"\n\tMax TP:\t{lstats["Max TP"]:9.2f} dBTP")
    print(f"\tLUFS-I:\t{lstats["LUFS-I"]:9.2f} LUFS")
    print(f"\tLRA:\t{lstats["LRA"]:9.2f} LU")

def print_warnings(warnings):
    print()
    for key in warnings:
        print("\t" + key + ": " + warnings[key])

def find_clipping(adf, pt_time):
    # find frames with clipping (flat factor being greater than a given threshold)
    flat_frames = adf.index[adf['Overall.Flat_factor'] > FLAT_FACTOR_THRESH].tolist()
    
    flats = group_warnings(flat_frames, pt_time)

    clips = {}

    for i, flat in enumerate(flats):

        if adf["Overall.Peak_level"][flat[0]] > -.0004:
            clips.update({"Potential digital clipping" + str(i): flat})
        else:
            clips.update({"Potential source clipping" + str(i): flat})


    clipping_data = parse_warnings(clips, pt_time)
    
    return clipping_data

def find_silence(adf, silence_min_length, pt_time):
    silent_frames = adf.index[adf['Overall.Entropy'] < ENTROPY_THRESH].tolist()

    silences = group_warnings(silent_frames, pt_time, silence_min_length)
    silences_dict = {}
    for i, s in enumerate(silences):
        key = "Potential silence" + str(i)
        silences_dict.update({key: s})
    silent_data = parse_warnings(silences_dict, pt_time)

    return silent_data
    
def group_warnings(timestamps, pt_time, min_length=0):

    # create groups of consecutive frames
    groups = []
    for k, g in groupby(enumerate(timestamps), lambda x: x[0]-x[1]):
        groups.append(list(map(itemgetter(1), g)))

    if not groups:
        return []
    
    long_groups = []
    for group in groups:
        if len(group) >=  min_length:
            long_groups.append(group)

    groups = long_groups

    
    merged_groups = []
    cooldown_frames = int(COOLDOWN/pt_time)
    last_end = -cooldown_frames
    for i, group in enumerate(groups):
        #print(group)
        if group[0] - last_end < cooldown_frames:
            merged_groups[-1].extend(group)
        else:
            merged_groups.append(group)
        last_end = group[-1]

    groups = merged_groups
    
    return groups

def parse_warnings(groups, pt_time):

    if not groups:
        return

    warnings = {}


    for key in groups:
        start_sec = pt_time * groups[key][0]
        end_sec = pt_time * groups[key][-1]
        # format times
        start_time = sec2time(start_sec)
        end_time = sec2time(end_sec)

        label = ''.join([i for i in key if not i.isdigit()])
        # for short durations, treat the clipping as a single event
        if end_sec - start_sec <= COOLDOWN:
            warnings.update({start_time: label})
        else:
            warnings.update({start_time + " - " + end_time: label})

    # print()
    return warnings

def graph_astats(adf):
    columns = [
        "Overall.Entropy", 
        "Overall.RMS_level",
        "Overall.RMS_difference",  
        "Overall.Mean_difference",
    ]
    adf.plot(x='pts_time',y=columns, subplots=True, layout=(2,2))
    plt.show()

def df_print(df):
    # print with my own settings
    with pd.option_context('display.max_rows', 8,
                    'display.max_columns', 4,
                    'display.precision', 2,
                    ):

        print(df)

def default_widgets(label=""):
    widgets = [
        FormatLabel(label + " |"), ' ', 
        Percentage(format='%(percentage)3d%%'), ' ', 
        Bar("#"), ' ',
        Timer(format='Time: %(elapsed)s', timedelta = '0:00:01.00')
        #AdaptiveETA(exponential_smoothing=True, exponential_smoothing_factor=0.1), ' ',
    ]
    return widgets

def get_total_seconds(stringHMS):
   if stringHMS == "N/A":
       return -1
   
   timedeltaObj = datetime.datetime.strptime(stringHMS, "%H:%M:%S.%f") - datetime.datetime(1900,1,1)
   return timedeltaObj.total_seconds()

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

def get_immediate_subdirectories(folder):
    """
    get list of immediate subdirectories of input
    """
    return [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]

if __name__ == "__main__":
    main()
