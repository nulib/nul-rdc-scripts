import os
import pandas as pd
import subprocess
import tempfile
from paramparser import args


input_path = os.path.normpath(args.input_path)

yuv = ["y", "u", "v"]
counteryuv = 0
yuvvalues = ["min", "low", "avg", "high", "max", "dif", "bitdepth"]
counteryuvvalues = 0
satvalues = ["min", "low", "avg", "high", "max"]
countersatvalues = 0
huevalues = ["med", "avg"]
counterhuevalues = 0
psnrcriteria = ["psnr.mse", "psnr.psnr"]
counterpsnrcriteria = 0
psnrvalues = [".y", ".u", ".v", "_avg"]
counterpsnrvalues = 0
# splitext[0] refers to the first item returned by splitext()
# aka everything but the extension
file_name = os.path.splitext(input_path)[0] + ".txt"


def generatetempfile(fullcriteria):
    temp = tempfile.TemporaryFile()
    # replace backslashes to forward slashes
    movie_path = input_path.replace("\\", "/")
    # delimit any colons
    movie_path = movie_path.replace(":", "\\\\:")

    # NOTE commas will separate items by a space whne running subprocess
    # if you want a single string you need to concatenate
    command = [
        args.ffprobe_path,
        "-f",
        "lavfi",
        "movie=" + movie_path + "," + "signalstats=stat=" + fullcriteria,
        "-show_entries",
        "packet=pts_time" "frame_tags",
        "-of",
        "flat",
    ]

    subprocess.run(command, stdout=temp)
    temp.seek(0)
    searchtxtff = "frames.frame"
    replacetxtempty = ""
    replacetxtcomma = ","
    searchtxtequal = "="
    searchtxtlss = ".tags.lavfi_signalstats_"

    try:
        data = temp.read()
        data = data.replace(searchtxtff, replacetxtempty)
        data = data.replace(searchtxtlss, replacetxtcomma)
        data = data.replace(searchtxtequal, replacetxtcomma)

        print(data)
    except:
        pass

    # with open(temp, "w") as file:
    #    file.write(data)


#
# df = pd.read_csv(temp, delimter=",")
# temp.close()
# print(df)


def runyuvgeneration(input_path, yuv, yuvvalues, counteryuvvalues, counteryuv):
    while counteryuv <= len(yuv):
        criteria = yuv[counteryuv]
        while counteryuvvalues <= len(yuvvalues):
            value = yuvvalues[counteryuvvalues]
            fullcriteria = criteria + value
            numberleft = len(yuv) - counteryuvvalues
            generatetempfile(fullcriteria)
            print(
                criteria
                + "data has been generated."
                + numberleft
                + "left to run for"
                + criteria
            )
            counteryuvvalues += 1
        counteryuv += 1


print("Done")

runyuvgeneration(input_path, yuv, yuvvalues, counteryuvvalues, counteryuv)
