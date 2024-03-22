#!/usr/bin/env python3
import os
import subprocess
from nulrdcscripts.vproc.params import args

"""Functions that check and setup the script to run"""

def inventory_check(item_csvDict):
    if item_csvDict is None:
        print("unable to locate file in csv data!")
        inventoryCheck = "FAIL"
    else:
        print("item found in inventory")
        inventoryCheck = "PASS"
    return inventoryCheck


def qcli_check():
    """
    checks that qcli exists by running its -version command
    """
    try:
        subprocess.check_output([args.qcli_path, "-version"]).decode(
            "ascii"
        ).rstrip().splitlines()[0]
    except:
        print("Error locating qcli")
        quit()

def mediaconch_check():
    """
    checks that mediaconch exists by running its -v command
    """
    try:
        subprocess.check_output([args.mediaconch_path, "-v"]).decode(
            "ascii"
        ).rstrip().splitlines()[0]
    except:
        print("Error locating mediaconch")
        quit()

def get_ffmpeg_version():
    """
    Returns the version of ffmpeg
    """
    ffmpeg_version = "ffmpeg"
    try:
        ffmpeg_version = (
            subprocess.check_output([args.ffmpeg_path, "-version"])
            .decode("ascii")
            .rstrip()
            .splitlines()[0]
            .split()[2]
        )
    except:
        print("Error getting ffmpeg version")
        quit()
    return ffmpeg_version


def ffprobe_check():
    """
    checks that ffprobe exists by running its -version command
    """
    try:
        subprocess.check_output([args.ffprobe_path, "-version"]).decode(
            "ascii"
        ).rstrip().splitlines()[0].split()[2]
    except:
        print("Error locating ffprobe")
        quit()


def mediaconch_policy_exists(policy_path):
    """
    checks that the specified mediaconch policy exists
    """
    if not os.path.isfile(policy_path):
        print("unable to find mediaconch policy:", policy_path)
        print("Check if file exists before running")
        quit()

def input_check():
    """
    Checks if input was provided and if it is a directory that exists
    """
    if args.input_path:
        indir = args.input_path
    else:
        print("No input provided, using current directory as input")
        indir = os.getcwd()

    if not os.path.isdir(indir):
        print("input is not a directory")
        quit()
    return indir


def output_check(indir):
    """
    Checks if output was provided and if it is a directory that exists
    If no output is provided, output folder will default to input
    """
    if args.output_path:
        outdir = args.output_path
    else:
        print("Output not specified. Using input directory as Output directory")
        outdir = indir

    if not os.path.isdir(outdir):
        print("output is not a directory")
        quit()
    return outdir


def check_mixdown_arg():
    mixdown_list = ["copy", "4to3", "4to2", "2to1"]
    # TO DO add swap as an option to allow switching tracks 3&4 with tracks 1&2
    if not args.mixdown in mixdown_list:
        print("The selected audio mixdown is not a valid value")
        print("please use one of: copy, 4to3, 4to2, 2to1")
        quit()
