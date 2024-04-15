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


def setFilename(
    input,
    output,
):
    basefilename = os.path.splitext(os.path.basename(input))[0]
    filepath = output + "\\" + basefilename + ".json"
    return filepath


def batchvideos(norm_input, norm_output):
    ext = (".mp4", ".mkv", ".mov")
    for file in norm_input:
        if file.endswith(ext):
            filepath = setFilename(file, norm_output)
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
            with open(filepath, "w") as f:
                subprocess.run(command, stdout=f)
                f.close()
        else:
            raise Exception("There are no eligible files in the supplied directory")


def singlevideo(norm_input, norm_output):
    fixed_input = swapSlashes(norm_input)
    filepath = setFilename(norm_input, norm_output)
    command = [
        args.ffprobe_path,
        "-f",
        "lavfi",
        "movie=" + fixed_input + ",signalstats='stat=tout+vrep+brng'",
        "-show_frames",
        "-of",
        "json",
    ]
    with open(filepath, "w") as f:
        subprocess.run(command, stdout=f)
        f.close()


def main():
    norm_input = os.path.abspath(args.input_path)
    runType = setRunType(norm_input)
    norm_output = setOutput(norm_input, runType)
    if runType == "batch":
        batchvideos(norm_input, norm_output)
    else:
        singlevideo(norm_input, norm_output)


main()
