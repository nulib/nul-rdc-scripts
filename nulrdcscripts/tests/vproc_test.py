"""
Checks all relevent files in vproc_test by comparing
them to reference files in CORRECT folder.
Run after running vproc on vproc_test.
"""

import os
import shutil
import subprocess
import json
import nulrdcscripts.tests.helpers as helpers

def main(current_dir):
	
    # setup directories
    correct_results_dir = os.path.join(current_dir, "CORRECT")
    aproc_test_dir = os.path.join(current_dir, "vproc_test")

    # look through every file in vproc_test
    for subdir, dirs, files in os.walk(aproc_test_dir):
        for file in files:
            filepath = os.path.join(subdir, file)

            # for p files, check policy
            # don't check md5s as it ends up being different
            # since they will have different metadata
            # this is only the case for video p files
            if file.endswith("p.mkv"):
                policy_path = os.path.join(current_dir, "policies", "AJA_NTSC_VHS-2SAS-MKV.xml")
                mediaconch_command = ["mediaconch", filepath, "--policy=" + policy_path]
                subprocess.run(mediaconch_command)

            # for a files, compare md5 checksums
            elif file.endswith("a.mp4"):
                md5 = file.replace(".mp4", ".md5")
                md5_path = os.path.join(subdir, md5)
                # skip checking md5 if it doesn't exist
                if not os.path.isfile(md5_path):
                    print("fail! md5 file not found for " + file)
                    continue
                # read in the test md5 and the correct md5
                with open(md5_path, "r") as f:
                    checksum = f.read()
                correct_md5_path = os.path.join(correct_results_dir, md5)
                with open(correct_md5_path, "r") as f:
                    correct_checksum = f.read()
                # check for equality
                if not checksum == correct_checksum:
                    print("fail! " + filepath)
                else:
                    print("pass! " + filepath)

            # compare contents of .framemd5 for p file
            # this md5 checksum is not different since it is
            # independant of encoding date metadata
            elif file.endswith(".framemd5"):
                correct_framemd5 = os.path.join(correct_results_dir, file)
                with open(filepath) as f1, open(correct_framemd5) as f2:
                    contents1 = f1.read()
                    contents2 = f2.read()
                    if not contents1 == contents2:
                        print("fail! " + filepath)
                    else:
                        print("pass! " + filepath)

            # read in json data and check for equality
            # not including system info, encoding date, and md5
            # NOTE: stream md5s are still checked
            elif file.endswith(".json"):
                correct_json_path = os.path.join(correct_results_dir, file)
                with open(filepath) as json_file, open(correct_json_path) as correct_json_file:
                    json_data = json.load(json_file)
                    correct_json_data = json.load(correct_json_file)
                    if not helpers.json_test(json_data, correct_json_data):
                        # json_test() will print out all failures so this
                        # little print makes it clear what file it corresponds to
                        print("     in " + file)
                    else:
                        print("pass! " + filepath)

            # checks qc_log csv
            elif file.endswith("qc_log.csv"):
                if not helpers.qc_log_test(filepath):
                    # qc_log_test() will print out all failures so this
                    # little print makes it clear what file it corresponds to
                    print("     in " + file)
                else:
                    print("pass! " + filepath)

            # directly compare the spectrogram images
            # kind of brute force but it works and doesn't take long
            elif file.endswith("spectrogram_00.png") or file.endswith("spectrogram_01.png"):
                correct_png_path = os.path.join(correct_results_dir, file)
                if helpers.brute_force_file_compare(filepath, correct_png_path):
                    print("fail! " + filepath)
                else:
                    print("pass! " + filepath)

            # just check if qc tools file exists, too much to check for exact match
            elif file.endswith("p.mkv.qctools.mkv"):
                print("pass! " + filepath)

    # prompt user to reset
    print("Reset? (y/n)")
    answer = input()
    if answer.lower() == "y":
        reset(current_dir)

def reset(current_dir):
    """
    Deletes files created by aproc and strips p files of metadata
    """
    
    # list of projects in vproc
    projects = ["bars1min", "bars5min"]
    
    # get directory of vproc_test
    vproc_test_dir = os.path.join(current_dir, "vproc_test")
    # removes ingest if present because why not
    ingest_path = os.path.join(vproc_test_dir, "vproc_test_ingest.csv")
    if os.path.isfile(ingest_path):
            os.remove(ingest_path)

    # for each project
    for project in projects:
        item_path = os.path.join(vproc_test_dir, project)
        project_path = os.path.join(item_path, project)
        # deletes the entire containing folder for the project
        if os.path.isdir(project_path):
            shutil.rmtree(project_path)
        # also removes qc_log bye bye
        item_qclog_path = os.path.join(item_path, "qc_log.csv")
        if os.path.isfile(item_qclog_path):
            os.remove(item_qclog_path)
            

if __name__ == "__main__":
	main()