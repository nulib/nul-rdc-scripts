"""
Checks all relevent files in vproc_test by comparing
them to reference files in CORRECT folder.
Run after running vproc on vproc_test.
"""

import os
import shutil
import subprocess
import nulrdcscripts.tests.colors as colors
import nulrdcscripts.tests.helpers as helpers

def main(current_dir):
	
    # setup directories
    correct_results_dir = os.path.join(current_dir, "CORRECT")
    aproc_test_dir = os.path.join(current_dir, "vproc_test")

    result = True

    not_skip = (
        "p.mkv", 
        "a.mp4", 
        ".json", 
        ".framemd5", 
        "qc_log.csv", 
        "p.mkv.qctools.mkv", 
        "spectrogram_00.png", 
        "spectrogram_01.png"
    )

    vproc_dir = os.path.join(current_dir, "vproc_test")
    filepath_list = [
        os.path.join(vproc_dir, "bars1min", "bars1min", "a", "bars1min_a.md5"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "a", "bars1min_a.mp4"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "meta", "bars1min_s.json"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "meta", "bars1min_spectrogram00_s.png"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "meta", "bars1min_spectrogram01_s.png"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "p", "bars1min_p.framemd5"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "p", "bars1min_p.md5"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "p", "bars1min_p.mkv"),
        os.path.join(vproc_dir, "bars1min", "bars1min", "p", "bars1min_p.mkv.qctools.mkv"),
        os.path.join(vproc_dir, "bars1min", "qc_log.csv"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "a", "bars5min_a.md5"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "a", "bars5min_a.mp4"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "meta", "bars5min_s.json"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "meta", "bars5min_spectrogram00_s.png"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "meta", "bars5min_spectrogram01_s.png"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "p", "bars5min_p.framemd5"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "p", "bars5min_p.md5"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "p", "bars5min_p.mkv"),
        os.path.join(vproc_dir, "bars5min", "bars5min", "p", "bars5min_p.mkv.qctools.mkv"),
        os.path.join(vproc_dir, "bars5min", "qc_log.csv"),
    ]

    # look through every file in vproc_test
    for filepath in filepath_list:
        print(os.path.basename(filepath) + "...", end = "")
        if os.path.isfile(filepath):
            result = check(filepath, current_dir, correct_results_dir) * result
        else:
            result = False
            print(colors.FAIL + "fail! file not found" + colors.DEFAULT)

    if result:
        print(colors.PASS + "\nALL PASS!" + colors.DEFAULT)

    # prompt user to reset
    print("\nreset? (y/n): ", end="")
    answer = input()
    if answer.lower() == "y":
        reset(current_dir)

def check(filepath, current_dir, correct_results_dir):
    # for p files, check policy
    # don't check md5s as it ends up being different
    # since they will have different metadata
    # this is only the case for video p files
    if filepath.endswith("p.mkv"):
        return check_mkv(filepath, current_dir)

    if filepath.endswith("p.md5"):
        print(colors.PASS + "pass!" + colors.DEFAULT)
        return True

    if filepath.endswith("a.md5"):
        return helpers.check_file(filepath, correct_results_dir)

    elif filepath.endswith("a.mp4"):
        print(colors.PASS + "pass!" + colors.DEFAULT)
        return True

    # compare contents of .framemd5 for p file
    # this md5 checksum is not different since it is
    # independant of encoding date metadata
    elif filepath.endswith(".framemd5"):
        return helpers.check_file(filepath, correct_results_dir)

    # read in json data and check for equality
    # not including system info, encoding date, and md5
    # NOTE: stream md5s are still checked
    elif filepath.endswith(".json"):
        return helpers.check_json(filepath, correct_results_dir)
    
    # checks qc_log csv
    elif filepath.endswith("qc_log.csv"):
        return helpers.check_qc_log(filepath)

    # directly compare the spectrogram images
    elif filepath.endswith("spectrogram00_s.png") or filepath.endswith("spectrogram01_s.png"):
        return helpers.check_file(filepath, correct_results_dir)

    # just check if qc tools file exists, too much to check for exact match
    elif filepath.endswith("p.mkv.qctools.mkv"):
        print(colors.PASS + "pass!" + colors.DEFAULT)
        return True

    return False

def check_mkv(filepath, current_dir):
    policy_path = os.path.join(current_dir, "policies", "AJA_NTSC_VHS-2SAS-MKV.xml")
    mediaconch_command = ["mediaconch", filepath, "--policy=" + policy_path]
    output = subprocess.check_output(mediaconch_command)
    parsed_output = output.decode("ascii").rstrip().split()[0]
    if not parsed_output == "pass!":
        print(colors.FAIL + "fail! ", end="")
        print(*output, sep=", ")
        print(colors.DEFAULT, end="")
        return False
    else:
        print(colors.PASS + "pass!" + colors.DEFAULT)
        return True

def reset(current_dir):
    """
    Deletes files created by aproc and strips p files of metadata
    """
    
    # list of projects in vproc
    projects = ["bars1min", "bars5min"]
    
    print(colors.DELETE)

    # get directory of vproc_test
    vproc_test_dir = os.path.join(current_dir, "vproc_test")
    # removes ingest if present because why not
    ingest_path = os.path.join(vproc_test_dir, "vproc_test_ingest.csv")
    if os.path.isfile(ingest_path):
        print("deleting " + ingest_path)
        os.remove(ingest_path)

    # for each project
    for project in projects:
        item_path = os.path.join(vproc_test_dir, project)
        project_path = os.path.join(item_path, project)
        # deletes the entire containing folder for the project
        if os.path.isdir(project_path):
            print("deleting " + project_path)
            shutil.rmtree(project_path)
        # also removes qc_log bye bye
        item_qclog_path = os.path.join(item_path, "qc_log.csv")
        if os.path.isfile(item_qclog_path):
            print("deleting " + item_qclog_path)
            os.remove(item_qclog_path)
    print(colors.DEFAULT, end="")

if __name__ == "__main__":
	main()