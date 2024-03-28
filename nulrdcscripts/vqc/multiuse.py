def setOperatorIR(level):
    """Sets the operator to assess if video value is in range"""
    if level == ("low"):
        operatorIR = ">"
    else:
        operatorIR = "<"
    return operatorIR


def setOperatorCL(level):
    """Sets operator to use to assess clipping"""
    if level == ("low"):
        operatorCL = "<="
    else:
        operatorCL = ">="
    return operatorCL


def setLevel(fullCriteria):
    boollevel = fullCriteria.endswith("high")
    if boollevel:
        level = "high"
    else:
        level = "low"
    return level


def setLeveltoCheck(level):
    if level == "high":
        leveltoCheck = "max"
    else:
        leveltoCheck = "min"
    return leveltoCheck
