"""
Checks all relevent files in aproc_test by comparing
them to reference files in CORRECT folder.
Run after running aproc on aproc_test.
"""

import subprocess
import os
import shutil
import json
import nulrdcscripts.tests.colors as colors
import nulrdcscripts.tests.helpers as helpers

def main(current_dir):

    # setup directory paths
    correct_results_dir = os.path.join(current_dir, "CORRECT")
    aproc_test_dir = os.path.join(current_dir, "aproc_test")

    result = True

    aproc_dir = os.path.join(current_dir, "aproc_test")
    filepath_list = [
        os.path.join(aproc_dir, "100Hz", "p", "100Hz_s01_p.wav"),
        os.path.join(aproc_dir, "100Hz", "p", "100Hz_s01_p.md5"),
        os.path.join(aproc_dir, "100Hz", "p", "100Hz_s02_p.wav"),
        os.path.join(aproc_dir, "100Hz", "p", "100Hz_s02_p.md5"),
        os.path.join(aproc_dir, "100Hz", "a", "100Hz_s01_a.wav"),
        os.path.join(aproc_dir, "100Hz", "a", "100Hz_s01_a.md5"),
        os.path.join(aproc_dir, "100Hz", "a", "100Hz_s02_a.wav"),
        os.path.join(aproc_dir, "100Hz", "a", "100Hz_s02_a.md5"),
        os.path.join(aproc_dir, "100Hz", "meta", "100Hz_s.json"),
        os.path.join(aproc_dir, "100Hz", "meta", "100Hz_s01_spectrogram_s.png"),
        os.path.join(aproc_dir, "100Hz", "meta", "100Hz_s02_spectrogram_s.png"),
        os.path.join(aproc_dir, "500Hz", "p", "500Hz_s01_p.wav"),
        os.path.join(aproc_dir, "500Hz", "p", "500Hz_s01_p.md5"),
        os.path.join(aproc_dir, "500Hz", "p", "500Hz_s02_p.wav"),
        os.path.join(aproc_dir, "500Hz", "p", "500Hz_s02_p.md5"),
        os.path.join(aproc_dir, "500Hz", "a", "500Hz_s01_a.wav"),
        os.path.join(aproc_dir, "500Hz", "a", "500Hz_s01_a.md5"),
        os.path.join(aproc_dir, "500Hz", "a", "500Hz_s02_a.wav"),
        os.path.join(aproc_dir, "500Hz", "a", "500Hz_s02_a.md5"),
        os.path.join(aproc_dir, "500Hz", "meta", "500Hz_s.json"),
        os.path.join(aproc_dir, "500Hz", "meta", "500Hz_s01_spectrogram_s.png"),
        os.path.join(aproc_dir, "500Hz", "meta", "500Hz_s02_spectrogram_s.png"),
        os.path.join(aproc_dir, "aproc_test-qc_log.csv"),
    ]
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
    if filepath.endswith(".wav"):
        return check_wav(filepath, current_dir, correct_results_dir)
    if filepath.endswith(".md5"):
        return helpers.check_file(filepath, correct_results_dir)
    # open both json files and check if data matches
    elif filepath.endswith(".json"):
        return helpers.check_json(filepath, correct_results_dir)
    # check qc_log for PASS or FAIL results
    elif filepath.endswith("qc_log.csv"): 
        return helpers.check_qc_log(filepath)
    # check spectrograms
    elif filepath.endswith("spectrogram_s.png"):
        return helpers.check_file(filepath, correct_results_dir)
    return False

def check_wav(filepath, current_dir, correct_results_dir):
    file = os.path.basename(filepath)
    
    # set the policy path based on p or a
    if file.endswith("p.wav"):
        policy_path = os.path.join(current_dir, "policies", "preservation_wav-96k24-tech.xml")
    elif file.endswith("a.wav"):
        policy_path = os.path.join(current_dir, "policies", "access_wav-44k16-tech.xml")
    # mediaconch policy check
    mediaconch_command = ["mediaconch", filepath, "--policy="+policy_path]
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