import pandas as pd


def buildDF10Bit(csv10Bit):
    """Takes video values from 10bit csv and returns dataframe"""
    standardsDF = pd.read_csv(csv10Bit, sep=",", index_col="criteria")
    return standardsDF


def buildvideodata(videodata):
    """Takes the video data and reads the csv. Returns dataframe"""
    videodata = pd.read_csv(videodata, sep=",")
    return videodata


def setFullCriteria(criteria, level):
    """Combines the yuv and yuv level to give the full criteria that gets compared to standards."""
    criteriaFull = criteria + level
    return criteriaFull


def setOperatorIR(level):
    """Sets the operator to assess if video value is in range"""
    if level == "low":
        operatorIR = ">"
    elif level == "high":
        operatorIR = "<"
    return operatorIR


def setOperatorCL(level):
    """Sets operator to use to assess clipping"""
    if level == "low":
        operatorCL = "<="
    elif level == "high":
        operatorCL = ">="
    return operatorCL


def runyuvanalysis(level, videodata, standardsDF, criteriaFull):
    extractSumData = videodata.at(
        criteriaFull, level
    )  # grabs data from dataframe at this matrix intersection # NEED TO FIX
    extractStandDataBRNG = standardsDF.at(criteriaFull, "brngout")
    extractStandDataClipping = standardsDF.at(criteriaFull, "clipping")
    operatorIR = setOperatorIR(level)
    equationIR = extractSumData + operatorIR + extractStandDataBRNG
    tfIR = eval(equationIR)
    if tfIR:
        pass
    else:
        operatorCL = setOperatorCL(level)
        equationCL = extractSumData + operatorCL + extractStandDataClipping
        tfCL = eval(equationCL)
        if tfCL:
            error = {""}


def runsatanalysis(level, videodata, standardsDF, criteria):
    extractSumData = videodata.at()  # ADD
    extractStandDataBRNG = standardsDF.at(criteria, "brnglimit")
    extractStandDataClipping = standardsDF.at(criteria, "clippinglimit")
    extractStandDataIllegal = standardsDF.at(criteria, "illegal")
    if extractSumData <= extractStandDataBRNG:
        pass  # this would be a fine value
    else:
        if extractSumData >= extractStandDataIllegal:
            pass  # this would be an illegal value
        else:
            pass  # this would be a BRNGOut value


def runcheck(criteria, level, position, levelposition, videodata, standardsDF):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    criteria = ["y", "u", "v", "sat"]
    criteriaposition = 0
    level = ["low", "high"]
    levelposition = 0

    while position <= len(criteria):
        criteria = criteria[position]
        while levelposition <= len(level):
            level = level[levelposition]
            criteriaFull = setFullCriteria(criteria, level)
            if criteria == "sat":
                errors = runsatanalysis(
                    level, videodata, standardsDF, criteriaFull, criteria
                )
            else:
                errors = runyuvanalysis(level, videodata, standardsDF, criteriaFull)
            levelposition += 1
        criteriaposition += 1
