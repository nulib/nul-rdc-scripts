import datetime
import hashlib
import os
import sys
import time


def guess_date(string):
    for fmt in ["%m/%d/%Y", "%d-%m-%Y", "%m/%d/%y", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            continue
    raise ValueError(string)


def convert_runtime(duration):
    runtime = time.strftime("%H:%M:%S", time.gmtime(float(duration)))
    return runtime


def delete_files(list):
    """
    Loops through a list of files and tries to delete them
    """
    for i in list:
        try:
            os.remove(i)
        except FileNotFoundError:
            print("unable to delete " + i)
            print("File not found")


def hashlib_md5(filename):
    """
    Uses hashlib to return an MD5 checksum of an input filename
    Credit: IFI scripts
    """
    read_size = 0
    last_percent_done = 0
    chksm = hashlib.md5()
    total_size = os.path.getsize(filename)
    with open(filename, "rb") as f:
        while True:
            # 2**20 is for reading the file in 1 MiB chunks
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            chksm.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write("[%d%%]\r" % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    md5_output = chksm.hexdigest()
    return md5_output
