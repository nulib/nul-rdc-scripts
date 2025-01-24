#!/usr/bin/env python3

"""
Functions that will be in multiple scripts
Handle things like: 
input, output, checksumming, checking that software exists, etc.
"""

import os
import hashlib
import sys
import subprocess
from nulrdcscripts.vproc.params import args


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


def mediaconch_policy_exists(policy_path):
    """
    checks that the specified mediaconch policy exists
    """
    if not os.path.isfile(policy_path):
        print("unable to find mediaconch policy:", policy_path)
        print("Check if file exists before running")
        quit()


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
