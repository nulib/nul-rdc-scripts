import nulrdcscripts.vqc.setup as setup
import pandas as pd
import json

# errortuple = namedtuple("Error", ["type", "criteria", "video value", "standard value"])
standardcsv = "nulrdcscripts/vqc/Video10BitValues.csv"
standardDF = pd.read_csv(standardcsv, sep=",",index_col=0)
videodata = "nulrdcscripts/vqc/testdata.csv"
sumdata = pd.read_csv(videodata,sep=",",index_col=0)

def setOperatorIR(level):
    """Sets the operator to assess if video value is in range"""
    if level == ("low"):
        operatorIR = ">"
    else:
        operatorIR = "<"
    return operatorIR


def setOperatorCL(level):
    """Sets operator to use to assess clipping"""
    if level == ("low"):
        operatorCL = "<="
    else:
        operatorCL = ">="
    return operatorCL

def setLevel(fullCriteria):
    boollevel = fullCriteria.endswith("high")
    if boollevel:
        level ="high"
    else:
        level = "low"
    return level


def setLeveltoCheck(level):
    if level == "high":
        leveltoCheck ="max"
    else:
        leveltoCheck ="min"
    return leveltoCheck

def runyuvanalysis(standardDF, sumdata, fullCriteria,level):
    leveltoCheck = setLeveltoCheck(level)
    extractSumData = sumdata.at[leveltoCheck, fullCriteria]
    extractStandDataBRNG = standardDF.at[fullCriteria, "brngout"]
    extractStandDataClipping = standardDF.at[fullCriteria, "clipping"]
    operatorIR = setOperatorIR(level)
    equationIR = str(extractSumData) + operatorIR + str(extractStandDataBRNG)
    tfIR = eval(equationIR)
    if tfIR:
        pass
    else:
        operatorCL = setOperatorCL(level)
        equationCL = str(extractSumData) + operatorCL + str(extractStandDataClipping)
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


def runcheckyuv(standardDF, sumdata):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    yuverrors = {}
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        level = setLevel(fullCriteria)
        errorcriteria=str(fullCriteria)
        yuverrors[errorcriteria]= runyuvanalysis(
            standardDF,sumdata,fullCriteria,level
        )
    return yuverrors


def runsatanalysis(standardDF, sumdata):
    criteria = "sat"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    extractSumData = sumdata.at[leveltoCheck, fullCriteria]
    extractStandDataBRNG = standardDF.at[criteria, "brnglimit"]
    extractStandDataClipping = standardDF.at[criteria, "clippinglimit"]
    extractStandDataIllegal = standardDF.at[criteria, "illegal"]
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


def runTOUTandVREPanalysis(standardDF, sumdata):
    criterium = ["tout", "vrep"]
    i=0
    while i<len(criterium):
        criteria = criterium[i]
        level = "max"
        extractSumData = sumdata.at[level, criteria]
        extractStandDataMax = standardDF.at[criteria, level]
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
        i+=1


def runOverallVideo(standardDF, sumdata):
    yuverrors = runcheckyuv(standardDF, sumdata)
    saterrors =runsatanalysis(standardDF,sumdata)
    toutVREPErrors = runTOUTandVREPanalysis(standardDF,sumdata)
    dict_list = [yuverrors,saterrors,toutVREPErrors]
    with open("sample.json","w") as outfile:
        json.dump(dict_list,outfile)
    # saterrors = runsatanalysis(standardDF, videoDSDF)
    # toutVREPErrors = runTOUTandVREPanalysis(standardDF, videoDSDF)


runOverallVideo(standardDF, sumdata)
