import pandas as pd
from argparser import args

videoerrors = {}


def checkAllVideo(videostats, videoBitDepth):
    MINsCheck(videostats, videoBitDepth)
    LOWsCheck(videostats, videoBitDepth)
    AVGsCheck(videostats, videoBitDepth)
    HIGHsCheck(videostats, videoBitDepth)
    MAXsCheck(videostats, videoBitDepth)

    def check(criteria, videostats, videoBitdepth):
        setcriteria = videoBitDepth.get[criteria]
        lowEnd = videostats.at[3, criteria]
        highEnd = videostats.at[8, criteria]
        if highEnd < setcriteria > lowEnd:
            values = [lowEnd, highEnd]
            videoerrors[criteria] = values
        else:
            pass
        return videoerrors

    def MINsCheck():
        criteriaprefix = ["Y", "U", "V", "SAT"]
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "MIN"
            check(criteria)
            i = i + 1

    def MAXsCheck():
        criteriaprefix = ["Y", "U", "V", "SAT", "BRNG", "VREP", "TOUT"]
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "MAX"
            check(criteria)
            i = i + 1

    def AVGsCheck():
        criteriaprefix = ["Y", "U", "V", "SAT"]
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "AVG"
            check(criteria)
            i = i + 1

    def LOWsCheck():
        criteriaprefix = ["Y", "U", "V", "SAT"]
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "LOW"
            check(criteria)
            i = i + 1

    def HIGHsCheck():
        criteriaprefix = ["Y", "U", "V", "SAT"]
        i = 0
        while i < len(criteriaprefix):
            criteria = criteriaprefix[i] + "HIGH"
            check(criteria)
            i = i + 1

    return videoerrors
