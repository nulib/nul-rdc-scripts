#!/usr/bin/env python3

import os
import posixpath
import csv

def init_io(input_path, output_path):
    """
    Sets up input directory and output csv file
    If no input path is provided, current working directory is used
    If no output is provided, input is used
        Parameters:
            input_path(string): fullpath to input directory
            output_path(string): fullpath to output file
        Returns:
            input_path(string): fullpath to valid input directory
            output_path(string): fullpath to valid output directory
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

def input_check(indir):
    """
    Checks given input is valid. Quits if not.
        Parameters:
            indir(string): fullpath to input directory to be checked
    """
    if not os.path.isdir(indir):
        print("\n--- ERROR: Input must be a directory ---\n")
        quit()

def output_check(outfile):
    """
    Checks that output is a valid csv file. Quits if not.
        Parameters:
            outfile(string): fullpath to output file to be checked
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

def write_csv(outfile, csv_fields, csv_data):
    """
    Writes ingest sheet data to a csv
        Parameters:
            outfile(string): fullpath to output file including extension
            csv_fields: list of fieldnames(headers) for csv file
            csv_data(dict): contains data to be written to csv
    """
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for item in csv_data:
            for file_info in csv_data[item]:
                writer.writerow(file_info)

def clean_subdir(subdir, indir):
    """
    Cleans up subdir to easier use in analyzing file.
    Kind of niche function but it made the class look prettier.
        Parameters:
            subdir(string): fullpath to subdirectory
            indir(string): fullpath to input directory
    """
    subdir = subdir.replace(indir, "")
    subdir = subdir.strip("/")
    return subdir

def clean_dirs(dirs):
    """
    Reorganized dirs
    Not sure why this exists but it was done in the original script.
        Parameters:
            dirs(list): contains list of directories
        Returns:
            dirs(list): sorted directories
    """
    dirs.sort()
    dirs[:] = [d for d in dirs if not d[0] == "."]
    return dirs

def clean_files(files, skip):
    """
    Removes files to be ignored when making ingest sheet
    By default skips ".", "Thumbs.db", ".md5", ".csv"
        Parameters:
            files(list): list of files in a directory
            skip(list): list of files to skip in addition defaults
        Returns:
            files(list): sorted list of files
    """
    files = [f for f in files if not f[0] == "."]
    files = [f for f in files if not f == "Thumbs.db"]
    files = [f for f in files if not f.endswith(".md5")]
    files = [f for f in files if not f.endswith(".csv")]

    if skip:
        skip_list = skip
        for i in skip_list:
            files = [f for f in files if not i in f]
    return sorted(files)

def get_unix_fullpath(file, subdir):
    """
    Creates fullpath filename for file
    Uses unix style path without leading slash
        Parameters:
            file(string): input filename
            subdir(string): fullpath to directory that file is in
        Returns:
            filename(string): unix style path for file
    """
    filename = os.path.join(subdir, file)
    filename = filename.replace(os.sep, posixpath.sep)
    filename = filename.strip("/")
    return filename

def yn_check(message = ""):
    """
    Gets yes or no response from user
        Parameters:
            message(string): optional string to be added to prompt
        Returns:
            1 or 0 based on user input
        Quits if user enters invalid response
    """
    print(message + " (y/n)")
    yes = {"yes", "y", "ye", ""}
    no = {"no", "n"}
    choice = input().lower()
    if choice in yes:
        return 1
    elif choice in no:
        return 0
    else:
        print("Please respond with 'yes' or 'no'")
        quit()

if __name__ == "__main__":
    import doctest

    doctest.testmod()