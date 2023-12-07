"""
Checks all relevent files in aproc_test by comparing
them to reference files in CORRECT folder.
Run after running aproc on aproc_test.
"""

import subprocess
import os
import shutil
import json
import nulrdcscripts.tests.helpers as helpers

def main(current_dir):

    # setup directory paths
    correct_results_dir = os.path.join(current_dir, "CORRECT")
    aproc_test_dir = os.path.join(current_dir, "aproc_test")

    # look through every file in aproc_test
    for subdir, dirs, files in os.walk(aproc_test_dir):
        for file in files:
            filepath = os.path.join(subdir, file)

            # for a and p wav files, compare md5s and run mediaconch policy
            # NOTE: the policies in this test do not have a separate bwf metadata policy
            # They are merged into the a and p policies
            if file.endswith(".wav"):
                
                #check md5 checksums
                md5 = file.replace(".wav", ".md5")
                md5_path = os.path.join(subdir, md5)
                if not os.path.isfile(md5_path):
                    print("fail! no md5 file not found for " + file)
                # read in the test md5 and the correct md5
                with open(md5_path, "r") as f:
                    checksum = f.read()
                correct_md5_path = os.path.join(correct_results_dir, md5)
                with open(correct_md5_path, "r") as f:
                    correct_checksum = f.read()
                if not checksum == correct_checksum:
                    print("fail! " + md5_path)
                else:
                    print("pass! " + md5_path)
                
                # set the policy path based on p or a
                if file.endswith("p.wav"):
                    policy_path = os.path.join(current_dir, "policies", "preservation_wav-96k24-tech.xml")
                elif file.endswith("a.wav"):
                    policy_path = os.path.join(current_dir, "policies", "access_wav-44k16-tech.xml")
                # mediaconch policy check
                mediaconch_command = ["mediaconch", filepath, "--policy="+policy_path]
                subprocess.run(mediaconch_command)

            # open both json files and check if data matches
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

            # check qc_log for PASS or FAIL results
            elif file.endswith("qc_log.csv"): 
                if not helpers.qc_log_test(filepath):
                    # qc_log_test() will print out all failures so this
                    # little print makes it clear what file it corresponds to
                    print("     in " + file)
                else:
                    print("pass! " + filepath)

            # check spectrograms
            elif file.endswith("spectrogram_s.png"):
                correct_png_path = os.path.join(correct_results_dir, file)
                if helpers.brute_force_file_compare(filepath, correct_png_path):
                    print("pass! " + filepath)
                else:
                    print("fail! " + filepath)

    # prompt user to reset
    print("Reset? (y/n)")
    answer = input()
    if answer.lower() == "y":
        reset(current_dir)


def reset(current_dir):
    """
    Deletes files created by aproc and strips p files of metadata
    """

    #list of projects in aproc_test
    projects = ["100Hz", "500Hz"]

    # get directory of aproc_test
    aproc_test_dir = os.path.join(current_dir, "aproc_test")

    # removes these files if they exist
    qclog_path = os.path.join(aproc_test_dir, "aproc_test-qc_log.csv")
    if os.path.isfile(qclog_path):
        os.remove(qclog_path)
    # checks for ingest because why not
    ingest_path = os.path.join(aproc_test_dir, "aproc_test_ingest.csv")
    if os.path.isfile(ingest_path):
        os.remove(ingest_path)

    # for each project
    for project in projects:

        # delete a and meta folders
        folder = os.path.join(aproc_test_dir,project)
        a_folder = os.path.join(folder, "a")
        if os.path.isdir(a_folder):
            shutil.rmtree(a_folder)
        meta_folder = os.path.join(folder, "meta")
        if os.path.isdir(meta_folder):
            shutil.rmtree(meta_folder)

        # look through p file to reset
        p_folder = os.path.join(folder, "p")
        for subdir, dirs, files in os.walk(p_folder):
            for file in files:
                filepath: str = os.path.join(subdir, file)

                # delete md5s
                if filepath.endswith(".md5"):
                    os.remove(filepath)
                    # remove bwf metadata from p files
                elif filepath.endswith(".wav"):
                    metaeditcommand = ["bwfmetaedit", "--in-core-remove", filepath]
                    subprocess.run(metaeditcommand)
            

if __name__ == "__main__":
	main()