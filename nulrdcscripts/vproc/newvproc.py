import argparse
import sys
import os
import subprocess
import datetime
import progressbar
import nulrdcscripts.vproc.setup as setup
import nulrdcscripts.vproc.helpers as helpers
import nulrdcscripts.vproc.csvfunctions as csvfunctions
from nulrdcscripts.vproc.params import args
from nulrdcscripts.vproc import assists
from nulrdcscripts.vproc import corefuncs

if sys.version_info[0] < 3:
    raise Exception("Python 3 or higher is required")


def main():
    ac_identifier = "a"
    inventory_name = "transcode_inventory.csv"
    if not args.input_policy:
        mkvPolicy = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/mediaconch_policies/AJA_NTSC_VHA-2SAS-MKV.xml",
        )
    else:
        mkvPolicy = args.input_policy

    indir = setup.input_check()
    outdir = setup.output_check(indir)
    setup.noReturnchecks(mkvPolicy)
    csvDict = csvfunctions.checkandCreate(inventory_name, indir)
    csvHeaderList = csvfunctions.setHeaderList()
    print("**Starting Process**")

    if args.batch:
        batch_video(indir, outdir)
    else:
        single_video_folder(indir, outdir)


def batch_video(indir, outdir):
    for subdir in os.listdir(indir):
        subdir = os.path.join(indir, subdir)
        if os.path.isdir(subdir):
            if not os.path.isfile(os.path.join(subdir, "qc_log.csv")):
                single_video_folder(subdir, subdir)


def single_video_folder(indir, outdir):
    for mkvFile in (indir, "*.mkv"):
        dirPath = os.path.abspath(indir)
        mkvFilePath = os.path.abspath(os.path.join(indir + mkvFile))
        baseFileName = mkvFile.replace("_p.mkv", "")
        accFile = os.path.abspath("indir" + baseFileName + "_a.mp4")
        mkvBaseFilename = mkvFile.replace(".mkv", "")
        md5Pfile = mkvBaseFilename + ".md5"
        md5PAbsPath = os.path.join (dirPath, md5Pfile)
        md5Afile = baseFileName + ".md5"
        md5AAbsPath = os.path.join (dirPath,md5Afile)

        inputMeta = assists.ffprobereport(mkvFile,indir)
        audioStreamCounter = assists.extractAudioStreamCounter(inputMeta)
        assists.generatechecksum(mkvFile,md5PAbsPath)
        print("***Encoding your file to h264***")
        corefuncs.two_pass_h264_encoding(mkvFile,audioStreamCounter,accFile)
        print("***File successfully encoded***")
        assists.generatechecksum(accFile,md5AAbsPath)
