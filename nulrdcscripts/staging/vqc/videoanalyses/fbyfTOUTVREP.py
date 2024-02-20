import pandas as pd

levels = ["ideal", "max"]
criteria = ["tout", "vrep"]
level = 0
item = 0

videodata = "YHighData.csv"


def runCriteria(videoBitDepth, videodata):
    while item <= len(criteria):
        criteriaToCheck = criteria[item]
        errors = runLevels(videoBitDepth, videodata, criteriaToCheck)
        item = item + 1
        print(errors)


def runLevels(videoBitDepth, videodata, criteriaToCheck):
    while level <= len(levels):
        levelToCheck = levels[level]
        errors = setUpCheckErrors(
            levelToCheck, criteriaToCheck, videoBitDepth, videodata
        )
        level = level + 1
        return errors


def setUpCheckErrors(levelToCheck, criteriaToCheck, videoBitDepth, videodata):
    criteriaValue = videoBitDepth.at[criteriaToCheck, levelToCheck]
    criteria = criteriaToCheck + levelToCheck
    data = setColumn(videodata, criteriaToCheck)
    equationSign = setEquationSign(criteriaValue)
    equation = setEquation(equationSign, criteriaToCheck, criteriaValue)
    errorType = setErrorType(criteriaToCheck)
    errors = checkErrors(equation, data, errorType)
    return errors


def checkErrors(Equation, data, errorType):
    errors = data.query(Equation)
    errors = assignETColumn(data, errorType)
    print(errors)
    return errors


def setEquation(equationSign, criteriaValue, criteria):
    equation = "" + criteria + equationSign + criteriaValue + ""
    return equation


def setEquationSign(criteriaValue):
    # Ideal Value
    if criteriaValue == 0:
        equationSign = "=="
    # Max Value
    elif criteriaValue > 0:
        equationSign = ">="
    return equationSign


def setColumn(criteriaToCheck, videodata):
    viewColumns = "" + criteriaToCheck + "Frame Time" + "Frame" + ""
    data = videodata(viewColumns)
    return data


def setErrorType(criteriaToCheck):
    errorType = criteriaToCheck
    return errorType


def assignETColumn(data, errorType):
    data = data.assign(ErrorType=errorType)
    return data
