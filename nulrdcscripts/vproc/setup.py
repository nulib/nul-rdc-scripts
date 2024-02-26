import datetime
import os
import subprocess
import time
from nulrdcscripts.vproc.params import args


def create_transcode_output_folders(baseOutput, outputFolderList):
    if not os.path.isdir(baseOutput):
        try:
            os.mkdir(baseOutput)
        except:
            print("unable to create output folder:", baseOutput)
            quit()
    else:
        print(baseOutput, "already exists")
        print("Proceeding")

    for folder in outputFolderList:
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except:
                print("unable to create output folder:", folder)
                quit()
        else:
            print("using existing folder", folder, "as output")


def mediaconch_policy_check(input, policy):
    mediaconchResults = (
        subprocess.check_output([args.mediaconch_path, "--policy=" + policy, input])
        .decode("ascii")
        .rstrip()
        .split()[0]
    )
    if mediaconchResults == "pass!":
        mediaconchResults = "PASS"
    else:
        mediaconchResults = "FAIL"
    return mediaconchResults


def guess_date(string):
    for fmt in ["%m/%d/%Y", "%d-%m-%Y", "%m/%d/%y", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            continue
    raise ValueError(string)


def check_mixdown_arg():
    mixdown_list = ["copy", "4to3", "4to2", "2to1"]
    # TO DO add swap as an option to allow switching tracks 3&4 with tracks 1&2
    if not args.mixdown in mixdown_list:
        print("The selected audio mixdown is not a valid value")
        print("please use one of: copy, 4to3, 4to2, 2to1")
        quit()


def convert_runtime(duration):
    runtime = time.strftime("%H:%M:%S", time.gmtime(float(duration)))
    return runtime
