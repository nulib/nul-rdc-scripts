import os
import subprocess
from nulrdcscripts.staging.vprocwip import args


def basefilename():
    pass


def input_check():
    inputDirTF = os.path.isdir(args.input_path)
    if inputDirTF:
        indir = os.path.abspath(args.input_path)
        return indir
    else:
        raise ValueError("Input path is not a directory")


def output_check():
    if args.output_path == None:
        outdir = os.path.abspath(args.input_path)
    else:
        outdirTF = os.path.isdir(args.output_path)
        if outdirTF:
            outdir = os.path.abspath(args.output_path)
        else:
            raise ValueError("Output path is not a directory")
    return outdir


def set_path(item):
    """Sets the path of the software provided"""
    argslookup = "args." + item + "_path"
    if argslookup == None:
        path = "item"
    else:
        path = os.path.abspath(argslookup)
    return path


def checkmixdown():
    mixdown_list = ["copy", "4to3", "4to2", "2to1"]
    if not args.mixdown in mixdown_list:
        raise ValueError(
            "The audio mixdown provided is not a valid value. /n Please use: copy, 4to3, 4to2, 2to1"
        )


def exists(item):
    """Checks if the provided software is available"""
    if "mediaconch" in item:
        versioncommand = "-v"
    else:
        versioncommand = "-version"

    try:
        subprocess.check_output([item, versioncommand]).decode(
            "ascii"
        ).rstrip().splitlines()[0].split()[2]
    except:
        raise Exception("Error Locating:" + item)


def runmethod(indir):
    for item in os.listdir(indir):
        countfiles = 0
        countfolders = 0

        item_path = os.path.join(indir, item)
        if os.path.isdir(item_path):
            countfolders += 1
        elif os.path.isfile(item_path):
            files = os.path.basefilename(item_path)
            if files.endswith(".mkv"):
                countfiles += 1
            else:
                pass
        if countfolders >= 0 and countfiles == 0:
            runmethod = "batchT1"
            return runmethod
        elif countfolders == 0 and countfiles == 1:
            runmethod = "single"
            return runmethod
        elif countfolders == 0 and countfiles >= 1:
            runmethod = "batchT2"
            return runmethod
        else:
            raise Exception(
                "Your input file structure is not supported. See associated documentation for more information"
            )
