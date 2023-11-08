levels = ["ideal", "MAX"]
criteria = ["TOUT", "VREP"]
level = 0
item = 0
def runCriteria (videoBitDepth, videodata):
    while item <= criteria:
        criteriaToCheck = criteria[item]
        runLevels(videoBitDepth, videodata, criteriaToCheck)
        item = item + 1

def runLevels (videoBitDepth,videodata, criteriaToCheck):
    while level <= levels:
        levelToCheck = levels[level]
        errors = setUpCheckErrors(criteria, levelToCheck, criteriaToCheck, videoBitDepth, videodata)
        level = level + 1
        return errors


def setUpCheckErrors (criteria, levelToCheck, criteriaToCheck, videoBitDepth, videodata):
    criteriaValue = videoBitDepth.get(criteria[levelToCheck])
    data = setColumn(videodata,criteriaToCheck)
    equationSign = setEquationSign(criteriaValue)
    Equation = setEquation(equationSign, criteria, criteriaValue)
    errorType = setErrorType(criteriaToCheck)
    checkErrors(Equation,data, errorType)

def checkErrors(Equation, data, errorType):
    errors = data.query(Equation)
    errors = assignETColumn(data,errorType)
    return errors


def setEquation(equationSign, criteriaValue, criteria):
    Equation = ""+criteria+equationSign+criteriaValue+""
    return Equation
   
def setEquationSign (criteriaValue):
    #Ideal Value
    if criteriaValue == 0:
        equationSign = "=="
    #Max Value
    elif criteriaValue > 0:
        equationSign = ">="
    return equationSign

def setColumn (criteriaToCheck, videodata):
    viewColumns = ""+criteriaToCheck+"Frame Time" + "Frame" + ""
    data = videodata(viewColumns)
    return data

def setErrorType (criteriaToCheck):
    errorType = criteriaToCheck
    return errorType

def assignETColumn (data, errorType):
    data = data.assign(ErrorType = errorType)
    return data