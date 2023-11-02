import pandas as pd
from data.videovalues10Bit import tenBitVideoValues as tenBitVideoValues
from data.videovalues8Bit import eightBitVideoValues as eightBitVideoValues

satI = 0
satB = 0
suffix = ["MIN", "MAX", "HIGH", "LOW", "AVG"]
lumaChroma = ["Y", "U", "V"]

YErrors = {}
UErrors = {}
VErrors = {}


def checkerrors(videodata, videobitdepth):
    def setStandardValues():
        if videobitdepth == "--8bit" or videobitdepth == "-8":
            standardvalues = eightBitVideoValues
        elif videobitdepth == "--10bit" or videobitdepth == "-10":
            standardvalues = tenBitVideoValues
        return standardvalues

   