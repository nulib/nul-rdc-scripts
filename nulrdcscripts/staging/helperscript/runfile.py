import os
import subprocess
from paramparser import args

input_path = os.path.normpath(args.input_path)
fileName = os.path.basename(args.input_path)


command = [
    args.ffprobe_path,
    " -f",
    " lavfi",
    "movie=",
    input_path,
    ",",
    "signalstats",
    " -show_entries",
    " frame_tags",
    " -of flat",
    " >>",
    fileName,
    ".json",
]

subprocess.Popen(command)
