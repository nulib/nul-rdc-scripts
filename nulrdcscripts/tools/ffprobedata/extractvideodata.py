import os
import subprocess
from nulrdcscripts.tools.ffprobedata.params import args


def swapSlashes(item):
    fixed_path = item.replace("\\", "/")
    fixed_path = fixed_path.replace(":", "\\\\:")
    return fixed_path


def setRunType(norm_input):
    batchTF = os.path.isdir(norm_input)
    if batchTF:
        runType = "batch"
    else:
        runType = "file"
    return runType


def setOutput(norm_input, runType):
    if args.output_path == None:
        if runType == "file":
            norm_output = os.path.abspath(os.path.dirname(norm_input))
        else:
            norm_output = norm_input + "/videodata"
    else:
        norm_output = os.path.abspath(args.output_path)
    return norm_output


def batchvideos():
    pass


def singlevideo(norm_input):
    fixed_input = swapSlashes(norm_input)
    command = [
        args.ffprobe_path,
        "-f",
        "lavfi",
        "movie=" + fixed_input + ",signalstats='stat=tout+vrep+brng'",
        "-show_frames",
        "-of",
        "json",
    ]
    print(command)
    subprocess.run(command)


def main():
    norm_input = os.path.abspath(args.input_path)
    print(norm_input)
    runType = setRunType(norm_input)
    norm_output = setOutput(norm_input, runType)
    if runType == "batch":
        batchvideos()
    else:
        singlevideo(norm_input)


main()
