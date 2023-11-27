import os
import setvideostandardvals


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
    if videobitdepth == "--8bit" or "-8":
        bitDepth = 8
        standardsDF = setvideostandardvals.setvideobitdepthstandards(videobitdepth)
    elif videobitdepth == "--10bit" or "-10":
        bitDepth = 10
        standardsDF = setvideostandardvals.setvideobitdepthstandards(bitDepth)
    return standardsDF
