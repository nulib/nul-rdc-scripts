import nulrdcscripts.vqc.setup as setup
import pandas as pd
from collections import namedtuple

# errortuple = namedtuple("Error", ["type", "criteria", "video value", "standard value"])
standardcsv = "nulrdcscripts\\vqc\Video10BitValues.csv"
standardDF = pd.read_csv(standardcsv, sep=",")
videodatasum = "testdata.csv"
videoDSDF = pd.read_csv(videodatasum, sep=",")


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


def runyuvanalysis(videoDSDF, standardDF, fullCriteria):
    if fullCriteria.endswith("low"):
        level = "low"
    else:
        level = "high"
    extractSumData = videoDSDF.at(fullCriteria, level)
    extractStandDataBRNG = standardDF.at(fullCriteria, "brngout")
    extractStandDataClipping = standardDF.at(fullCriteria, "clipping")
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
            errors = {
                "Error Type": "Clipping",
                "criteria": fullCriteria,
                "Video Value": extractSumData,
                "Standard Value": extractStandDataClipping,
            }
            # error = errortuple("clipping",fullCriteria,extractSumData,extractStandDataClipping)
            return errors
        else:
            errors = {
                "Error Type": "Out of Broadcasting Range",
                "criteria": fullCriteria,
                "Video Value": extractSumData,
                "Standard Value": extractStandDataBRNG,
            }
            # error = errortuple("brngout",fullCriteria,extractSumData,extractStandDataBRNG)
            return errors


def runcheckyuv(videoDSDF, standardsDF):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    yuverrors = {}
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        fullCriteria = str(fullCriteria)
        yuverrors = runyuvanalysis(
            fullCriteria,
            videoDSDF,
            standardsDF,
        )
    return yuverrors


def runsatanalysis(videoDSDF, standardDF, errors):
    criteria = "sat"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    extractSumData = videoDSDF.at(leveltoCheck, fullCriteria)
    extractStandDataBRNG = standardDF.at(criteria, "brnglimit")
    extractStandDataClipping = standardDF.at(criteria, "clippinglimit")
    extractStandDataIllegal = standardDF.at(criteria, "illegal")
    if extractSumData <= extractStandDataBRNG:
        pass
    else:
        if extractSumData >= extractStandDataIllegal:
            errors = {
                "Error Type": "Illegal",
                "criteria": fullCriteria,
                "Video Value": extractSumData,
                "Standard Value": extractStandDataIllegal,
            }
            # error = errortuple("illegal",fullCriteria, extractSumData, extractStandDataIllegal)
            return errors
        else:
            errors = {
                "Error Type": "Clipping",
                "criteria": fullCriteria,
                "Video Value": extractSumData,
                "Standard Value": extractStandDataClipping,
            }
            # error = errortuple("clipping", fullCriteria, extractSumData,extractStandDataClipping)
            return errors


def runTOUTandVREPanalysis(videoDSDF, standardDF, errors):
    criterium = ["tout", "vrep"]
    for c in criterium:
        criteria = criterium[c]
        level = "max"
        extractSumData = videoDSDF.at(level, criteria)
        extractStandDataMax = standardDF.at(criteria, level)
        if extractSumData >= extractStandDataMax:
            errors = {
                "Error Type": "Exceeds Standard",
                "criteria": criteria,
                "Video Value": extractSumData,
                "Standard Value": extractStandDataMax,
            }
            return errors
        else:
            pass


def runOverallVideo(standardDF, videoDSDF):
    yuverrors = runcheckyuv(standardDF, videoDSDF)
    print(yuverrors)
    # saterrors = runsatanalysis(standardDF, videoDSDF)
    # toutVREPErrors = runTOUTandVREPanalysis(standardDF, videoDSDF)


runOverallVideo(standardDF, videoDSDF)
