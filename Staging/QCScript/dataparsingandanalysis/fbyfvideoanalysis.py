import pandas as pd
import data.videovalues10Bit as tenBitVideoValues
import data.videovalues8Bit as eightBitVideoValues
from argparser import args

videobitdepth = args.videobitdepth


def setStandardValues(eightBitVideoValues, tenBitVideoValues):
    if videobitdepth == "--8bit" or videobitdepth == "-8":
        standardvalues = eightBitVideoValues
    elif videobitdepth == "--10bit" or videobitdepth == "-10":
        standardvalues = tenBitVideoValues
    return standardvalues


def checkerrors(videodata, videobitdepth, standardvalues, tenBitVideoValues):
    def checkLuma(videodata, videobitdepth, standardvalues):
        criteria = "Y"
        checkLOWs(videobitdepth, videodata, standardvalues, criteria)

    def checkChromaU(videodata, videobitdepth, standardvalues):
        criteria = "U"
        checkLOWs(videobitdepth, videodata, standardvalues, criteria)

    def checkChromaV(videodata, videobitdepth, standardvalues):
        criteria = "V"
        checkLOWs(videobitdepth, videodata, standardvalues, criteria)

    def checkHIGHs(videodata, standardvalues, criteria):
        criteria = criteria + "HIGH"
        criteriaBRNG = standardvalues.criteria.get(["BRNG"])
        criteriaClipping = standardvalues.criteria.get(["clipping"])
        selectColumns = "" + criteria + "" + "," + "Frame Time" + ""
        highBRNGErrors = setAndRunHighBRNG(
            criteriaBRNG, criteria, selectColumns, videodata
        )
        highClippingErrors = setAndRunHighClipping(
            criteriaClipping, criteria, selectColumns, videodata
        )

        if highBRNGErrors.isEmpty and highClippingErrors.isEmpty:
            pass
        elif highBRNGErrors.isEmpty or highClippingErrors.isEmpty:
            if highClippingErrors.isEmpty:
                highErrors = highBRNGErrors
            else:
                highErrors = highClippingErrors
        else:
            highErrors = [highBRNGErrors, highClippingErrors]
        return highErrors

    def setAndRunHighClipping(criteria, criteriaClipping, selectColumns, videodata):
        criteriaEquation = "" + criteria + ">=" + criteriaClipping + ""
        highClippingErrors = {}
        subDF = videodata[[selectColumns]]

        highClippingErrors = subDF.query(criteriaEquation)
        if subDF.empty:
            pass
        else:
            highClippingErrors.assign(errortype="High Clipping")
        return highClippingErrors

    def setAndRunHighBRNG(criteria, criteriaBRNG, selectColumns, videodata):
        criteriaEquation = "" + criteria + "=<" + criteriaBRNG
        highBRNGErrors = {}
        subDF = videodata[[selectColumns]]

        highBRNGErrors = subDF.query(criteriaEquation)
        if highBRNGErrors.isEmpty:
            pass
        else:
            highBRNGErrors.assign(errortype="High BRNG")
        return highBRNGErrors

    def checkLOWs(videodata, standardvalues, criteria):
        criteria = criteria + "LOW"
        criteriaBRNG = standardvalues.get(criteria["BRNG"])
        criteriaClipping = standardvalues.get(criteria["clipping"])
        selectColumns = "" + criteria + "," + "Frame Time" + ""
        lowBRNGErrors = setAndRunLowBRNG(
            criteriaBRNG, criteria, selectColumns, videodata
        )
        lowClippingErrors = setAndRunLowClipping(
            criteriaClipping, criteria, selectColumns, videodata
        )

        if lowBRNGErrors.isEmpty and lowClippingErrors.isEmpty:
            pass
        elif lowBRNGErrors.isEmpty or lowClippingErrors.isEmpty:
            if lowBRNGErrors.isEmpty:
                lowErrors = lowClippingErrors
            else:
                lowErrors = lowBRNGErrors
        else:
            lowErrors = [lowClippingErrors, lowBRNGErrors]
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
        criteriaEquation = (
            "" + criteria + "=<" + criteriaBRNG + "&" + criteria + "!=" + 0 + ""
        )
        lowBRNGErrors = {}
        subDF = videodata[[selectColumns]]

        lowBRNGErrors = subDF.query(criteriaEquation)
        if lowBRNGErrors.isEmpty:
            pass
        else:
            lowBRNGErrors.assign(errortype="Low BRNG")
        return lowBRNGErrors

    standardvalues = setStandardValues(
        videobitdepth, eightBitVideoValues, tenBitVideoValues
    )
    YErrors = checkLuma(standardvalues, videodata)
    UErrors = checkChromaU(standardvalues, videodata)
    VErrors = checkChromaV(standardvalues, videodata)
