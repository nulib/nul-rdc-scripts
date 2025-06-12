import os
import pandas as pd
import pathlib

path8Bit = "nulrdcscripts\\vqc\\data\\Video8BitValues.csv"
path10Bit = "nulrdcscripts\\vqc\\data\\Video10BitValues.csv"

csv8Bit = os.path.join(os.path.dirname(os.path.abspath(__file__)), path8Bit)
csv10Bit = os.path.join(os.path.dirname(os.path.abspath(__file__)), path10Bit)


def inputCheck(inputPath):
    """Checks that the input path is a file and not a folder which is currently not supported"""
    if os.path.isdir(inputPath):
        raise ValueError("Folders are currently not supported by this script")
    else:
        pass


def outputCheck(inputPath, outputPath):
    """Checks if there is an output path. If there isn't, the file goes to the directory of the input file. Otherwise, checks if the output path is a folder"""
    if outputPath == "input":
        outputPath = os.path.dirname(inputPath)
    else:
        outputPathTF = os.path.isdir(outputPath)
        if outputPathTF:
            outputPath = os.path.normpath(outputPath)
        else:
            raise ValueError("The output path must be a folder")
    return outputPath


def setVideoBitDepth(videobitdepth):
    """Sets and assigns the values for bit depth for data comparison"""
    if videobitdepth in ["8bit", "8", "8Bit"]:
        standardsDF = pd.read_csv(csv8Bit, sep=",", index_col="criteria")
    elif videobitdepth in ["10bit", "10", "10Bit"]:
        standardsDF = pd.read_csv(csv10Bit, sep=",", index_col="criteria")
    else:
        raise ValueError("Unsupported video bit depth. Choose '8bit' or '10bit'.")
    return standardsDF


def setInputFileType(inputPath):
    """Sets the file type of the input file"""
    fileExt = pathlib.Path(inputPath).suffix
    if fileExt == ".json":
        fileType = "JSON"
    elif fileExt == ".xml":
        fileType = "XML"
    else:
        raise ValueError("This filetype is not currently supported.")
    return fileType
