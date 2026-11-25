#!/usr/bin/env python3

"""
General helper functions for Ingest_Sheet_Maker
"""

import os
import posixpath
import csv

# CSV lookup table of ignore rules, expected to sit alongside this script.
# Override by passing a different path to clean_files(ignore_csv=...).
DEFAULT_IGNORE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore_patterns.csv")


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
        output_path = os.path.join(input_path, base_folder_name + "_ingest.csv")
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
    Rows for each item are sorted in the order:
    asset front, asset side, asset back, tape front, tape side, tape back.
    Files that don't match any pattern are written last, in their original order.

    :param str outfile: fullpath to output file including extension
    :param list csv_fields: fieldnames(headers) for csv file
    :param list csv_data: data to be written to csv
    """
    # Order tokens checked against each file's label (case-insensitive).
    # Earlier position in the list = earlier in the output.
    _LABEL_ORDER = [
        "asset front",
        "asset side",
        "asset back",
        "tape front",
        "tape side",
        "tape back",
    ]

    def _sort_key(file_info: dict) -> int:
        label = (file_info.get("label") or "").lower()
        for idx, token in enumerate(_LABEL_ORDER):
            if token in label:
                return idx
        return len(_LABEL_ORDER)  # unrecognised labels sort last

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for item in csv_data:
            sorted_files = sorted(csv_data[item], key=_sort_key)
            for file_info in sorted_files:
                writer.writerow(file_info)


# Extensions used to detect work_type from the files being ingested.
# Priority when a work has mixed types: VIDEO > AUDIO > IMAGE
WORK_TYPE_EXTENSIONS: dict[str, set[str]] = {
    "VIDEO": {".mkv", ".mp4", ".mov", ".m4v", ".avi", ".mxf", ".dv", ".mpg", ".mpeg", ".webm"},
    "AUDIO": {".wav", ".flac", ".mp3", ".m4a", ".aif", ".aiff", ".bwf"},
    "IMAGE": {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".jp2"},
}


def get_work_type_from_files(filenames: list[str]):
    """
    Determines work_type from file extensions.
    If any video file is present the result is VIDEO, then AUDIO, then IMAGE.

    :param list[str] filenames: names or paths of files
    :returns: 'VIDEO', 'AUDIO', 'IMAGE', or None if no media files are recognized
    :rtype: str
    """
    exts = {os.path.splitext(f)[1].lower() for f in filenames}
    for work_type in ("VIDEO", "AUDIO", "IMAGE"):
        if exts & WORK_TYPE_EXTENSIONS[work_type]:
            return work_type
    return None


def assign_work_types(ingest_dictlist: dict[str, list[dict[str, str]]]):
    """
    Sets work_type on every row, per work_accession_number, based on the files in that work.
    Rows keep their existing work_type if no media files are recognized for the work.

    :param dict ingest_dictlist: ingest sheet data
    """
    works: dict[str, list[dict[str, str]]] = {}
    for rows in ingest_dictlist.values():
        for row in rows:
            works.setdefault(row["work_accession_number"], []).append(row)
    for work_rows in works.values():
        work_type = get_work_type_from_files([r["filename"] for r in work_rows])
        if work_type:
            for row in work_rows:
                row["work_type"] = work_type


def list_files(indir: str, skip: list[str] = None):
    """
    Lists all cleaned filenames under indir.

    :param str indir: fullpath to input directory
    :param list[str] skip: patterns to skip
    :returns: filenames
    :rtype: list of str
    """
    found: list[str] = []
    for _, _, files in os.walk(indir):
        found.extend(clean_files(files, skip))
    return found


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


# Hardcoded fallback, used only if the ignore_patterns.csv lookup table
# can't be found/loaded, so clean_files() never silently stops filtering.
_FALLBACK_STARTSWITH = ["."]
_FALLBACK_EXACT = {"Thumbs.db"}
_FALLBACK_ENDSWITH = [
    ".qctools.mkv",
    ".qctools.xmlpoetry",
    ".qctools.xml.gz",
    ".mkv.xml.gz",
    ".framemd5",
    ".md5",
    ".csv",
    ".py",
    ".log",
    "frame_eia608data.txt",
    "capture_options.log",
    "vrecord_input.tlog",
    ".log-0.log.mbtree",
    ".scc",
    ".vtt",
    ".mkv.qctools.xml",
    "_failing_frames_by_criteria.txt",
    "_video_level_report.txt",
]


def load_ignore_rules(csv_path: str = DEFAULT_IGNORE_CSV):
    """
    Loads the ignore-pattern lookup table from a CSV file.

    Expected CSV columns: match_type (startswith/exact/endswith/contains), pattern.
    Falls back to a hardcoded rule set if the file is missing or unreadable.

    :param str csv_path: fullpath to the ignore_patterns.csv lookup table
    :returns: (startswith patterns, exact filenames, endswith patterns, contains patterns)
    :rtype: tuple(list, set, list, list)
    """
    startswith: list[str] = []
    exact: set[str] = set()
    endswith: list[str] = []
    contains: list[str] = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                match_type = (row.get("match_type") or "").strip()
                pattern = (row.get("pattern") or "").strip()
                if not pattern:
                    continue  # empty pattern would match every file
                if match_type == "startswith":
                    startswith.append(pattern)
                elif match_type == "exact":
                    exact.add(pattern)
                elif match_type == "endswith":
                    endswith.append(pattern)
                elif match_type == "contains":
                    contains.append(pattern)
    except OSError:
        print(f"\n--- WARNING: Could not read {csv_path}, using built-in defaults ---\n")
        return list(_FALLBACK_STARTSWITH), set(_FALLBACK_EXACT), list(_FALLBACK_ENDSWITH), []

    return startswith, exact, endswith, contains


def clean_files(files: list[str], skip: list[str], ignore_csv: str = DEFAULT_IGNORE_CSV):
    """
    Removes files to be ignored when making ingest sheet.
    Default ignore patterns (hidden files, Thumbs.db, QC/report/log sidecar
    files, etc.) are loaded from the ignore_patterns.csv lookup table so new
    patterns can be added there instead of editing this function.
    .jpg ignore rules only apply when the folder also contains a .tif/.tiff.

    :param list files: list of files in a directory
    :param list skip: list of files to skip in addition defaults
    :param str ignore_csv: fullpath to the ignore_patterns.csv lookup table
    :returns: cleaned and sorted list of files
    :rtype: list of str
    """
    startswith, exact, endswith, contains = load_ignore_rules(ignore_csv)

    # jpgs are only ignored when a tif is present in the same folder,
    # so folders with only jpgs still get ingested
    if not any(f.lower().endswith((".tif", ".tiff")) for f in files):
        startswith = [p for p in startswith if ".jpg" not in p.lower()]
        endswith = [p for p in endswith if ".jpg" not in p.lower()]
        contains = [p for p in contains if ".jpg" not in p.lower()]

    files = [
        f
        for f in files
        if f not in exact
        and not any(f.startswith(p) for p in startswith)
        and not any(f.endswith(p) for p in endswith)
        and not any(p in f for p in contains)
    ]

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


def yn_check(message=""):
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