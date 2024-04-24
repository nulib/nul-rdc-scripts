import hashlib
import sys
import os
from nulrdcscripts.tools.checksumCreation.params import args


def hashlib_md5(filename):
    """Uses hashlib to return an MD5 checksum of a input filename
    Credit: IFI scripts"""

    read_size = 0
    last_percent_done = 0
    chksm = hashlib.md5()
    total_size = os.path.getsize(filename)
    with open(filename, "rb") as f:
        while True:
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


def main():
    filename = args.input_path
