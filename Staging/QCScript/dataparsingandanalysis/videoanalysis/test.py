import videovalues10Bit

videodata = "baddata.csv"

def runLOW (criteria):
    criteria = criteria + "LOW"
    return criteria

def runHIGH (criteria):
    criteria = criteria + "HIGH"
    return criteria


def checkLOWHIGH(videodata, videoBitDepth, fullCriteria):
    criteriaBRNG = videoBitDepth.get(fullCriteria["BRNG"])
    criteriaClipping = videoBitDepth.get(fullCriteria["clipping"])
    selectColumns = "" + fullCriteria + "," + "Frame Time" + ""
    BRNGErrors = setAndRunBRNG(
        criteriaBRNG, fullCriteria, selectColumns, videodata
    )
    clippingErrors = setAndRunClipping(
        criteriaClipping, fullCriteria, selectColumns, videodata
    )

    if BRNGErrors.isEmpty and clippingErrors.isEmpty:
        pass
    elif BRNGErrors.isEmpty or clippingErrors.isEmpty:
        if BRNGErrors.isEmpty:
            videoYUVErrors = clippingErrors
        else:
            videoYUVErrors = BRNGErrors
    else:
        videoYUVErrors = [clippingErrors, BRNGErrors]
    return videoYUVErrors

def setAndRunClipping(criteria, criteriaClipping, selectColumns, videodata):
    criteriaEquation = "" + criteria + "==" + criteriaClipping + ""
    clippingErrors = {}
    subDF = videodata[[selectColumns]]

    clippingErrors = subDF.query(criteriaEquation)
    if subDF.empty:
        pass
    else:
        if criteria.contains ("LOW"):
            errortype = "Low Clipping"
        elif criteria.contains ("HIGH"):
            errortype = "High Clipping"
        clippingErrors.assign(errortype)

    return clippingErrors

def setAndRunBRNG(criteria, criteriaBRNG, selectColumns, videodata):
    if criteria.contains ("LOW"):
        firstOp = "=<"
        clipVal = 0
    elif criteria.contains ("HIGH"):
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
        if criteria.contains ("LOW"):
            errortype = "Low BRNG"
        elif criteria.contains ("HIGH"):
            errortype = "High BRNG"
        BRNGErrors.assign(errortype)
    return BRNGErrors

def check():
    videodata = "baddata.csv"
    criteria = "Y"
    videoBitDepth = videovalues10Bit
    fullCriteria = runLOW(criteria)
    checkLOWHIGH (videodata,videoBitDepth, fullCriteria)
    fullCriteria = runHIGH(criteria)
    checkLOWHIGH (videodata, videoBitDepth, fullCriteria)

check()