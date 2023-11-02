import pandas as pd
from data.videovalues10Bit import tenBitVideoValues as tenBitVideoValues
from data.videovalues8Bit import eightBitVideoValues as eightBitVideoValues

satI = 0
satB = 0
suffix = ["MIN", "MAX", "HIGH", "LOW", "AVG"]
lumaChroma = ["Y", "U", "V"]

YErrors = {}
UErrors = {}
VErrors = {}


def checkerrors(videodata, videobitdepth):
    def setStandardValues():
        if videobitdepth == "--8bit" or videobitdepth == "-8":
            standardvalues = eightBitVideoValues
        elif videobitdepth == "--10bit" or videobitdepth == "-10":
            standardvalues = tenBitVideoValues
        return standardvalues

    standardvalues = setStandardValues(videobitdepth)
    checkMINs(standardvalues, videodata)

    def checksfbf(videodata, standardvalues):
        pass

    def checkMINs(videodata, standardvalues):
        for i in suffix:
            criteria = lumaChroma[i] + "MIN"
            criteriastandard = standardvalues.get[criteria]
            criteriaequation = '"' + criteria + "<" + criteriastandard + '"'
            errorsMINdf = videodata.query(criteriaequation)
            if errorsMINdf.empty:
                pass
            else:
                pass

    def writetolumaChromadict(criteria):
        if criteria == "Y":
            pass
