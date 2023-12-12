"""
Script to use when QCing AV projects.
"""

import sys
import os
import hashlib
import subprocess
from nulrdcscripts.avqc.params import args

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():
    indir = get_input()
    dirs = get_immediate_subdirectories(indir)

    #setup extenstions based on work type
    if args.audio:
        p_ext = ".wav"
        a_ext = ".wav"
    elif args.video:
        p_ext = ".mkv"
        a_ext = ".mp4"
    else:
        p_ext = ".mkv"
        a_ext = ".mov"

    if not args.skip_checksums:
        print("*** Validating Checksums ***")
    # to be populated with any checksum errors
    checksum_faildict = {}

    # list of files to play with mpv
    playlist = []
    playlist_file = os.path.join(indir, "playlist.txt")

    # run through each folder in input directory
    for dirname in dirs:
        dir = os.path.join(indir, dirname)

        # get p folder
        p_dir = os.path.join(dir, "p")
        if not os.path.isdir(p_dir):
            continue

        # get a folder
        a_dir = os.path.join(dir, "a")
        if not os.path.isdir(a_dir):
            print("--- WARNING: No 'a' folder in " + dirname)
            a_dir = None

        # run through each file in \p folder
        for filename in os.listdir(p_dir):
            # skip files w/o p extension
            if not filename.endswith(p_ext):
                continue
            # extra check for these cause it'll think they are p files
            if filename.endswith(".qctools.mkv"):
                continue
            if not args.skip_checksums:
                # write to dict based on result of check
                checksum_result = verify_checksums(filename, p_dir)
                if checksum_result == -1:
                    checksum_faildict.update(
                        {
                            filename: ".md5 not found!" 
                        }
                    )  
                elif checksum_result == 0:
                    checksum_faildict.update(
                        {
                            filename: "md5 checksums don't match!"
                        }
                    )  
            playlist.append(os.path.join(p_dir, filename))
        
        # run through each file in \p folder
        if a_dir:
            for filename in os.listdir(a_dir):
                # skip files w/o p extension
                if not filename.endswith(a_ext):
                    continue
                if not args.skip_checksums:
                    # write to dict based on result of check
                    checksum_result = verify_checksums(filename, a_dir)
                    if checksum_result == -1:
                        checksum_faildict.update(
                            {
                                filename: ".md5 not found" 
                            }
                        )  
                    elif checksum_result == 0:
                        checksum_faildict.update(
                            {
                                filename: "checksums don't match" 
                            }
                        )  
                if args.play_access:
                    playlist.append(os.path.join(a_dir, filename))

    # print results of checksum validation
    if not args.skip_checksums:
        # print all errors if and quit
        if checksum_faildict:
            print("FAIL!")
            for key, value in checksum_faildict.items():
                print(key + ":", value + "---")
            quit()
        # wait for user input to continue in case they left it running
        # while checksums were validated
        print("Success!")
        input("\nPress enter to continue to file inspection...")

    # write files to playlist file
    try:
        with open(playlist_file, "w") as f:
            f.write('\n'.join(playlist))
    except:
        print("--- ERROR: playlist file could not be created ---")

    # open playlist in mpv
    mpv_command = [
        "mpv",
        "--vd-lavc-threads=16",
        "--cache=yes",
        "cache-secs=15",
        "--demuxer-max-bytes=3GiB",
        "--playlist=" + playlist_file,
    ]
    subprocess.run(mpv_command)
    os.remove(playlist_file)
        

def get_input():
    """
    Sets up input directory.

    Returns:
        (str): fullpath to valid input directory
    """
    if args.input_path:
        # checks if directory exists
        if not os.path.isdir(args.input_path):
            print("--- ERROR: Input is not a directory ---")
            quit()
        return args.input_path
    print("Using current directory as input")
    return os.getcwd()

def get_immediate_subdirectories(folder: str):
    """
    Gets list of immediate subdirectories of folder.

    Args:
        folder (str): fullpath to input folder

    Returns:
        (list of str): contains immediate subdirectories of input folder
    """
    return [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]

def verify_checksums(filename: str, dir: str):
    """
    Validates checksum of given file.

    Args:
        filename (str): input filename to check
        dir (str): fullpath to directory of input file

    Returns:
        -1: md5 file not found
        0: checksum not validated
        1: checksum validated
    """
    file = os.path.join(dir, filename)
    md5_file = find_md5(file)
    # returns -1 if file not found
    if not md5_file:
        return -1

    # otherwise returns if they match
    return compare_checksums(file, md5_file)

def compare_checksums(file: str, md5_file: str):
    """
    Compares md5 from file with md5 generated in python.

    Args:
        file (str): fullpath to input file
        md5_file (str): fullpath to md5 file

    Returns:
        True: checksums match
        False: checksums don't match
    """
    computed_md5 = hashlib_md5(file)
    with open(md5_file, "r") as f:
        for line in f:
            words = line.split()
            # reads first word of md5 file
            # which is the actual checksum part
            read_md5 = words[0].lower()
    return computed_md5 == read_md5

def find_md5(file: str):
    """
    Locates md5 checksum file for input file

    Args:
        file (str): fullpath to input file

    Returns:
        md5_file (str): fullpath to md5 file
            or None if md5 file not found
    """
    # ex - filename.wav.md5
    # how vendors send checksums
    md5_file = file + ".md5"
    if os.path.isfile(md5_file):
        return md5_file

    # ex - filename.md5
    # how we save checksums
    base, ext = os.path.splitext(file)
    md5_file = base + ".md5"
    if os.path.isfile(md5_file):
        return md5_file
    
    # if file not found
    return None

def hashlib_md5(file):
    """
    Uses hashlib to return an MD5 checksum of an input filename
    Credit: IFI scripts
    """
    read_size = 0
    last_percent_done = 0
    chksm = hashlib.md5()
    total_size = os.path.getsize(file)
    filename = os.path.basename(file)
    with open(file, "rb") as f:
        while True:
            # 2**20 is for reading the file in 1 MiB chunks
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            chksm.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write(filename + " [%d%%]\r" % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    
    sys.stdout.write("\r")
    blank = " " * (len(filename) + 7)
    sys.stdout.write(blank + "\r")
    
    # print("")
    md5_output = chksm.hexdigest()
    return md5_output

if __name__ == "__main__":
	main()