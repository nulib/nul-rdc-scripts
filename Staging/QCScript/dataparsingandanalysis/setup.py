import os
from data import videovalues8Bit
from data import videovalues10Bit

def inputCheck(inputPath):
    if not os.path.isdir(inputPath):
        inputType = "File"
    else:
        inputType = "Folder"
    return inputType


def outputCheck(outputPath, inputPath):
    if outputPath:
        outputPath = outputPath
    else:
        outputPath = os.path.basename(inputPath)
    return outputPath


def setVideoBitDepth (videobitdepth):
    if videobitdepth == "--8bit" or "-8":
        standardvalues = videovalues8Bit
    elif videobitdepth == "--10bit" or "-10":
        standardvalues = videovalues10Bit
    return standardvalues