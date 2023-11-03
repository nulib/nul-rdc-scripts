import os
import data.videovalues10Bit as tenBitVideoValues
import data.videovalues8Bit as eightBitVideoValues


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


def setBitDepth (videoBitDepth):
    if videoBitDepth == "--8bit" or videoBitDepth == "-8":
        standardvalues = eightBitVideoValues
    elif videoBitDepth == "--10bit" or videoBitDepth == "-10":
        standardvalues = tenBitVideoValues
    return standardvalues