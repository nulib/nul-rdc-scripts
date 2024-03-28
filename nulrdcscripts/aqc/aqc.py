#!/usr/bin/env python3

"""
For running automated audio quality control on .wav and .mkv files.
"""

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import re
import json
import csv
from colorama import Style, Fore, Back
from progressbar import *
import nulrdcscripts.aqc.warnings as warnings
import nulrdcscripts.aqc.helpers as helpers
import nulrdcscripts.aqc.ff_helpers as ff_helpers
import nulrdcscripts.aqc.inventory_helpers as i_helpers
from nulrdcscripts.aqc.parser import args

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")


# Global variables static throughout script.
# Use to set/tweak parameters.
ASETNSAMPLES = 48000
""" size (in samples) of audio chunk/frame analyzed in astats filter"""
FLAT_FACTOR_THRESH = 15
"""threshold for flatness to be considered clipping"""
COOLDOWN = 5
"""length that a warning is considered a duration instead of separate events"""
SILENCE_MIN_LENGTH = 10
"""minimum length for a silent period to be counted"""
ENTROPY_THRESH = .3
"""upper threshold for entropy to be considered silence"""

def main():

    """
    Runs qc on a single file or a project directory. 
    Writes output to json file.
    """

    wav_policy = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "mediaconch_policies/wav_policy.xml",
    )
    mkv_policy = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "mediaconch_policies/mkv_policy.xml")

    jsondata = {}

    # validate/find inventory path
    if args.inventory:
        i_helpers.check_inventory(args.inventory)
        inventory_path = args.inventory
    else:
        inventory_path = i_helpers.find_inventory(args.inpath)
    
    # initialize inventory
    if inventory_path:
        inventory_dictlist = i_helpers.load_inventory(inventory_path)
    else:
        inventory_dictlist = []

    # input is a file, run a single file
    if os.path.isfile(args.inpath):
        jsonfile = os.path.splitext(args.inpath)[0] + ".json"
        filename = os.path.basename(args.inpath)

        if inventory_path:
            # inventory filename doesn't have extension or _p
            inv_filename = os.path.splitext(filename)[0]
            if inv_filename.endswith("_p"):
                inv_filename = inv_filename[:-2]
            # search inventory for file
            for index, item in enumerate(inventory_dictlist):
                if item["filename"] == inv_filename:
                    
                    inventory_dictlist[index]["found"] = True

                    # run mediaconch policy
                    if filename.endswith(".mkv"):
                        file_check = helpers.mediaconch_policy_check(args.inpath, mkv_policy)
                    elif filename.endswith(".wav"):
                        file_check = helpers.mediaconch_policy_check(args.inpath, wav_policy)
                    inventory_dictlist[index]["file_check"] = file_check

                    # get astats data
                    file_data = qc_file(file)
                    jsondata.update({filename: file_data})
                    # update inventory info
                    inventory_dictlist[index].update({
                        "clipping": ("Clipping" in jsondata[filename]),
                        "silence": ("Silence" in jsondata[filename])
                    })
        # if inventory wasn't loaded
        else:

            # get astats data
            file_data = qc_file(args.inpath)
            jsondata.update({filename: file_data})
            # run mediaconch policy
            if filename.endswith(".mkv"):
                file_check = helpers.mediaconch_policy_check(args.inpath, mkv_policy)
            elif filename.endswith(".wav"):
                file_check = helpers.mediaconch_policy_check(args.inpath, wav_policy)
            # add entry to inventory
            inventory_dictlist.append({
                "filename": filename,
                "found": True,
                "file_check": file_check,
                "clipping": ("Clipping" in jsondata[filename]),
                "silence": ("Silence" in jsondata[filename])
            })
            # add astats data
            jsondata.update({filename: file_data})


    # input is a directory, run through every p file
    elif os.path.isdir(args.inpath):
        jsonfile = os.path.join(args.inpath, os.path.basename(args.inpath) + ".json")

        # go though every folder
        dirs = helpers.get_immediate_subdirectories(args.inpath)
        for dirname in dirs:
            pdir = os.path.join(args.inpath, dirname, "p")
            if os.path.isdir(pdir):
                for path, dirs, filenames in os.walk(pdir):
                    for filename in filenames:
                        
                        # ignores any files that aren't .mkv or .wav in p folders
                        if filename.endswith(".mkv") or filename.endswith(".wav"):
                            file = os.path.join(path, filename)
                            # if an inventory was loaded
                            if inventory_path:
                                # inventory filename doesn't have extension or _p
                                inv_filename = os.path.splitext(filename)[0]
                                if inv_filename.endswith("_p"):
                                    inv_filename = inv_filename[:-2]
                                # search inventory for file
                                for index, item in enumerate(inventory_dictlist):
                                    if item["filename"] == inv_filename:
                                        
                                        inventory_dictlist[index]["found"] = True

                                        # run mediaconch policy
                                        if filename.endswith(".mkv"):
                                            file_check = helpers.mediaconch_policy_check(file, mkv_policy)
                                        elif filename.endswith(".wav"):
                                            file_check = helpers.mediaconch_policy_check(file, wav_policy)
                                        inventory_dictlist[index]["file_check"] = file_check

                                        # get astats data
                                        file_data = qc_file(file)
                                        jsondata.update({filename: file_data})
                                        # update inventory info
                                        inventory_dictlist[index].update({
                                            "clipping": ("Clipping" in jsondata[filename]),
                                            "silence": ("Silence" in jsondata[filename])
                                        })
                            # if inventory wasn't loaded
                            else:

                                # get astats data
                                file_data = qc_file(os.path.join(path, filename))
                                jsondata.update({filename: file_data})
                                # run mediaconch policy
                                if filename.endswith(".mkv"):
                                    file_check = helpers.mediaconch_policy_check(file, mkv_policy)
                                elif filename.endswith(".wav"):
                                    file_check = helpers.mediaconch_policy_check(file, wav_policy)
                                # add entry to inventory
                                inventory_dictlist.append({
                                    "filename": filename,
                                    "found": True,
                                    "file_check": file_check,
                                    "clipping": ("Clipping" in jsondata[filename]),
                                    "silence": ("Silence" in jsondata[filename])
                                })
                                # add astats data
                                jsondata.update({filename: file_data})
    else:
        print("ERROR: " + args.inpath + " could not be opened")
        quit()

    print()

    # print any inventory items that weren't found
    for item in inventory_dictlist:
        if not item["found"]:
            print(Fore.RED + "Warning: " + Style.BRIGHT 
                  + item["filename"] + Style.RESET_ALL 
                  + Fore.RED + " not found in directory!")
            print(Style.RESET_ALL)
    csvfile = os.path.join(os.path.dirname(jsonfile), "aqc_log.csv")
    # write the inventory to a csv file, shows a quick rundown of the qc
    helpers.write_csv(csvfile, inventory_dictlist)

    # print final message and write json file with more detailed info
    print(Fore.LIGHTCYAN_EX + "***QC Finished***" + Style.RESET_ALL)
    print("general output in " + csvfile)
    with open(jsonfile, "w", encoding='utf-8') as f:
        print("detailed output in " + jsonfile + "\n")
        json.dump(jsondata, f, ensure_ascii=False, indent=4)

