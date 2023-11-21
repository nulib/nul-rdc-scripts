import videovalues10Bit

levels = ["ideal", "max"]
criteria = ["tout", "vrep"]
level = 0
item = 0

videodata = "YHighData.csv"
videoBitDepth = videovalues10Bit


def runCriteria(videoBitDepth, videodata):
    while item <= criteria:
        criteriaToCheck = criteria[item]
        errors = runLevels(videoBitDepth, videodata, criteriaToCheck)
        item = item + 1
        print(errors)


def runLevels(videoBitDepth, videodata, criteriaToCheck):
    while level <= levels:
        levelToCheck = levels[level]
        errors = setUpCheckErrors(
            criteria, levelToCheck, criteriaToCheck, videoBitDepth, videodata
        )
        level = level + 1
        return errors


def setUpCheckErrors(criteria, levelToCheck, criteriaToCheck, videoBitDepth, videodata):
    criteriaValue = videoBitDepth.get(criteria[levelToCheck])
    data = setColumn(videodata, criteriaToCheck)
    equationSign = setEquationSign(criteriaValue)
    equation = setEquation(equationSign, criteria, criteriaValue)
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
