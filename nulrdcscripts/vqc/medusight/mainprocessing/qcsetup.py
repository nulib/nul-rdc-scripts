import os
import pandas as pd
import pathlib


csv8Bit = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "Video8BitValues.csv"
)
csv10Bit = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "Video10BitValues.csv"
)


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
    videobitdepth = int(videobitdepth)
    if videobitdepth == 8:
        standardsDF = pd.read_csv(csv8Bit, sep=",", index_col="criteria")
    elif videobitdepth == 10:
        standardsDF = pd.read_csv(csv10Bit, sep=",", index_col="criteria")
    return standardsDF


def setInputFileType(inputPath):
    """Sets the file type of the input file"""
    fileExt = pathlib.Path(inputPath).suffix
    
    # Fixed: Added proper if/elif/else structure
    if fileExt == ".xml":
        fileType = "XML"
    elif fileExt == ".csv":
        fileType = "CSV"
    elif fileExt in ['.mkv', '.mov', '.mp4', '.avi', '.mxf', '.dv']:
        fileType = "VIDEO"
    else:
        raise ValueError(f"This filetype is not currently supported: {fileExt}")
    
    return fileType