import pandas as pd
import json
from nulrdcscripts.vqc.multiuse import (
    setLeveltoCheck,
    setLevel,
    setOperatorCL,
    setOperatorIR,
)

videodata = "nulrdcscripts/vqc/ExampleVideoDataCSV.csv"
videodataDF = pd.read_csv(videodata, sep=",", index_col=0)
videodataDFLen = len(videodataDF)
standardcsv = "nulrdcscripts/vqc/Video10BitValues.csv"
standardDF = pd.read_csv(standardcsv, sep=",", index_col=0)
frameerrors = {}


def runyuvfbyfanalysis(standardDF, videodataDF, fullCriteria, level, frame):
    exVideoVal = videodataDF.at[frame, fullCriteria]
    exStandBRNG = standardDF.at[fullCriteria, "brngout"]
    exStandClipping = standardDF.at[fullCriteria, "clipping"]
    operatorIR = setOperatorIR(level)
    equationIR = str(exVideoVal) + operatorIR + str(exStandBRNG)
    tfIR = eval(equationIR)
    if tfIR:
        pass
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
            return errors
        else:
            errors = {
                "Error Type": "Out of Broadcast Range",
                "Video Value": exVideoVal,
                "Standard Value": "above " + str(exStandBRNG),
                "Pass/Fail": "Fail",
            }
            return errors


def runfbyfyuv(standardDF, videodataDF, frame):
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    errors = {}
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        level = setLevel(fullCriteria)
        errorCriteria = str(fullCriteria)
        errors[errorCriteria] = runyuvfbyfanalysis(
            standardDF, videodataDF, fullCriteria, level, frame
        )
    return errors


def runfbyfsat(standardDF, videodataDF, frame):
    errors = {}
    criteria = "sat"
    leveltoCheck = "max"
    fullCriteria = criteria + leveltoCheck
    exVideoVal = videodataDF.at(frame, fullCriteria)
    exBRNG = standardDF.at(fullCriteria, "brnglimit")
    exClipping = standardDF.at(fullCriteria, "clipping")
    exIllegal = standardDF.at(fullCriteria, "illegal")
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


def runTOUTandVREPanalysis(standardDF, videodataDF, frame):
    criterium = ["tout", "vrep"]
    for criteria in criterium:
        level = "max"
        exVideoVal = videodataDF.at[frame, criteria]
        exStandMax = standardDF.at[criteria, level]
        errors = runfbyfToutVrep(exVideoVal, exStandMax, criteria)
    return errors


def runfbyfToutVrep(exVideoVal, exStandMax, criteria):
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


def runfbyfanalysis(standardDF, videodataDF):
    frame = 1
    while frame <= videodataDFLen:
        frameerrors[frame] = runfbyfyuv(standardDF, videodataDF, frame)
        frameerrors[frame] = runfbyfsat(standardDF, videodataDF, frame)
        # frameerrors[frame] = runfbyfToutVrep (standardDF,videodataDF,frame)
        frame += 1
    return frameerrors


def makejson(frameerrors):
    with open("samplefbyf.json", "w") as outfile:
        json.dump(frameerrors, outfile, indent=4)


frameerrors = runfbyfanalysis(standardDF, videodataDF)
makejson(frameerrors)
