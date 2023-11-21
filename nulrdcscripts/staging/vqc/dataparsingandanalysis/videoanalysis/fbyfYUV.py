import pandas as pd

videodata = "baddata.csv"


def checkerrors(videodata, videoBitDepth):
    videoerrors = pd.DataFrame()
    checkLuma(videoBitDepth, videodata, videoerrors)
    checkChromaU(videoBitDepth, videodata, videoerrors)
    checkChromaV(videoBitDepth, videodata, videoerrors)
    return videoerrors


def checkLuma(videodata, videoBitDepth, videoerrors):
    criteria = "Y"
    check(videodata, videoBitDepth, criteria, videoerrors)


def checkChromaU(videodata, videoBitDepth, videoerrors):
    criteria = "U"
    check(videodata, videoBitDepth, criteria, videoerrors)


def checkChromaV(videodata, videoBitDepth, videoerrors):
    criteria = "V"
    check(criteria, videodata, videoBitDepth, videoerrors)


def check(criteria, videodata, videoBitDepth, videoerrors):
    fullCriteria = runLOW(criteria)
    checkLOWHIGH(videodata, videoBitDepth, fullCriteria, videoerrors)
    fullCriteria = runHIGH(criteria)
    checkLOWHIGH(videodata, videoBitDepth, fullCriteria, videoerrors)


def runLOW(criteria):
    criteria = criteria + "low"
    return criteria


def runHIGH(criteria):
    criteria = criteria + "high"
    return criteria


def checkLOWHIGH(videodata, videoBitDepth, fullCriteria, videoerrors):
    criteriaBRNG = videoBitDepth.get(fullCriteria["BRNG"])
    criteriaClipping = videoBitDepth.get(fullCriteria["clipping"])
    selectColumns = "" + fullCriteria + "," + "Frame Time" + ""
    BRNGErrors = setAndRunBRNG(criteriaBRNG, fullCriteria, selectColumns, videodata)
    clippingErrors = setAndRunClipping(
        criteriaClipping, fullCriteria, selectColumns, videodata
    )

    if BRNGErrors.isEmpty and clippingErrors.isEmpty:
        pass
    elif BRNGErrors.isEmpty or clippingErrors.isEmpty:
        if BRNGErrors.isEmpty:
            videoerrors = clippingErrors
        else:
            videoerrors = BRNGErrors
    else:
        videoerrors = [clippingErrors, BRNGErrors]
    return videoerrors


def setAndRunClipping(criteria, criteriaClipping, selectColumns, videodata):
    criteriaEquation = "" + criteria + "==" + criteriaClipping + ""
    clippingErrors = {}
    subDF = videodata[[selectColumns]]

    clippingErrors = subDF.query(criteriaEquation)
    if subDF.empty:
        pass
    else:
        if criteria.contains("low"):
            errortype = "Low Clipping"
        elif criteria.contains("high"):
            errortype = "High Clipping"
        clippingErrors.assign(errortype)

    return clippingErrors


def setAndRunBRNG(criteria, criteriaBRNG, selectColumns, videodata):
    if criteria.contains("low"):
        firstOp = "=<"
        clipVal = 0
    elif criteria.contains("high"):
        firstOp = ">="
        clipVal = 1023
    criteriaEquation = (
        "" + criteria + firstOp + criteriaBRNG + "&" + criteria + "!=" + clipVal + ""
    )
    BRNGErrors = {}
    subDF = videodata[[selectColumns]]

    BRNGErrors = subDF.query(criteriaEquation)
    if BRNGErrors.isEmpty:
        pass
    else:
        if criteria.contains("low"):
            errortype = "Low BRNG"
        elif criteria.contains("high"):
            errortype = "High BRNG"
        BRNGErrors.assign(errortype)
    return BRNGErrors
