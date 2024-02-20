import pandas as pd


def checkerrors(videodata, videoBitDepth):
    prefix = ["y", "u", "v"]
    value = 0
    videoerrors = pd.DataFrame()
    while value < len(prefix):
        prefix = prefix[value]
        if prefix == "y":
            videoerrors = check(videodata, videoBitDepth, videoerrors, prefix)
        elif prefix == "u":
            videoerrors = check(videodata, videoBitDepth, videoerrors, prefix)
        if prefix == "v":
            videoerrors = check(videodata, videoBitDepth, videoerrors, prefix)
        value = value + 1
    return videoerrors


def check(prefix, videodata, videoBitDepth, videoerrors):
    fullCriteria = runLOW(prefix)
    checkLOWHIGH(videodata, videoBitDepth, fullCriteria, videoerrors)
    fullCriteria = runHIGH(prefix)
    checkLOWHIGH(videodata, videoBitDepth, fullCriteria, videoerrors)


def runLOW(prefix):
    criteria = prefix + "low"
    return criteria


def runHIGH(prefix):
    criteria = prefix + "high"
    return criteria


def checkLOWHIGH(videodata, videoBitDepth, fullCriteria, videoerrors):
    valuecriteria = str(fullCriteria)
    criteriaBRNG = videoBitDepth.loc[fullCriteria, "brngout"]
    criteriaClipping = videoBitDepth.loc[fullCriteria, "clipping"]
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


def setAndRunClipping(fullCriteria, criteriaClipping, selectColumns, videodata):
    criteriaEquation = "" + fullCriteria + "==" + criteriaClipping + ""
    clippingErrors = {}
    subDF = videodata[[selectColumns]]

    clippingErrors = subDF.query(criteriaEquation)
    if subDF.empty:
        pass
    else:
        if fullCriteria.contains("low"):
            errortype = "Low Clipping"
        elif fullCriteria.contains("high"):
            errortype = "High Clipping"
        clippingErrors.assign(errortype)

    return clippingErrors


def setAndRunBRNG(fullCriteria, criteriaBRNG, selectColumns, videodata):
    if fullCriteria.contains("low"):
        firstOp = "=<"
        clipVal = 0
    elif fullCriteria.contains("high"):
        firstOp = ">="
        clipVal = 1023
    criteriaEquation = (
        ""
        + fullCriteria
        + firstOp
        + criteriaBRNG
        + "&"
        + fullCriteria
        + "!="
        + clipVal
        + ""
    )
    BRNGErrors = {}
    subDF = videodata[[selectColumns]]

    BRNGErrors = subDF.query(criteriaEquation)
    if BRNGErrors.isEmpty:
        pass
    else:
        if fullCriteria.contains("low"):
            errortype = "Low BRNG"
        elif fullCriteria.contains("high"):
            errortype = "High BRNG"
        BRNGErrors.assign(errortype)
    return BRNGErrors
