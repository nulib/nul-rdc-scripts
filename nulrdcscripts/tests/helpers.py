"""
Contains helpers for the test scripts.
"""

import csv

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
    result = True
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

def qc_log_test(filepath):
    """
    Checks results in qc_log to make sure everything passed.

    :param str filepath: path to qc_log
    :return: result of test
    :rtype: bool
    """
    result = True
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
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
    return result

def brute_force_file_compare(filepath1, filepath2):
    """
    Directly compares binary data in 2 files.

    :param str filepath1: fullpath to first file
    :param str filepath2: fullpath to second file
    :return: whether the 2 files match
    :rtype: bool
    """
    with open(filepath1, 'rb') as f1, open(filepath2, 'rb') as f2:
        contents1 = f1.read()
        contents2 = f2.read()
        return contents1 == contents2