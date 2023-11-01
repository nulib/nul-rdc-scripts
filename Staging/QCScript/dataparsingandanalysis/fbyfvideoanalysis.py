import pandas as pd
from data.videovalues10Bit import tenBitVideoValues as tenBitVideoValues
from data.videovalues8Bit import eightBitVideoValues as eightBitVideoValues

satI = 0
satB = 0
suffix = ["MIN", "MAX", "HIGH", "LOW", "AVG"]
lumaChroma = ["Y", "U", "V"]


def checkerrors(videodata, videobitdepth):
    def setStandardValues():
        if videobitdepth == "--8bit" or videobitdepth == "-8":
            standardvalues = eightBitVideoValues
        elif videobitdepth == "--10bit" or videobitdepth == "-10":
            standardvalues = tenBitVideoValues
        return standardvalues

    standardvalues = setStandardValues(videobitdepth)
    checkSAT(standardvalues, videodata)

    def checksfbf(videodata, standardvalues):
        pass

    def checkMINs(videodata, standardvalues):
        for i in suffix:
            criteria = lumaChroma[i] + "MIN"
            criteriastandard = standardvalues.get[criteria]
            errorBRNG = []

    def checkSAT(videodata, standardvalues):
        for i in suffix:
            criteria = "SAT" + suffix[i]
            criteriaChecking = standardvalues.get[criteria]
            satOutRNG = []
            for index, row in videodata.iterrows():
                """if value > value:
                    satOutRNG.append(row[index])
                    satI = satI + 1
                else:
                    pass
                """
