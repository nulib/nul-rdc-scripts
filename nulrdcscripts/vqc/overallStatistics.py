import pandas as pd
import json
from nulrdcscripts.vqc.multiuse import setLevel,setOperatorCL,setOperatorIR,setLeveltoCheck
# errortuple = namedtuple("Error", ["type", "criteria", "video value", "standard value"])
standardcsv = "nulrdcscripts/vqc/Video10BitValues.csv"
standardDF = pd.read_csv(standardcsv, sep=",", index_col=0)
videodata = "nulrdcscripts/vqc/testdata.csv"
sumdata = pd.read_csv(videodata, sep=",", index_col=0)
errors = {}




def runyuvanalysis(standardDF, sumdata, fullCriteria, level):
    leveltoCheck = setLeveltoCheck(level)
    extractSumData = sumdata.at[leveltoCheck, fullCriteria]
    extractStandDataBRNG = standardDF.at[fullCriteria, "brngout"]
    extractStandDataClipping = standardDF.at[fullCriteria, "clipping"]
    operatorIR = setOperatorIR(level)
    equationIR = str(extractSumData) + operatorIR + str(extractStandDataBRNG)
    tfIR = eval(equationIR)
    if tfIR:
        errors= {
            "Video Value":extractSumData,
            "Pass/Fail": "Pass"

        }
    else:
        operatorCL = setOperatorCL(level)
        equationCL = str(extractSumData) + operatorCL + str(extractStandDataClipping)
        tfCL = eval(equationCL)
        if tfCL:
            errors = {
                "Error Type": "Clipping",
                "Video Value": extractSumData,
                "Standard Value": extractStandDataClipping,
                "Pass/Fail": "Fail"
            }
            # error = errortuple("clipping",fullCriteria,extractSumData,extractStandDataClipping)
        else:
            errors = {
                "Error Type": "Out of Broadcasting Range",
                "Video Value": extractSumData,
                "Standard Value": extractStandDataBRNG,
                "Pass/Fail": "Fail"
            }
            # error = errortuple("brngout",fullCriteria,extractSumData,extractStandDataBRNG)
    return errors


def runcheckyuv(standardDF, sumdata):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        level = setLevel(fullCriteria)
        errorcriteria = str(fullCriteria)
        errors[errorcriteria] = runyuvanalysis(standardDF, sumdata, fullCriteria, level)
    return errors


def runsatanalysis(standardDF, sumdata):
    criteria = "sat"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    extractSumData = sumdata.at[leveltoCheck, fullCriteria]
    extractStandDataBRNG = standardDF.at[criteria, "brnglimit"]
    extractStandDataClipping = standardDF.at[criteria, "clippinglimit"]
    extractStandDataIllegal = standardDF.at[criteria, "illegal"]
    if extractSumData <= extractStandDataBRNG:
        errors[fullCriteria] = {
            "Video Values": extractSumData,
            "Pass/Fail": "Pass"}
    else:
        if extractSumData >= extractStandDataIllegal:
            errors[fullCriteria] = {
                "Error Type": "Illegal",
                "Video Value": extractSumData,
                "Standard Value": extractStandDataIllegal,
                "Pass/Fail": "Fail"
            }
            # error = errortuple("illegal",fullCriteria, extractSumData, extractStandDataIllegal)
        else:
            errors[fullCriteria] = {
                "Error Type": "Clipping",
                "Video Value": extractSumData,
                "Standard Value": extractStandDataClipping,
                "Pass/Fail": "Fail"
            }
            # error = errortuple("clipping", fullCriteria, extractSumData,extractStandDataClipping)
    return errors


def runTOUTandVREPanalysis(standardDF, sumdata):
    criterium = ["tout", "vrep"]
    for criteria in criterium:
        level = "max"
        extractSumData = sumdata.at[level, criteria]
        extractStandDataMax = standardDF.at[criteria, level]
        errors = toutVREPcheck(extractSumData, extractStandDataMax, criteria)
    return errors


def toutVREPcheck(extractSumData, extractStandDataMax, criteria):
    if extractSumData >= extractStandDataMax:
        errors[criteria] = {
            "Error Type": "Exceeds Standard",
            "Video Value": extractSumData,
            "Standard Value": extractStandDataMax,
            "Pass/Fail":"Fail"
        }
    else:
        errors[criteria] = {"Video Value":extractSumData,"Pass/Fail":"Pass"}
    return errors

def runOverallVideo(standardDF, sumdata):
    errors.clear()
    runcheckyuv(standardDF, sumdata)
    runsatanalysis(standardDF, sumdata)
    runTOUTandVREPanalysis(standardDF, sumdata)
    # dict_list = [yuverrors, saterrors, toutVREPErrors]
    with open("sample.json", "w") as outfile:
        json.dump(errors, outfile, indent=4)
    # toutVREPErrors = runTOUTandVREPanalysis(standardDF, videoDSDF)


runOverallVideo(standardDF, sumdata)