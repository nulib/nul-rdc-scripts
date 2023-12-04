#!/usr/bin/env python3

"""
General helper functions for Ingest_Sheet_Maker
"""

import os
import posixpath
import csv

def init_io(input_path: str, output_path: str):
    """
    Sets up input directory and output csv file.
    If no input path is provided, current working directory is used.
    If no output is provided, input is used.

    :param str input_path: fullpath to input directory
    :param str output_path: fullpath to output file
    :returns: fullpath to valid input directory and valid output directory
    :rtype: tuple
    """
    if not (input_path):
        print("No input provided, using current directory")
        input_path = os.getcwd()
    input_check(input_path)

    if not output_path:
        base_folder_name = os.path.basename(input_path)
        output_path = os.path.join(
            input_path, 
            base_folder_name + '_ingest.csv'
        )
    output_check(output_path)

    return input_path, output_path

def input_check(indir: str):
    """
    Checks given input is valid. Quits if not.
    
    :param str indir: fullpath to input directory to be checked
    """
    if not os.path.isdir(indir):
        print("\n--- ERROR: Input must be a directory ---\n")
        quit()

def output_check(outfile: str):
    """
    Checks that output is a valid csv file. Quits if not.

    :param str outfile: fullpath to output file to be checked
    """
    if not outfile.endswith(".csv"):
        print("\n--- ERROR: Output must be a CSV file ---\n")
        quit()
    try:
        with open(outfile, "w", newline="\n") as f:
            f.close
    except OSError:
        print("\n--- ERROR: Unable to create output file", outfile + " ---\n")
        quit()

def write_csv(outfile: str, csv_fields: list[str], csv_data: list[dict[str, str]]):
    """
    Writes ingest sheet data to a csv.
    
    :param str outfile: fullpath to output file including extension
    :param list csv_fields: fieldnames(headers) for csv file
    :param list csv_data: data to be written to csv
    """
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for item in csv_data:
            for file_info in csv_data[item]:
                writer.writerow(file_info)

def clean_subdir(subdir: str, indir: str):
    """
    Cleans up subdir to easier use in analyzing file.
    Kind of niche function but it made the class look prettier.

    :param str subdir: fullpath to subdirectory
    :param str indir: fullpath to input directory
    """
    subdir = subdir.replace(indir, "")
    subdir = subdir.strip("/")
    return subdir

def clean_dirs(dirs: list[str]):
    """
    Reorganized dirs.
    Not sure why this exists but it was done in the original script.

    :param list dirs: contains list of directories
    :returns dirs: sorted directories
    :rtype: list of str
    """
    dirs.sort()
    dirs[:] = [d for d in dirs if not d[0] == "."]
    return dirs

def clean_files(files: list[str], skip: list[str]):
    """
    Removes files to be ignored when making ingest sheet.
    By default skips ".", "Thumbs.db", ".md5", ".csv", ".py"
    
    :param list files: list of files in a directory
    :param list skip: list of files to skip in addition defaults
    :returns: cleaned and sorted list of files
    :rtype: list of str
    """
    files = [f for f in files if not f[0] == "."]
    files = [f for f in files if not f == "Thumbs.db"]
    files = [f for f in files if not f.endswith(".md5")]
    files = [f for f in files if not f.endswith(".csv")]
    files = [f for f in files if not f.endswith(".py")]

    if skip:
        skip_list = skip
        for i in skip_list:
            files = [f for f in files if not i in f]
    sorted_files: list[str] = sorted(files)
    return sorted_files

def get_unix_fullpath(file: str, subdir: str):
    """
    Creates fullpath filename for file.
    Uses unix style path without leading slash.
    
    :param str file: input filename
    :param str subdir: fullpath to directory that file is in
    :returns: unix style path for file
    :rtype: str
    """
    filename: str = os.path.join(subdir, file)
    filename = filename.replace(os.sep, posixpath.sep)
    filename = filename.strip("/")
    return filename

def yn_check(message = ""):
    """
    Gets yes or no response from user.

    :param str message: optional string to be added to prompt
    :returns: True or False based on user input
    :rtype: bool
    """
    print(message + " (y/n)")
    yes = {"yes", "y", "ye", ""}
    no = {"no", "n"}
    while True:
        choice = input().lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'")

if __name__ == "__main__":
    import doctest

    doctest.testmod()