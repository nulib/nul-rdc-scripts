"""
Checks all relevent files in vproc_test by comparing
them to reference files in CORRECT folder.
Run after running vproc on vproc_test.
"""

import os
import shutil
import nulrdcscripts.tests.colors as colors
import nulrdcscripts.tests.helpers as helpers

def main(current_dir: str):
	
    # setup directories
    vproc_test_dir: str = os.path.join(current_dir, "vproc_test")

    filepath_list = [
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "a", "bars1min_a.md5"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "a", "bars1min_a.mp4"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "meta", "bars1min_s.json"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "meta", "bars1min_spectrogram00_s.png"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "meta", "bars1min_spectrogram01_s.png"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "p", "bars1min_p.framemd5"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "p", "bars1min_p.md5"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "p", "bars1min_p.mkv"),
        os.path.join(vproc_test_dir, "bars1min", "bars1min", "p", "bars1min_p.mkv.qctools.mkv"),
        os.path.join(vproc_test_dir, "bars1min", "qc_log.csv"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "a", "bars5min_a.md5"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "a", "bars5min_a.mp4"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "meta", "bars5min_s.json"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "meta", "bars5min_spectrogram00_s.png"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "meta", "bars5min_spectrogram01_s.png"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "p", "bars5min_p.framemd5"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "p", "bars5min_p.md5"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "p", "bars5min_p.mkv"),
        os.path.join(vproc_test_dir, "bars5min", "bars5min", "p", "bars5min_p.mkv.qctools.mkv"),
        os.path.join(vproc_test_dir, "bars5min", "qc_log.csv"),
    ]

    total_result: bool = True
    # look through every file
    for filepath in filepath_list:
        print(os.path.basename(filepath) + "...", end = "")
        # check it exists
        # if it does, check the file
        if os.path.isfile(filepath):
            # this multiplication will make total_result false if any files fail
            total_result = check(filepath, current_dir) * total_result
        else:
            total_result = False
            print(colors.FAIL + "fail! file not found" + colors.DEFAULT)

    if total_result:
        print(colors.PASS + "\nALL PASS!" + colors.DEFAULT)

    # prompt user to reset
    print("\nreset? (y/n): ", end="")
    answer = input()
    if answer.lower() == "y":
        reset(current_dir)

def check(filepath: str, current_dir: str):
    """
    Performs a check on a file based on its type.

    :param str filepath: path to test file
    :param str current_dir: path to 'tests' directory
    :return: result of the file check
    :rtype: bool
    """
    correct_results_dir: str = os.path.join(current_dir, "CORRECT")
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

    elif filepath.endswith(".framemd5"):
        return helpers.check_file(filepath, correct_results_dir)

    elif filepath.endswith(".json"):
        return helpers.check_json(filepath, correct_results_dir)

    elif filepath.endswith("qc_log.csv"):
        return helpers.check_qc_log(filepath)
    
    elif filepath.endswith("spectrogram00_s.png") or filepath.endswith("spectrogram01_s.png"):
        return helpers.check_file(filepath, correct_results_dir)

    elif filepath.endswith("p.mkv.qctools.mkv"):
        print(colors.PASS + "pass!" + colors.DEFAULT)
        return True

    # should not get here, just need a base case
    print(colors.FAIL + "fail! what is this file?" + colors.DEFAULT)
    return False

def check_mkv(filepath: str, current_dir: str):
    """
    Performs check on mkv file.

    :param str filepath: path to test file
    :param str current_dir: path to 'tests' directory
    :return: result of test
    :rtype: bool
    """
    # runs mediaconch policy check and grabs 1st word of its output
    policy_path: str = os.path.join(current_dir, "policies", "AJA_NTSC_VHS-2SAS-MKV.xml")
    return helpers.policy_check(filepath, policy_path)

def reset(current_dir: str):
    """
    Deletes files created by aproc and strips p files of metadata.

    :param str current_dir: path to 'tests' directory
    """
    # list of projects in vproc
    projects: list[str] = ["bars1min", "bars5min"]
    
    print(colors.DELETE)

    # get directory of vproc_test
    vproc_test_dir: str = os.path.join(current_dir, "vproc_test")
    # removes ingest if present because why not
    ingest_path: str = os.path.join(vproc_test_dir, "vproc_test_ingest.csv")
    if os.path.isfile(ingest_path):
        print("deleting " + ingest_path)
        os.remove(ingest_path)

    # for each project
    for project in projects:
        item_path: str = os.path.join(vproc_test_dir, project)
        project_path: str = os.path.join(item_path, project)
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