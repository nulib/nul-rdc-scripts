import pandas as pd
from tabulate import tabulate
from nulrdcscripts.vqc import setup
from nulrdcscripts.vqc.multiuse import (
    setLevel,
    setOperatorCL,
    setOperatorIR,
)

frameerrors = {}
videodata = "nulrdcscripts/vqc/testdata.csv"
standard = 8

standardDF = setup.setVideoBitDepth(standard)
csvDF = pd.read_csv(videodata)


def runyuvfbyfanalysis(standardDF, csvDF, fullCriteria, level, frame):
    exVideoVal = csvDF.at[frame, fullCriteria]
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


def runfbyfyuv(standardDF, csvDF, frame):
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    errors = {}
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        level = setLevel(fullCriteria)
        errorCriteria = str(fullCriteria)
        errors[errorCriteria] = runyuvfbyfanalysis(
            standardDF, csvDF, fullCriteria, level, frame
        )
    return errors


def runfbyfsat(standardDF, csvDF, frame):
    errors = {}
    criteria = "sat"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    exVideoVal = csvDF.at[frame, fullCriteria]
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


def runTOUTandVREPanalysis(standardDF, csvDF, frame):
    criteria = ["tout", "vrep"]
    for c in criteria:
        level = "max"
        exVideoVal = csvDF.at[frame, c]
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


def runfbyfanalysis(standardDF, csvDF):
    frameerrors.clear()
    frame = 1
    videodataDFlen = len(csvDF)
    while frame <= (videodataDFlen - 1):
        errors = runfbyfyuv(standardDF, csvDF, frame)
        errorsSat = runfbyfsat(standardDF, csvDF, frame)
        errorsTOUTVREP = runTOUTandVREPanalysis(standardDF, csvDF, frame)
        frameerrors[frame] = joindict(errors, errorsSat, errorsTOUTVREP)
        frame += 1
    return frameerrors


def dictodftojson(frameerrors):

    df = pd.DataFrame.from_dict(frameerrors, orient="index")
    print(tabulate(df))


frameerrors = runfbyfanalysis(standardDF, csvDF)
dictodftojson(frameerrors)
