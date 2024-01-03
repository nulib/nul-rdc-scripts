import pandas as pd

yuv = ["y", "u", "v"]
yuvposition = 0
yuvlevel = ["min", "max"]
yuvlevelposition = 0


def buildDF10Bit(csv10Bit):
    """Takes video values from 10bit csv and returns dataframe"""
    standardsDF = pd.read_csv(csv10Bit, sep=",", index_col="criteria")
    return standardsDF


def buildvideodata(videodata):
    """Takes the video data and reads the csv. Returns dataframe"""
    videodata = pd.read_csv(videodata, sep=",")
    return videodata


def setFullCriteria(yuv, yuvlevel):
    """Combines the yuv and yuv level to give the full criteria that gets compared to standards."""
    criteriaFull = yuv + yuvlevel
    return criteriaFull


def setOperator(yuvlevel):
    """Sets the operator to use in the equation"""
    if yuvlevel == "min":
        operator = "<="
    elif yuvlevel == "max":
        operator = ">="
    return operator


def runyuvcheck(yuv, yuvlevel, yuvposition, yuvlevelposition, videodata, standardsDF):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    while yuvposition <= len(yuv):
        yuv = yuv[yuvposition]
        while yuvlevelposition <= len(yuvlevel):
            yuvlevel = yuvlevel[yuvlevelposition]
            criteriaFull = setFullCriteria(yuv, yuvlevel)
            operator = setOperator(yuvlevel)

            yuvlevelposition += 1
        yuvposition += 1
