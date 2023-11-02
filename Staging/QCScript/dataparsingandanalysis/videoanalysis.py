import pandas as pd
from argparser import args
from data.videovalues10Bit import tenBitVideoValues
from data.videovalues8Bit import eightBitVideoValues

videobitdepth = args.videobitdepth
videoerrors = {}
def checkAllVideo (videostats, videobitdepth):
    if videobitdepth == "--10bit" or videobitdepth == "-10":
        standardvalues = tenBitVideoValues
    elif videobitdepth == "--8bit" or videobitdepth == "-8":
        standardvalues = eightBitVideoValues

    MINsCheck(videostats, standardvalues)
    LOWsCheck(videostats, standardvalues)
    AVGsCheck(videostats, standardvalues)
    HIGHsCheck(videostats, standardvalues)
    MAXsCheck(videostats, standardvalues)

    def check (criteria, videostats, standardvalues):
        setcriteria = standardvalues.get[criteria]
        lowEnd = videostats.at[3, criteria]
        highEnd = videostats.at[8, criteria]
        if highEnd < setcriteria > lowEnd:
            values = [lowEnd, highEnd]
            videoerrors[criteria] = values
        else:
            pass
        return videoerrors

    def MINsCheck ():
        criteriaprefix = ['Y', 'U', 'V', 'SAT']
        i = 0 
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "MIN"
            check(criteria)
            i = i + 1
        
    def MAXsCheck ():
        criteriaprefix = ['Y', 'U', 'V', 'SAT', 'BRNG', 'VREP', 'TOUT']
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "MAX"
            check(criteria)
            i = i + 1

    def AVGsCheck ():
        criteriaprefix = ['Y', 'U', 'V', 'SAT']
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "AVG"
            check(criteria)
            i = i + 1

    def LOWsCheck ():
        criteriaprefix = ['Y', 'U', 'V', 'SAT']
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "LOW"
            check(criteria)
            i = i + 1

    def HIGHsCheck ():
        criteriaprefix = ['Y', 'U', 'V', 'SAT']
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "HIGH"
            check(criteria)
            i = i + 1
    
    return videoerrors