def qc_file(file: str):

    """
    _summary_

    :param str file: fullpath to input file
    :return: qc data formatted for json
    :rtype: dict
    """

    infile = os.path.normpath(file)
    
    # setup astats output file
    txtfile = os.path.splitext(infile)[0] + ".txt"

    # print message
    infilename = os.path.basename(infile)
    print("\n" + Fore.LIGHTCYAN_EX + infilename + Style.RESET_ALL)

    # get sample rate and setup variables based on it
    sample_rate = ff_helpers.get_sample_rate(infile)
    pt_time = ASETNSAMPLES / sample_rate
    silence_min_length = SILENCE_MIN_LENGTH / pt_time

    jsondata = {}

    # get astats
    adf = get_astats(infile, txtfile)
        

    # get loudness stats
    if args.lstats:
        lstats = get_lstats(infile)
        if args.verbose:
            helpers.print_lstats(lstats)
        jsondata.update({"Loudness": lstats})
    
    # find clipping
    if args.find_clipping:
        clipping = find_clipping(adf, pt_time)
        if clipping:
            jsondata.update({"Clipping": clipping})
            if args.verbose:
                helpers.print_warnings(clipping)

    # find silences
    if args.find_silence:
        silence = find_silence(adf, silence_min_length, pt_time)
        if silence:
            jsondata.update({"Silence": silence})
            if args.verbose:
                helpers.print_warnings(silence)

    # plot graphs
    if args.plot:
        graph_astats(adf)

    return jsondata

def get_astats(infile: str, outfile: str):

    """
    Generates audio stats, writing them to text file.
    Then reads them in and puts them in pandas dataframe

    :param str infile: fullpath to input file
    :param str outfile: fullpath to output txt file
    :return: audio stats
    :rtype: pandas.DataFrame
    """

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
    # run ffmpeg command w progress bar
    ff_helpers.ff_progress_bar(command, "Generating astats")

    # read in text file as dict
    frames = parse_astats(outfile)

    # return dict as dataframe
    return pd.DataFrame.from_dict(frames, orient='index')

def parse_astats(txtfile: str):

    """
    Reads astats data from txt file and pasres it into dict

    :param str txtfile: fullpath to text file w astats data
    :return: astats data
    :rtype: dict
    """

    # load frame data into a dict
    # this code akes more sense when you view the txt file
    frames = {}

    # used in progress bar
    with open(txtfile, "r") as f:
        length = len(f.readlines())

    # read through each line of text file updating progress throughout
    with ProgressBar(widgets=helpers.default_widgets("Parsing astats   "), max_value=length) as bar:
        with open(txtfile, "r") as f:
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

