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
    "BRNGMax": 1,
}


def videoanalyzer(videodata):
    BRNGcheck(videodata, tenBitVideoValues)
    TOUTcheck(videodata, tenBitVideoValues)
    VREPcheck(videodata, tenBitVideoValues)


def BRNGcheck(videodata, tenBitVideoValues):
    maxBRNG = tenBitVideoValues["BRNGMax"]
    videomaxBRNG = videodata.at[8, "BRNG"]
    if maxBRNG < videomaxBRNG:
        criteria = "BRNG Max"
        description = "The video is out of the maximum broadcasting range"
        value = videomaxBRNG
        errortiers.tier1error(criteria, description, value)
    else:
        pass


def TOUTcheck(videodata, tenBitVideoValues):
    maxTOUT = tenBitVideoValues["TOUTMax"]
    videomaxTOUT = videodata.at[8, "TOUT"]
    if maxTOUT < videomaxTOUT:
        criteria = "TOUTMax"
        description = "Your TOUT maximum is higher than the suggested range"
        value = videomaxTOUT
        errortiers.tier2error(criteria, value, description)
    else:
        pass


def VREPcheck(videodata, tenBitVideoValues):
    maxVREP = tenBitVideoValues["VREPMax"]
    videomaxVREP = videodata.at[8, "VREP"]
    if maxVREP < videomaxVREP:
        criteria = "VREPMax"
        value = videomaxVREP
        description = "Your VREP maximum is outside of the suggested range"
        errortiers.tier2error(criteria, value, description)
    else:
        pass
