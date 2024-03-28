import pandas as pd
import json
from nulrdcscripts.vqc.multiuse import setLeveltoCheck,setLevel,setOperatorCL,setOperatorIR

videodata = "nulrdcscripts/vqc/ExampleVideoDataCSV.csv"
videodataDF = pd.read_csv(videodata, sep=',',index_col=0)
videodataDFLen = len(videodataDF)
standardcsv = "nulrdcscripts/vqc/Video10BitValues.csv"
standardDF = pd.read_csv(standardcsv, sep=',', index_col=0)
frameerrors = {}

def runyuvfbyfanalysis (standardDF,videodataDF, fullCriteria,level,frame):
    exVideoVal = videodataDF.at[frame, fullCriteria]
    exStandBRNG = standardDF.at[fullCriteria,"brngout"]
    exStandClipping = standardDF.at[fullCriteria,"clipping"]
    operatorIR = setOperatorIR(level)
    equationIR = str(exVideoVal) + operatorIR +str (exStandBRNG)
    tfIR = eval(equationIR)
    if tfIR:
            pass
    else:
        operatorCL = setOperatorCL(level)
        equationCL =str(exVideoVal) + operatorCL + str(exStandClipping)
        tfCL = eval(equationCL)
        if tfCL:
            errors = {
                "Error Type": "Clipping",
                "Video Value": exVideoVal,
                "Standard Value": "above " + str(exStandBRNG),
                "Pass/Fail" : "Fail"
            }
            return errors
        else:
            errors = {
                "Error Type": "Out of Broadcast Range",
                "Video Value": exVideoVal,
                "Standard Value": "above " + str(exStandBRNG),
                "Pass/Fail" : "Fail"
            }
            return errors
            

def runfbyfyuv(standardDF, videodataDF,frame):
    criteria = ["y","u","v"]
    levels = ["low","high"]
    errors={}
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        level = setLevel(fullCriteria)
        errorCriteria = str(fullCriteria)
        errors[errorCriteria] = runyuvfbyfanalysis(standardDF, videodataDF, fullCriteria,level,frame)
    return errors

def runfbyfsat(standardDF,videodataDF,frame):
    pass

def runfbyfToutVrep (standardDF, videodataDF,frame):
    pass

def runfbyfanalysis (standardDF,videodataDF):
    frame=1
    while frame <= videodataDFLen:
        frameerrors[frame] = runfbyfyuv(standardDF,videodataDF,frame)
        #frameerrors[frame] = runfbyfsat (standardDF,videodataDF,frame)
        #frameerrors[frame] = runfbyfToutVrep (standardDF,videodataDF,frame)
        frame +=1 
    return frameerrors

def makejson(frameerrors):
    with open("samplefbyf.json","w") as outfile :
        json.dump(frameerrors,outfile,indent=4)

frameerrors=runfbyfanalysis(standardDF,videodataDF)
makejson(frameerrors)