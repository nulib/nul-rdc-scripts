import os


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


def setVideoBitDepth(videobitdepth):
    if videobitdepth == "--8bit" or "-8" or "--8Bit":
        bitDepth = 8
    elif videobitdepth == "--10bit" or "-10" or "--10Bit":
        bitDepth = 10
    return bitDepth
