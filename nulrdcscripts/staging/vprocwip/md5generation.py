import os
import sys
import hashlib

outputAbsPath = "Z:\\RDC\ACTIVE_AV\\p0479_gree\\Sophia\\toedit\\p0479_gree_99-1864621420-2441_v01\\p0479_gree_99-1864621420-2441_v01\\a\\p0479_gree_99-1864621420-2441_v01_a.mp4"
basefilename = os.path.basename(outputAbsPath)
md5output = "Z:\\RDC\ACTIVE_AV\\p0479_gree\\Sophia\\toedit\\p0479_gree_99-1864621420-2441_v01\\p0479_gree_99-1864621420-2441_v01\\a\\p0479_gree_99-1864621420-2441_v01_a.md5"
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



mkvHash = hashlib_md5(outputAbsPath)
with open(md5output, "w", newline="\n") as f:
    print(mkvHash, "*" + basefilename, file=f)