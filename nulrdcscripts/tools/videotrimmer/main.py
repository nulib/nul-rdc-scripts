import os
import subprocess
from datetime import datetime
from nulrdcscripts.tools.videotrimmer.params import args
from nulrdcscripts.tools.checksoftware.main import main as checksoftwaremain


def checkTime(time, timetype):
    try:
        timeFormat = "%H:%M:%S"
        validTime = datetime.strptime(time, timeFormat)
    except:
        raise Exception("Valid Time was not provided for" + timetype)


def setTrimType(start, end):
    if start == "00:00:00" and end != "NA":
        trimType = "newEnd"
    elif start and end == "NA":
        trimType = "newStart"
    else:
        trimType = "between"
    return trimType


def trimVideo(inputfileAbsPath, outputfileAbsPath, startTime, endTime, trimType):
    copy_command = "-c:v copy -c:a copy "
    corecommand = ffmpeg_path + " " + "-i" + " " + inputfileAbsPath
    if trimType == "newEnd":
        command = (
            corecommand
            + " "
            + "-to"
            + " "
            + endTime
            + " "
            + copy_command
            + outputfileAbsPath
        )
    elif trimType == "between":
        command = (
            corecommand
            + " "
            + "-ss"
            + " "
            + startTime
            + "-to"
            + " "
            + endTime
            + " "
            + outputfileAbsPath
        )
    elif trimType == "newStart":
        command = (
            corecommand
            + " "
            + "-ss"
            + " "
            + startTime
            + " "
            + copy_command
            + outputfileAbsPath
        )
    subprocess.run(command)


input_file = os.path.abspath(args.input_path)
basename, ext = os.path.splitext(os.path.basename(input_file))
output_file = basename + "_editted" + ext
output_path = os.path.join(os.path.dirname(input_file), output_file)
ffmpeg_path = args.ffmpeg_path
startTime = args.start_time
endTime = args.end_time


def main():
    checksoftwaremain(ffmpeg_path)
    checkTime(startTime, "start")
    if endTime != "NA":
        checkTime(endTime, "end")
    else:
        pass
    trimType = setTrimType(startTime, endTime)
    trimVideo(input_file, output_path, startTime, endTime, trimType)


main()
