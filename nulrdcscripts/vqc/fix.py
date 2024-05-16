import pandas as pd
from nulrdcscripts.vqc.multiuse import (
    setLevel,
    setOperatorCL,
    setOperatorIR,
)

frameerrors = {}
videodata = "videodata.csv"
standardDF = "Video8BitValues.csv"

def runyuvfbyfanalysis(standardDF, videodata, fullCriteria, level, frame):
    exVideoVal = videodata.at[frame, fullCriteria]
    exStandBRNG = standardDF.at[fullCriteria, "brngout"]
    exStandClipping = standardDF.at[fullCriteria, "clipping"]
    operatorIR = setOperatorIR(level)
    equationIR = str(exVideoVal) + operatorIR + str(exStandBRNG)
    tfIR = eval(equationIR)
    if tfIR:
        errors = {"Video Value": exVideoVal, "Pass/Fail": "Pass"}
    else:
        operatorCL = setOperatorCL(level)
        equationCL = str(exVideoVal) + operatorCL + str(exStandClipping)
        tfCL = eval(equationCL)
        if tfCL:
            errors = {
                "Error Type": "Clipping",
                "Video Value": exVideoVal,
                "Standard Value": "above " + str(exStandBRNG),
                "Pass/Fail": "Fail",
            }
        else:
            errors = {
                "Error Type": "Out of Broadcast Range",
                "Video Value": exVideoVal,
                "Standard Value": "above " + str(exStandBRNG),
                "Pass/Fail": "Fail",
            }
    return errors


def runfbyfyuv(standardDF, videodata, frame):
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    errors = {}
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        level = setLevel(fullCriteria)
        errorCriteria = str(fullCriteria)
        errors[errorCriteria] = runyuvfbyfanalysis(
            standardDF, videodata, fullCriteria, level, frame
        )
    return errors


def runfbyfsat(standardDF, videodata, frame):
    errors = {}
    criteria = "sat"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    exVideoVal = videodata.at[frame, fullCriteria]
    exBRNG = standardDF.at[criteria, "brnglimit"]
    exClipping = standardDF.at[criteria, "clippinglimit"]
    exIllegal = standardDF.at[criteria, "illegal"]
    if exVideoVal <= exBRNG:
        errors[fullCriteria] = {"Video Values": exVideoVal, "Pass/Fail": "Pass"}
    else:
        if exVideoVal >= exIllegal:
            errors[fullCriteria] = {
                "Error Type": "Illegal",
                "Video Value": exVideoVal,
                "Standard Value": exIllegal,
                "Pass/Fail": "Fail",
            }
            # error = errortuple("illegal",fullCriteria, extractSumData, extractStandDataIllegal)
        else:
            errors[fullCriteria] = {
                "Error Type": "Clipping",
                "Video Value": exVideoVal,
                "Standard Value": exClipping,
                "Pass/Fail": "Fail",
            }
            # error = errortuple("clipping", fullCriteria, extractSumData,extractStandDataClipping)
    return errors


def runTOUTandVREPanalysis(standardDF, videodata, frame):
    criteria = ["tout", "vrep"]
    for c in criteria:
        level = "max"
        exVideoVal = videodata.at[frame, c]
        exStandMax = standardDF.at[c, level]
        errors = runfbyfToutVrep(exStandMax, exVideoVal, c)
    return errors


def runfbyfToutVrep(exStandMax, exVideoVal, criteria):
    errors = {}
    if exVideoVal >= exStandMax:
        errors[criteria] = {
            "Error Type": "Exceeds Standard",
            "Video Value": exVideoVal,
            "Standard Value": exStandMax,
            "Pass/Fail": "Fail",
        }
    else:
        errors[criteria] = {"Video Value": exVideoVal, "Pass/Fail": "Pass"}
    return errors


def joindict(errors, errorsSat, errorsTOUTVREP):
    errors.update(errorsSat)
    errors.update(errorsTOUTVREP)
    return errors


def runfbyfanalysis(standardDF, videodata):
    frame = 1
    videodataDFlen = len(videodata)
    while frame <= (videodataDFlen - 1):
        errors = runfbyfyuv(standardDF, videodata, frame)
        errorsSat = runfbyfsat(standardDF, videodata, frame)
        errorsTOUTVREP = runTOUTandVREPanalysis(standardDF, videodata, frame)
        frameerrors[frame] = joindict(errors, errorsSat, errorsTOUTVREP)
        frame += 1
    return frameerrors


def dictodftojson(frameerrors):
    
frameerrorsDF = pd.DataFrame.from_dict(frameerrors)

framefails = frameerrorsDF[frameerrorsDF["Pass/Fail"] == "Fail"]
jsonframefails = framefails.to_json("samplefbyf.json", orient="table")
return jsonframefails
