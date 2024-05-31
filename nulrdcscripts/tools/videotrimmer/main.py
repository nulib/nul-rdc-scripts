import os
import subprocess
from datetime import datetime
from nulrdcscripts.tools.videotrimmer.params import args

inputfileAbsPath = os.path.abspath(args.input_path)
inputBaseFileName = os.path.basename(args.input_path)
filename,ext = os.path.splitext(inputBaseFileName)
inputfileDir = os.path.dirname(args.input_path)
outputFilename = inputBaseFileName.replace(ext,"_editted"+ext)
outputfileAbsPath = os.path.join(inputfileDir,outputFilename)
ffmpegPath = os.path.abspath(args.ffmpeg_path)
startTime = args.start_time
endTime = args.end_time
def checkTime (time,timetype):
    try:
        timeFormat = "%H:%M:%S"
        validTime = datetime.strptime(time,timeFormat)
    except:
        raise Exception ("Valid Time was not provided for" + timetype)

def trimVideo(inputfileAbsPath,outputfileAbsPath,startTime,endTime):
    checkTime (startTime, 'start time')    
    checkTime (endTime, 'end time')

    command = ffmpegPath + " " + "-i" + " " + inputfileAbsPath+ " " +"-c copy -ss"+ " " +startTime+ " " + "-to"+ " " + endTime+ " " + outputfileAbsPath
    subprocess.run(command)
def main():
    pass