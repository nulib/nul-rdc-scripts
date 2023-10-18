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
    "UHigh": 940,
    "UMax": 1023,
    "VMin": 0,
    "VLow": 64,
    "VAvg": 512,
    "VHigh": 940,
    "VMax": 1023,
    "SATMin": 0,
    "SATAvg": 362.04,
    "SATHigh": 512,
    "SATMax": 724.08,
    "TOUTMin": 0,
    "TOUTMax": 1,
    "VREPMin": 0,
    "VREPMax": 1,
    "BRNGMin": 0,
    "BRNGMax": 1,
}


def BRNGcheck(videodata, tenBitVideoValues):
    minBRNG = tenBitVideoValues["BRNGMin"]
    videominBRNG = videodata.at[4, "BRNG"]
    maxBRNG = tenBitVideoValues["BRNGMax"]
    videomaxBRNG = videodata.at[8, "BRNG"]
    if minBRNG > videominBRNG:
        criteria = "BRNG Min"
        description = "The video is out of the minimal broadcasting range"
        value = videominBRNG
        errortiers.tier1error(criteria, description, value)
    else:
        pass
    if maxBRNG < videomaxBRNG:
        criteria = "BRNG Max"
        description = "The video is out of the maximum broadcasting range"
        value = videomaxBRNG
        errortiers.tier1error(criteria, description, value)
    else:
        pass


def TOUTcheck(videodata, tenBitVideoValues):
    minTOUT = tenBitVideoValues["TOUTMin"]
    videominTOUT = videodata.at[4, "TOUT"]
    maxTOUT = tenBitVideoValues["TOUTMax"]
    videomaxTOUT = videodata.at[8, "TOUT"]
    if minTOUT > videominTOUT:
        criteria = "TOUTMin"
        description = "Your "
        value = videominTOUT
        errortiers.tier2error(criteria, description, value)
