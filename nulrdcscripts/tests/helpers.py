"""
Contains helpers for the test scripts.
"""

import os
import csv
import json
import subprocess
import nulrdcscripts.tests.colors as colors

def check_json(filepath: str, correct_results_dir: str):
    """
    Performs check on json file.

    :param str filepath: path to test file
    :param str correct_results_dir: path to 'CORRECT' directory
    :return: result of check
    :rtype: bool
    """
    file: str = os.path.basename(filepath)
    correct_json_path: str = os.path.join(correct_results_dir, file)
    result: bool = True
    with open(filepath) as json_file, open(correct_json_path) as correct_json_file:
        json_data = json.load(json_file)
        correct_json_data = json.load(correct_json_file)
        if not json_test(json_data, correct_json_data):
            print(colors.DEFAULT)
            result = False
        else:
            print(colors.DEFAULT + "\r" + file + "...", end="")
            print(colors.PASS + "pass!" + colors.DEFAULT)
    return result

def json_test(json_data, correct_json_data, key=""):
    """
    Recursively looks through json file and prints any fields
    that don't match. It has to be ugly like this since the
    json file contains a bunch of nested lists and dicts.

    :param json_data: result from json.load() on the test file
    :param correct_json_data: result from json.load() on the correct file
    :param key: Don't use on external function call. Defaults to "".
    :returns: if the json files match
    :rtype: bool
    """
    result: bool = True
    # get json_data type
    data_type = type(json_data)
    # if its a list, go through each item
    # and run json_test on it.
    if data_type is list:
        for index, item in enumerate(json_data):
            # result of json_test is combined with current result
            result = json_test(item, correct_json_data[index], key) and result
        # return the result after all items of the list have been checked
        return result
    # if its a list, go through each value 
    # and run json_test on it.
    elif data_type is dict:
        # NOTE: this is the only place key is overwritten.
        # this way each recursive call knows what key it
        # applies to.
        for key, value in json_data.items():
            if not ("md5 checksum" in key or "system information" in key):
                # result of json_test is combined with current result
                result = json_test(value, correct_json_data[key], key) and result
    # if its a str or int, just check for equality
    else:
        result = json_data == correct_json_data
        # use the key param to print message
        # this is why key has to be passed when running json_data on a dict
        if not result:
            print("fail! " + key, end="")
    return result

def check_qc_log(filepath: str):
    """
    Checks results in qc_log to make sure everything passed.

    :param str filepath: path to qc_log
    :return: result of test
    :rtype: bool
    """
    result = True
    with open(filepath, encoding="utf-8") as f:
        reader: dict[str, str] = csv.DictReader(f, delimiter=",")
        for row in reader:
            # filename is only a key for audio qc_logs
            if "filename" in row:
                filename = row["filename"]
            # PM filename is a key for video qc_logs
            else:
                filename = row["PM filename"]
            # check shot sheet check results
            if not row["shot sheet check"] == "PASS":
                result = False
                print("fail! " + filename + " " + "shot sheet check")
            # check file format and metadata results
            if not row["file format & metadata verification"] == "PASS":
                result = False
                print("fail! " + filename + " " + "file format & metadata verification")
            # check lossless results if its there (video)
            if "PM lossless transcoding" in row:
                if not row["PM lossless transcoding"] == "PASS":
                    result = False
                    print("fail! " + filename + " " + "PM lossless transcoding")
    if not result:
        print(colors.FAIL + "     in " + os.path.basename(filepath))
    else:
        print(colors.PASS + "pass!" + colors.DEFAULT)
    return result

def policy_check(filepath: str, policy_path: str):
    """
    Checks file against mediaconch policy.

    :param str filepath: path to test file
    :param str policy_path: path to mediaconch policy
    :return: result of policy check
    :rtype: bool
    """

    # grabs first word in mediaconch output
    mediaconch_command: list[str] = ["mediaconch", filepath, "--policy="+policy_path]
    output = subprocess.check_output(mediaconch_command)
    parsed_output = output.decode("ascii").rstrip().split()[0]
    # prints fails on one line 
    if not parsed_output == "pass!":
        print(colors.FAIL + "fail! ", end="")
        print(*output, sep=", ")
        print(colors.DEFAULT, end="")
        return False
    else:
        print(colors.PASS + "pass!" + colors.DEFAULT)
        return True

def check_file(filepath: str, correct_results_dir: str):
    """
    Directly compares binary data in 2 files.

    :param str filepath1: fullpath to first file
    :param str filepath2: fullpath to second file
    :return: whether the 2 files match
    :rtype: bool
    """
    correct_png_path = os.path.join(correct_results_dir, os.path.basename(filepath))
    with open(filepath, 'rb') as f1, open(correct_png_path, 'rb') as f2:
        contents = f1.read()
        correct_contents = f2.read()
        result = contents == correct_contents
    
    if result:
        print(colors.PASS + "pass!" + colors.DEFAULT)
        return True
    else:
        print(colors.FAIL + "fail! " + colors.DEFAULT)
        return False
