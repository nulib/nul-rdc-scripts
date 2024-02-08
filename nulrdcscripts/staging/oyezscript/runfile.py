import os
from setupparser import args

ext = [".wav", ".mp3"]
input_path = os.path.normpath(args.input_path)
output_path = os.path.normpath(args.output_path)
isDIRTF = os.path.isdir(args.input_path)

if isDIRTF:
    for files in input_path:
        filename = os.path.basename(files)
        filename, file_ext = os.path.splitext(filename)
        if file_ext in ext:
            command = (
                args.mediainfo_path,
                " -i ",
                input_path,
                " --LogFile=",
                output_path,
                ".json",
            )
        else:
            pass
