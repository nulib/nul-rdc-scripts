import pandas as pd
from data.videovalues10Bit import tenBitVideoValues as tenBitVideoValues
from data.videovalues8Bit import eightBitVideoValues as eightBitVideoValues

satI = 0
satB = 0
suffix = ["MIN", "MAX", "HIGH", "LOW", "AVG"]
def checkerrors (videodata, videobitdepth, eightBitVideoValues, tenBitVideoValues):

    def setStandardValues (eightBitVideoValues, tenBitVideoValues):
        if videobitdepth == "--8bit" or videobitdepth == "-8":
            standardvalues = eightBitVideoValues
        elif videobitdepth == "--10bit" or videobitdepth == "-10":
            standardvalues = tenBitVideoValues
        return standardvalues
    
    
    def checkLuma (videodata, videobitdepth, standardvalues):
         criteria = "Y"
         checkLOWs(videobitdepth, videodata, standardvalues, criteria)
    
    def checkChromaU (videodata, videobitdepth, standardvalues):
         criteria = "U"
         checkLOWs(videobitdepth, videodata, standardvalues, criteria)
          
    def checkChromaV (videodata, videobitdepth, standardvalues):
         criteria = "V"
         checkLOWs(videobitdepth, videodata, standardvalues, criteria)
    
    def checkLOWs (videodata, standardvalues, criteria):
            criteria = criteria + "LOW"
            criteriaBRNG = standardvalues.get(criteria) 
            criteriaClipping = standardvalues.get(criteria)
            selectColumns = "" + criteria + "," + "Frame Time" + ""
            lowBRNGErrors = setAndRunLowBRNG(criteriaBRNG, criteria, selectColumns, videodata)
            lowClippingErrors = setAndRunLowClipping(criteriaClipping, criteria, selectColumns, videodata)

            if lowBRNGErrors.isEmpty and lowClippingErrors.isEmpty:
                  pass
            elif lowBRNGErrors.isEmpty or lowClippingErrors.isEmpty:
                  if lowBRNGErrors.isEmpty:
                        lowErrors = lowClippingErrors
                  else:
                        lowErrors = lowBRNGErrors
            else:
                  lowErrors = [lowClippingErrors,lowBRNGErrors]
            return lowErrors
                  
    def setAndRunLowClipping(criteria, criteriaClipping, selectColumns, videodata):        
        criteriaEquation = "" + criteria + "==" + criteriaClipping + ""
        lowClippingErrors = {}
        subDF = videodata[[selectColumns]]

        lowClippingErrors = subDF.query(criteriaEquation)
        if subDF.empty:
                 pass
        else:
                 lowClippingErrors.assign(errortype="Low Clipping")
                
        return lowClippingErrors
    
    def setAndRunLowBRNG(criteria, criteriaBRNG, selectColumns, videodata):        
        criteriaEquation = "" + criteria + "=<" + criteriaBRNG + "&" + criteria + "!=" + 0 + ""
        lowBRNGErrors = {}
        subDF = videodata[[selectColumns]]

        lowBRNGErrors = subDF.query(criteriaEquation)
        if lowBRNGErrors.isEmpty:
              pass
        else:
              lowBRNGErrors.assign(errortype="Low BRNG")
        return lowBRNGErrors

    standardvalues = setStandardValues(videobitdepth)
    checkLuma (standardvalues,videodata)
    checkChromaU (standardvalues,videodata)
    checkChromaV (standardvalues,videodata)
    

