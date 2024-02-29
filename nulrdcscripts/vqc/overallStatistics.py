from collections import namedtuple

error = namedtuple("Error", ["criteria", "video value", "standard value"])


def setOperatorIR(fullCriteria):
    """Sets the operator to assess if video value is in range"""
    if fullCriteria.endswith("low"):
        operatorIR = ">"
    else:
        operatorIR = "<"
    return operatorIR


def setOperatorCL(fullCriteria):
    """Sets operator to use to assess clipping"""
    if fullCriteria.endswith("low"):
        operatorCL = "<="
    else:
        operatorCL = ">="
    return operatorCL


def runyuvanalysis(videodata, standardsDF, fullCriteria, error):
    if fullCriteria.endswith("low"):
        level = "low"
    else:
        level = "high"
    extractSumData = videodata.at(
        fullCriteria, level
    )  # grabs data from dataframe at this matrix intersection # NEED TO FIX
    extractStandDataBRNG = standardsDF.at(fullCriteria, "brngout")
    extractStandDataClipping = standardsDF.at(fullCriteria, "clipping")
    operatorIR = setOperatorIR(level)
    equationIR = extractSumData + operatorIR + extractStandDataBRNG
    tfIR = eval(equationIR)
    if tfIR:
        pass
    else:
        operatorCL = setOperatorCL(level)
        equationCL = extractSumData + operatorCL + extractStandDataClipping
        tfCL = eval(equationCL)
        if tfCL:
            error = {""}


def runcheckyuv(videodata, standardsDF):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        errorsYUV = runyuvanalysis(
            fullCriteria,
            videodata,
            standardsDF,
        )
    return errorsYUV


def runsatanalysis(videodata, standardsDF, error):
    criteria = "sat'"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    extractSumData = videodata.at(leveltoCheck, fullCriteria)  # ADD
    extractStandDataBRNG = standardsDF.at(criteria, "brnglimit")
    extractStandDataClipping = standardsDF.at(criteria, "clippinglimit")
    extractStandDataIllegal = standardsDF.at(criteria, "illegal")
    if extractSumData <= extractStandDataBRNG:
        status = "pass"
        errorsSat = error(fullCriteria)
    else:
        if extractSumData >= extractStandDataIllegal:
            status = "fail"
            errorsSat = error(
                fullCriteria, status, extractSumData, extractStandDataIllegal
            )
        else:
            status = "fail"
            errorsSat = error(
                fullCriteria, status, extractSumData, extractStandDataClipping
            )
    return errorsSat
