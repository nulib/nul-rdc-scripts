import pandas as pd
from data.videovalues10Bit import tenBitVideoValues as tenBitVideoValues
from data.videovalues8Bit import eightBitVideoValues as eightBitVideoValues

satI = 0
satB = 0
suffix = ["MIN", "MAX", "HIGH", "LOW", "AVG"]
def checkerrors (videodata, videobitdepth):
    def setStandardValues ():
        if videobitdepth == "--8bit" or videobitdepth == "-8":
            standardvalues = eightBitVideoValues
        elif videobitdepth == "--10bit" or videobitdepth == "-10":
            standardvalues = tenBitVideoValues
        return standardvalues
    
    standardvalues = setStandardValues(videobitdepth)
    
    
    def checkLOWs (videodata, standardvalues, criteria):
            criteria = criteria + "LOW"
            criteriaBRNG = standardvalues.get(tenBitVideoValues[criteria]["BRNGOut"])
            criteriaClipping = standardvalues.get(tenBitVideoValues[criteria]["clipping"])
            criteriaEquation = "" + criteria + "=<" + criteriaBRNG + ""
            lowErrors = {}
            dfLowErrors = videodata.query(criteriaEquation)
            if dfLowErrors.empty:
                 pass
            else:
                 lowErrors["LOW Errors"] = dfLowErrors
                
            return lowErrors
                



