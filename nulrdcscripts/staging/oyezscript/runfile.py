import os
import subprocess
from setupparser import args

ext = [".wav", ".mp3"]
input_path = os.path.normpath(args.input_path)
isDIRTF = os.path.isdir(args.input_path)

if isDIRTF:
    for files in input_path:
        filename, file_ext = os.path.splitext(files)
        if file_ext in ext:
            command = (
                args.mediainfo_path,
                " -i ",
                input_path,
                " --LogFile=",
                filename,
                ".json",
            )
            fullfilename = filename + ".json"
            with open(fullfilename, "w") as f:
                subprocess.run(command, stdout=f)
        else:
            pass
else:
    filename, file_ext = os.path.splitext(input_path)
    if file_ext == ".wav" or file_ext == ".mp3":
        command = (
            args.mediainfo_path,
            "-i",
            input_path,
            "--LogFile=",
            filename,
            ".json",
        )
        fullfilename = filename + ".json"
        with open(fullfilename, "w") as f:
            subprocess.run(command, stdout=f)

    else:
        raise ValueError("This file is not a .wav or .mp3 file.")

filecheck = filename + ".json"
with open(filecheck, "r") as file:
    file.read()
