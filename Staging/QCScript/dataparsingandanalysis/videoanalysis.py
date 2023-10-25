import pandas as pd
import errortiers

tenBitVideoValues = {
    "YMin": 0,
    "YLow": 64,
    "YAvg": 512,
    "YHigh": 940,
    "YMax": 1023,
    "UMin": 0,
    "ULow": 64,
    "UAvg": 512,
    "UHigh": 960,
    "UMax": 1023,
    "VMin": 0,
    "VLow": 64,
    "VAvg": 512,
    "VHigh": 960,
    "VMax": 1023,
    "SATMin": 0,
    "SATAvg": 362.04,
    "SATHigh": 512,
    "SATMax": 724.08,
    "TOUTMax": 0.009,
    "VREPMax": 0.03,
    "BRNGMax": 1
}


def videoanalyzer(videodata):
    BRNGcheck(videodata, tenBitVideoValues)
    TOUTcheck(videodata, tenBitVideoValues)
    VREPcheck(videodata, tenBitVideoValues)
    SATMincheck(videodata, tenBitVideoValues)
    SATLowcheck(videodata, tenBitVideoValues)
    SATAvgcheck(videodata, tenBitVideoValues)

def BRNGcheck(videodata, tenBitVideoValues):
    maxBRNG = tenBitVideoValues["BRNGMax"]
    videomaxBRNG = videodata.at[8, "BRNG"]
    if maxBRNG < videomaxBRNG:
        criteria = "BRNG Max"
        description = "The video is out of the maximum broadcasting range (0-1)"
        value = videomaxBRNG
        errortiers.tier1error(criteria, description, value)
    else:
        pass

def SATMincheck(videodata, tenBitVideoValues):
    minSAT = tenBitVideoValues.get("SATMin")
    videominSAT = videodata.at[3,"SATMin"]
    if minSAT > videominSAT:
        criteria = "SATMin"
        description = "Your Saturation Minimum is not within the suggested range"
        value = videominSAT
        errortiers.tier1error(criteria,value,description)
    else:
        pass

def SATLowcheck(videodata, tenBitVideoValues):
    lowSAT = tenBitVideoValues.get("SATLow")
    videolowSAT = videodata.at[4, "SATLow"]
    if lowSAT > videolowSAT:
        criteria = "SATLow"
        description = "Your Saturation Low is not within the suggested range"
        value = videolowSAT
        errortiers.tier1error(criteria,description,value)
    else:
        pass

def SATAvgcheck (videodata, tenBitVideoValues):
    avgSAT = tenBitVideoValues.get("SATAvg")
    videoavgSAT = videodata.at[5, "SATAvg"]
    if avgSAT > videoavgSAT:
        criteria = "SATAvg"
        description = "Your Saturation Average is not within the suggested range"
        value = videoavgSAT
        errortiers.tier1error(criteria,description,value)
    else:
        pass

def SATHighcheck (videodata, tenBitVideoValues):
    highSAT = tenBitVideoValues.get("SATHigh")
    videohighSAT = videodata.at[5, "SATAvg"]
    if highSAT < videohighSAT:
        criteria = "SATHigh"
        value = videohighSAT
        description = "Your Saturation High is not within the suggested range"
        errortiers.failstier1(criteria, value, description)
    else: 
        pass
def TOUTcheck(videodata, tenBitVideoValues):
    maxTOUT = tenBitVideoValues.get("TOUTMax")
    videomaxTOUT = videodata.at[8, "TOUT"]
    if maxTOUT < videomaxTOUT:
        criteria = "TOUTMax"
        description = "Your TOUT maximum is higher than the suggested range (0-0.009)"
        value = videomaxTOUT
        errortiers.tier2error(criteria, value, description)
    else:
        pass


def VREPcheck(videodata, tenBitVideoValues):
    maxVREP = tenBitVideoValues.get("VREPMax")
    videomaxVREP = videodata.at[8, "VREP"]
    if maxVREP < videomaxVREP:
        criteria = "VREPMax"
        value = videomaxVREP
        description = "Your VREP maximum is outside of the suggested range (0-0.03)"
        errortiers.tier2error(criteria, value, description)
    else:
        pass
