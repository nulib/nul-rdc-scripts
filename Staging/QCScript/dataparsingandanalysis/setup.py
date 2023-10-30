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


