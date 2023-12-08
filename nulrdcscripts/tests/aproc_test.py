"""
Checks all relevent files in aproc_test by comparing
them to reference files in CORRECT folder.
Run after running aproc on aproc_test.
"""

import subprocess
import os
import shutil
import nulrdcscripts.tests.colors as colors
import nulrdcscripts.tests.helpers as helpers

def main(current_dir: str):

    # setup directory paths
    aproc_test_dir = os.path.join(current_dir, "aproc_test")

    filepath_list = [
        os.path.join(aproc_test_dir, "100Hz", "p", "100Hz_s01_p.wav"),
        os.path.join(aproc_test_dir, "100Hz", "p", "100Hz_s01_p.md5"),
        os.path.join(aproc_test_dir, "100Hz", "p", "100Hz_s02_p.wav"),
        os.path.join(aproc_test_dir, "100Hz", "p", "100Hz_s02_p.md5"),
        os.path.join(aproc_test_dir, "100Hz", "a", "100Hz_s01_a.wav"),
        os.path.join(aproc_test_dir, "100Hz", "a", "100Hz_s01_a.md5"),
        os.path.join(aproc_test_dir, "100Hz", "a", "100Hz_s02_a.wav"),
        os.path.join(aproc_test_dir, "100Hz", "a", "100Hz_s02_a.md5"),
        os.path.join(aproc_test_dir, "100Hz", "meta", "100Hz_s.json"),
        os.path.join(aproc_test_dir, "100Hz", "meta", "100Hz_s01_spectrogram_s.png"),
        os.path.join(aproc_test_dir, "100Hz", "meta", "100Hz_s02_spectrogram_s.png"),
        os.path.join(aproc_test_dir, "500Hz", "p", "500Hz_s01_p.wav"),
        os.path.join(aproc_test_dir, "500Hz", "p", "500Hz_s01_p.md5"),
        os.path.join(aproc_test_dir, "500Hz", "p", "500Hz_s02_p.wav"),
        os.path.join(aproc_test_dir, "500Hz", "p", "500Hz_s02_p.md5"),
        os.path.join(aproc_test_dir, "500Hz", "a", "500Hz_s01_a.wav"),
        os.path.join(aproc_test_dir, "500Hz", "a", "500Hz_s01_a.md5"),
        os.path.join(aproc_test_dir, "500Hz", "a", "500Hz_s02_a.wav"),
        os.path.join(aproc_test_dir, "500Hz", "a", "500Hz_s02_a.md5"),
        os.path.join(aproc_test_dir, "500Hz", "meta", "500Hz_s.json"),
        os.path.join(aproc_test_dir, "500Hz", "meta", "500Hz_s01_spectrogram_s.png"),
        os.path.join(aproc_test_dir, "500Hz", "meta", "500Hz_s02_spectrogram_s.png"),
        os.path.join(aproc_test_dir, "aproc_test-qc_log.csv"),
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
    correct_results_dir = os.path.join(current_dir, "CORRECT")
    if filepath.endswith(".wav"):
        return check_wav(filepath, current_dir)
    if filepath.endswith(".md5"):
        return helpers.check_file(filepath, correct_results_dir)
    elif filepath.endswith(".json"):
        return helpers.check_json(filepath, correct_results_dir)
    elif filepath.endswith("qc_log.csv"): 
        return helpers.check_qc_log(filepath)
    elif filepath.endswith("spectrogram_s.png"):
        return helpers.check_file(filepath, correct_results_dir)
    return False

def check_wav(filepath: str, current_dir: str):
    """
    Runs mediaconch policy on wav file based on a or p.
    md5 check will find errors in actual file contents.

    :param str filepath: path to test wav file
    :param str current_dir: path to 'tests' directory
    :return: result of policy check
    :rtype: bool
    """

    # set the policy path based on p or a
    if filepath.endswith("p.wav"):
        policy_path = os.path.join(current_dir, "policies", "preservation_wav-96k24-tech.xml")
    elif filepath.endswith("a.wav"):
        policy_path = os.path.join(current_dir, "policies", "access_wav-44k16-tech.xml")
    # mediaconch policy check
    return helpers.policy_check(filepath, policy_path)

def reset(current_dir: str):
    """
    Deletes files created by aproc and strips p files of metadata.

    :param str current_dir: path to 'tests' directory
    """

    #list of projects in aproc_test
    projects = ["100Hz", "500Hz"]

    # get directory of aproc_test
    aproc_test_dir = os.path.join(current_dir, "aproc_test")

    print(colors.DELETE)

    # removes these files if they exist
    qclog_path = os.path.join(aproc_test_dir, "aproc_test-qc_log.csv")
    if os.path.isfile(qclog_path):
        print("deleting " + qclog_path)
        os.remove(qclog_path)
    # checks for ingest because why not
    ingest_path = os.path.join(aproc_test_dir, "aproc_test_ingest.csv")
    if os.path.isfile(ingest_path):
        print("deleting " + ingest_path)
        os.remove(ingest_path)

    # for each project
    for project in projects:

        # delete a and meta folders
        folder = os.path.join(aproc_test_dir,project)
        a_folder = os.path.join(folder, "a")
        if os.path.isdir(a_folder):
            print("deleting " + a_folder)
            shutil.rmtree(a_folder)
        meta_folder = os.path.join(folder, "meta")
        if os.path.isdir(meta_folder):
            print("deleting " + meta_folder)
            shutil.rmtree(meta_folder)

        # look through p file to reset
        p_folder = os.path.join(folder, "p")
        for subdir, dirs, files in os.walk(p_folder):
            for file in files:
                filepath: str = os.path.join(subdir, file)

                # delete md5s
                if filepath.endswith(".md5"):
                    print("deleting " + filepath)
                    os.remove(filepath)
                    # remove bwf metadata from p files
                elif filepath.endswith(".wav"):
                    metaeditcommand = ["bwfmetaedit", "--in-core-remove", filepath]
                    print("stripping metadata from " + filepath)
                    subprocess.run(metaeditcommand)

    print(colors.DEFAULT, end="")

if __name__ == "__main__":
	main()