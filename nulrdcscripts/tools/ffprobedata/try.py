from params import args
import subprocess
import os


def swapSlashes(item):
    fixed_path = item.replace("\\", "/")
    fixed_path = fixed_path.replace(":", "\\\\:")
    return fixed_path


norm_input = os.path.normpath(args.input_path)
fixed_input = swapSlashes(norm_input)
filepath = norm_input.replace(".mp4", "_framebyframe.xml")
command = [
    args.ffprobe_path,
    "-f",
    "lavfi",
    "movie=" + fixed_input + ",signalstats='stat=tout+vrep+brng'",
    "-show_frames",
    "-of",
    "xml",
]
with open(filepath, "w") as f:
    subprocess.run(command, stdout=f)
    f.close()
