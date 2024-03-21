#!/usr/bin/env python3

"""
ffmpeg helper functions for aqc.
"""

import subprocess
import re
import nulrdcscripts.aqc.helpers as helpers
from progressbar import *

def get_sample_rate(infile: str):

    """
    Gets the audio sample rate from a file using ffprobe
    Errors may occur if there are multiple audio streams with different sample rates,
    but that really shouldn't ever happen.

    :param str infile: fullpath to input file
    :return: audio sample rate of file
    :rtype: int
    """

    command = [
        "ffprobe",
        "-i",
        infile,
    ]
    # run command and grab the output
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    output = output.decode("ascii").splitlines()

    # read through the output and grab the sample rate
    sample_rate = None
    for line in output:
        if re.search(r'Stream #(\d):(\d): Audio', line):
            sample_rate = int(re.search(r'(\d+) Hz', line).group(1))
    return sample_rate

def ff_progress_bar(command: list, label: str, begin_save: str = None, stop_save: str = None):

    """
    Runs an ffmpeg command while parsing the live output to update a progress bar.
    Also can grab certain lines of output

    :param list command: ffmpeg command, each argument as an item in a list
    :param str label: to be displayed in the progress bar
    :param str begin_save: begins saving output lines when a line starts with this string
    :param str stop_save: stops saving output lines when a line start with this string
    :return: saved output, can be empty
    :rtype: list[str]
    """

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output = []
    line = ""
    seconds = -1
    writing = False
    with ProgressBar(widgets=helpers.default_widgets(label), max_value=100) as bar:
        while True:
            out = process.stdout.read(1)
            if out == b'' and process.poll() is not None:
                break
            if out == b'\n' or out == b'\r':
                if "Duration" in line:
                    time = re.search(r'Duration: (.*?), ', line).group(1)
                    seconds = helpers.hms2seconds(time)
                if re.search(r'(size=|frame=)', line):
                    current_time = re.search(r'time=(.*) bi', line).group(1)
                    current_seconds = helpers.hms2seconds(current_time)
                    percent = current_seconds/seconds * 100
                    if percent <= 100:
                        bar.update(current_seconds/seconds * 100)
                if begin_save and line.startswith(begin_save):
                    writing = True
                if stop_save and line.startswith(stop_save):
                    writing = False
                if writing:
                    output.append(line)
                line = ""
            elif out != b'':
                line = line + out.decode('utf-8')

    return output