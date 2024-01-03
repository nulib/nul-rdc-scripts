import pandas as pd
import os

csv10Bit = "Video10BitValues.csv"
videodata = "videosummarystats.csv"
errors = {}


def buildDF10Bit(csv10Bit):
    standardsDF = pd.read_csv(csv10Bit, sep=",", index_col="criteria")
    return standardsDF


def buildvideodata(videodata):
    videodata = pd.read_csv(videodata, sep=",")
    return videodata


def generateGenStatsReport(videodata, standardsDF):
    videoerrors = setupStatsYUV(videodata, standardsDF)
    return videoerrors


def setupStatsYUV(videodata, standardsDF):
    yuv = ["y", "u", "v"]
    yuvlevels = ["min", "max"]
    setYUV(yuv, yuvlevels, videodata, standardsDF)


def setoperator(level):
    if level == "min":
        operator = "<="
    elif level == "max":
        operator = ">="
    return operator


def yuvGenStats(level, criteria, videodata, standardsDF):
    operator = setoperator(level)
    criteriaFull = criteria + level
    extraction = videodata.at[level, criteriaFull]
    standardExtraction = standardsDF.at[criteriaFull, level]

    equation = extraction + operator + standardExtraction
    equationeval = eval(equation)
    if equationeval:
        pass
    else:
        errors = {
            criteriaFull: {
                "Video Value": extraction,
                "Standards Value": standardExtraction,
            }
        }

    return errors


def setYUVLevels(yuvlevels, criteria, videodata, standardsDF):
    position = 0
    while position <= len(yuvlevels):
        level = yuvlevels[position]
        yuvGenStats(level, criteria, videodata, standardsDF)
        position += 1


def setYUV(yuv, yuvlevels, videodata, standardsDF):
    position = 0
    while position <= len(yuv):
        criteria = yuv[position]
        setYUVLevels(yuvlevels, criteria, videodata, standardsDF)
        position += 1


standardsDF = buildDF10Bit(csv10Bit)
videodata = buildvideodata(videodata)
generateGenStatsReport(videodata, standardsDF)
