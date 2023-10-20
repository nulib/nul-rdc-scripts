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
from nulrdcscripts.aproc.params import args


def input_check():
    """
    Checks if input was provided and if it is a directory that exists
    """
    if args.input_path:
        indir = args.input_path
    else:
        print("No input provided, using current working directory")
        indir = os.getcwd()

    if not os.path.isdir(indir):
        print("input is not a directory")
        quit()
    return indir


def output_check(output):
    """Checks that output is valid"""
    if not output.endswith(".csv"):
        print("\n--- ERROR: Output must be a CSV file ---\n")
        quit()
    # TODO add check if csv will go in a valid directory


def hashlib_md5(filename):
    """
    Uses hashlib to return an MD5 checksum of an input filename
    Credit: IFI scripts
    """
    read_size = 0
    last_percent_done = 0
    chksm = hashlib.md5()
    total_size = os.path.getsize(filename)
    with open(filename, "rb") as f:
        while True:
            # 2**20 is for reading the file in 1 MiB chunks
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            chksm.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write("[%d%%]\r" % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    md5_output = chksm.hexdigest()
    return md5_output


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
        )
        if not "--enable-libsoxr" in ffmpeg_version:
            print("WARNING: ffmpeg is not configured with libsoxr. Exiting")
            quit()
        else:
            ffmpeg_version = ffmpeg_version.splitlines()[0].split()[2]
    except:
        print("Error getting ffmpeg version")
        quit()
    return ffmpeg_version


def get_bwf_metaedit_version():
    """
    Returns the version of BWF Metaedit by running the --Version command
    """
    metaedit_version = "bwf metaedit"
    try:
        metaedit_version = (
            subprocess.check_output([args.metaedit_path, "--Version"])
            .decode("ascii")
            .rstrip()
            .splitlines()[0]
            .split()[2]
        )
    except:
        print("Error getting BWF Metaedit version")
        quit()
    return metaedit_version


def get_sox_version():
    """
    Returns the version of sox
    """
    try:
        sox_version = (
            subprocess.check_output([args.sox_path, "--version"])
            .decode("ascii")
            .rstrip()
            .splitlines()[0]
            .split()
        )  # [2]
        sox_version = "".join([i for i in sox_version if i.startswith("v")])
    except:
        print("Error getting sox version")
        quit()
    return sox_version
