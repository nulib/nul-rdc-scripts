#!/usr/bin/env python3

import sys
import os
import subprocess
import pandas as pd
import re
from nulrdcscripts.aqc.parser import args

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():

    if not os.path.isfile(args.infile):
        print("ERROR: " + args.infile + " could not be opened")
        quit()
    
    if not args.infile.endswith(".wav"):
        print("ERROR: input must be a .wav file")
        quit()

    infile = os.path.normpath(args.infile)
    outfile = os.path.splitext(infile)[0] + ".txt"

    
    # replace backslashes to forward slashes 
    ff_outfile = outfile.replace("\\","/")
    # delimit any colons
    ff_outfile = ff_outfile.replace(":", "\\\\:")

    asetnsamples = 960

    ffmpeg_command = [
        "ffmpeg",
        "-i",
        infile,
        "-af",
        "asetnsamples=" + str(asetnsamples) + ",astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.Flat_factor:file=" + ff_outfile,
        "-f",
        "null",
        "-"
    ]
    subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    

    frames_dict = {}
    with open(outfile, "r") as f:
        for line in f:
            if line.startswith("frame"):
                nums = re.findall(r'-?\d+\.?\d*', line)
                frame = int(nums[0])
                pts = int(nums[1])
                pts_time = float(nums[2])
                frame_dict = {}
                frame_dict.update({"pts": pts})
                frame_dict.update({"pts_time": pts_time})
                frames_dict.update({frame: frame_dict})
            if line.startswith("lavfi.astats.Overall.Flat_factor"):
                nums = re.findall(r'-?\d+\.?\d*', line)
                flat_factor = float(nums[0])
                last = list(frames_dict)[-1]
                frames_dict[last].update({"flat_factor": flat_factor})
    
    #print(frames_dict)

    audio_data = pd.DataFrame.from_dict(frames_dict)
    print(audio_data)
                

if __name__ == "__main__":
    main()
