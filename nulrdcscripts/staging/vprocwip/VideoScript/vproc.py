import sys
import os
from nulrdcscripts.staging.vprocwip import setup, assists, csvwork
from nulrdcscripts.tools.FFProbeDataReport import main as ffprobedatareportmain

if sys.version_info[0] < 3:
    raise Exception("Python 3 or higher is required")


def single_video(input, output):
    """Runs only if there is a single video in the folder and no subfolders"""
    for file in os.listdir(input):
        if file.endswith(".mkv"):
            inputfilepath = os.path.join(input, file)
            input_abs_path = os.path.abspath(inputfilepath)
            baseFilename = file.replace(".mkv", "")
            frameMD5File = baseFilename + ".framemd5"
            frameMD5Path = os.path.join(output, frameMD5File)
            accessFile = baseFilename + ".mp4"
            accessFilePath = os.path.join(output, accessFile)

            inputMetaData = assists.ffprobereport(file, inputfilepath)
            print("*Checking inventory for", baseFilename + "*")
            item_csvDict = csvwork.get(baseFilename)
            input_metadata = ffprobedatareportmain.generalreport(file, input_abs_path)


def batchT1(input, output):
    """Runs only if there are multiple subfolders containing mkv files"""


def batchT2(input, output):
    """Runs only if there are more than one mkv file in the project folder and no subfolders"""
    pass


def main():
    indir = setup.input_check()
    outdir = setup.output_check()
    # Sets the paths for the softwares to check
    ffmpeg_path = setup.set_path("ffmpeg")
    mediaconch_path = setup.set_path("mediaconch")
    ffprobe_path = setup.set_path("ffprobe")
    # Checks if these paths exist
    setup.exists(ffmpeg_path)
    setup.exists(mediaconch_path)
    setup.exists(ffprobe_path)
    # Checks that the mixdown provided (optional) is valid
    setup.checkmixdown()
    csvInventory = os.path.join(indir, "transcode_code.csv")
    csvDict = assists.import_csv(csvInventory)
    runmethod = setup.runmethod(indir)

    if runmethod == "batchT1":
        batchT1(indir, outdir)
    elif runmethod == "single":
        single_video(indir, outdir)
    elif runmethod == "batchT2":
        batchT2(indir, outdir)
