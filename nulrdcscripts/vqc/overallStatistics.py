from collections import namedtuple

errortuple = namedtuple("Error", ["type", "criteria", "video value", "standard value"])
errors = {}

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


def runyuvanalysis(videodata, standardsDF, fullCriteria, errors):
    if fullCriteria.endswith("low"):
        level = "low"
    else:
        level = "high"
    extractSumData = videodata.at(
        fullCriteria, level
    ) 
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
            errors = {'Error Type': 'Clipping', 'criteria':fullCriteria, 'Video Value':extractSumData, 'Standard Value':extractStandDataClipping}
            #error = errortuple("clipping",fullCriteria,extractSumData,extractStandDataClipping)
            return errors
        else:
            errors = {'Error Type':'Out of Broadcasting Range', 'criteria':fullCriteria, 'Video Value':extractSumData, 'Standard Value': extractStandDataBRNG}
            #error = errortuple("brngout",fullCriteria,extractSumData,extractStandDataBRNG)
            return errors

def runcheckyuv(videodata, standardsDF):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        errors = runyuvanalysis(
            fullCriteria,
            videodata,
            standardsDF,
        )
    return errors


def runsatanalysis(videodata, standardsDF, errors):
    criteria = "sat"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    extractSumData = videodata.at(leveltoCheck, fullCriteria)  
    extractStandDataBRNG = standardsDF.at(criteria, "brnglimit")
    extractStandDataClipping = standardsDF.at(criteria, "clippinglimit")
    extractStandDataIllegal = standardsDF.at(criteria, "illegal")
    if extractSumData <= extractStandDataBRNG:
        pass
    else:
        if extractSumData >= extractStandDataIllegal:
            errortype = "illegal"
            errors = {'Error Type': 'Illegal', 'criteria': fullCriteria, 'Video Value': extractSumData, 'Standard Value':extractStandDataIllegal}
            #error = errortuple("illegal",fullCriteria, extractSumData, extractStandDataIllegal)
            return errors
        else:
            errors = {'Error Type':'Clipping','criteria':fullCriteria, 'Video Value': extractSumData, 'Standard Value': extractStandDataClipping}
            #error = errortuple("clipping", fullCriteria, extractSumData,extractStandDataClipping)
            return errors

def runTOUTandVREPanalysis(videodata,standardsDF, errors):
    criterium = ["tout","vrep"]
    for c in criterium:
        criteria=criterium[c]
        level = "max"
        extractSumData =videodata.at(level, criteria)
        extractStandDataMax = standardsDF.at(criteria,level)
        if extractSumData >= extractStandDataMax:
            errors = {"Error Type": 'Exceeds Standard', 'criteria':criteria,'Video Value':extractSumData, 'Standard Value': extractStandDataMax}
            return errors
        else:
            pass