def get_lstats(infile: str):

    """
    Gets loudness data from ffmpeg loudnorm filter

    :param str infile: fullpath to input file
    :return: loudness stats: max true peak, integrated LUFS, and loudness range
    :rtype: dict
    """

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
    # fun ffmpeg command with progress bar
    # returns lines from "[Parsed_loudnorm" to "}"
    output = ff_helpers.ff_progress_bar(command, "Generating lstats", "[Parsed_loudnorm", "}")

    # goes through useful part of output
    for line in output[2:-1]:

        # skip this value as it causes issue with parsing
        if "normalization_type" in line:
            continue

        # grab everything between quotes
        inquotes = re.findall(r'"(.+?)"', line)
        # there should be 2 strings found between quotes, the label(key) and value
        if len(inquotes) == 2:
            # add each key value pair to dict
            lstats.update({inquotes[0]: float(inquotes[1])})
    
    # grab these 3 values and change the labels to be more readable
    parsed_stats = {
        "Max TP":lstats["input_tp"],
        "LUFS-I":lstats["input_i"],
        "LRA":lstats["input_lra"],
    }

    return parsed_stats

def find_clipping(adf: pd.DataFrame, pt_time: float):

    """
    Finds and returns digital and source clipping

    :param pandas.DataFrame adf: DataFrame with astats data
    :param float pt_time: length of each frame in seconds
    :return: list of clipping instances
    :rtype: dict
    """

    # find frames with clipping (flat factor being greater than a given threshold)
    flat_frames = adf.index[adf['Overall.Flat_factor'] > FLAT_FACTOR_THRESH].tolist()
    
    # groups the warnings so you don't get bombarded with a warning for every single bad frame
    flats = warnings.group(flat_frames, pt_time, COOLDOWN)

    clips = {}

    # sort the clipping by digital and source
    for i, flat in enumerate(flats):

        if adf["Overall.Peak_level"][flat[0]] > -.0004:
            clips.update({"Potential digital clipping" + str(i): flat})
        else:
            clips.update({"Potential source clipping" + str(i): flat})

    # parse the warnings into a readable dict
    clipping_data = warnings.parse(clips, pt_time, COOLDOWN)
    
    return clipping_data

def find_silence(adf: pd.DataFrame, silence_min_length: float, pt_time: float):

    """
    Finds and returns silent periods in the file

    :param pandas.DataFrame adf: DataFrame with astats data
    :param float silence_min_length: minimum length in seconds for a silence to count
    :param float pt_time: length of each frame in seconds
    :return: list of silences
    :rtype: dict
    """

    # find all frames where entropy is high
    # this way it catches time when there is a lot of background noise but still 
    # no actual signal
    silent_frames = adf.index[adf['Overall.Entropy'] < ENTROPY_THRESH].tolist()

    # groups the warnings so you don't get bombarded with a warning for every single bad frame
    silences = warnings.group(silent_frames, pt_time, COOLDOWN, silence_min_length)
    silences_dict = {}
    # this nonsense is necessary to use the warnings.parse function, which itself is the way
    # it is so that you can have a single dict with multiple warning types (ie. digital and source clipping)
    for i, s in enumerate(silences):
        key = "Potential silence" + str(i)
        silences_dict.update({key: s})
    # parse the warnings in to a readable dict
    silent_data = warnings.parse(silences_dict, pt_time, COOLDOWN)

    return silent_data

def graph_astats(adf: pd.DataFrame):
    """
    Displays certain graphs of astats. Currently I only use this when I'm tweaking
    thresholds so I haven't made it very usable from an end user perspective.

    :param pandas.DataFrame adf: DataFrame with astats data
    """

    """
    columns = [
        "Overall.Entropy", 
        "Overall.RMS_level",
        "Overall.RMS_difference",  
        "Overall.Flat_factor",
    ]
    adf.plot(x='pts_time',y=columns, subplots=True, layout=(2,2))
    plt.show()
    """

    xaxis = adf["pts_time"][1:-1].to_list()

    columns = [
        "Overall.RMS_level",
        "Overall.Peak_level",  
        "Overall.Entropy", 
        "Overall.Flat_factor",
    ]

    if os.path.isfile(args.inpath):
        graphs_dir = os.path.join(os.path.dirname(args.inpath), "graphs")
    else:
        graphs_dir = os.path.join(args.inpath, "graphs")
    if not os.path.isdir(graphs_dir):
        os.mkdir(graphs_dir)

    for column in columns:
        
        if column == "Overall.Entropy":
            plt.axhline(y = ENTROPY_THRESH, color = 'r', linestyle = ':')
        if column == "Overall.Flat_factor":
            plt.axhline(y = FLAT_FACTOR_THRESH, color = 'r', linestyle = ':')

        yaxis = adf[column][1:-1].to_list()
        plt.plot(xaxis, yaxis)
        plt.xlabel("time (s)")
        plt.title(column)
        padding = (max(yaxis) - min(yaxis)) / 20.
        plt.ylim(min(yaxis) - padding, max(yaxis) + padding)
        
        image_path = os.path.join(graphs_dir, column + ".png")
        plt.savefig(image_path)
        plt.clf()

if __name__ == "__main__":
    main()
