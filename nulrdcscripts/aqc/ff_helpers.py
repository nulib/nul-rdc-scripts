#!/usr/bin/env python3

import subprocess
import re
import nulrdcscripts.aqc.helpers as helpers
from progressbar import *

def get_sample_rate(infile):
    command = [
        "ffprobe",
        "-i",
        infile,
    ]
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    output = output.decode("ascii").splitlines()

    sample_rate = None
    for line in output:
        if re.search(r'Stream #(\d):(\d): Audio', line):
            sample_rate = int(re.search(r'(\d+) Hz', line).group(1))
    return sample_rate

def ff_progress_bar(command, label, write_start=None, write_end=None):

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
                    seconds = helpers.get_total_seconds(time)
                if re.search(r'(size=|frame=)', line):
                    current_time = re.search(r'time=(.*) bi', line).group(1)
                    current_seconds = helpers.get_total_seconds(current_time)
                    percent = current_seconds/seconds * 100
                    if percent <= 100:
                        bar.update(current_seconds/seconds * 100)
                if write_start and line.startswith(write_start):
                    writing = True
                if write_end and line.startswith(write_end):
                    writing = False
                if writing:
                    output.append(line)
                line = ""
            elif out != b'':
                line = line + out.decode('utf-8')

    return output