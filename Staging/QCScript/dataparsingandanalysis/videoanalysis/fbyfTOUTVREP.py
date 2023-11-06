def checkErrors (videoBitDepth):
    def checkTOUT (videoBitDepth):
        criteria = "TOUT"
        check(criteria)

    def check (criteria):
        criteriavalue = videoBitDepth.get(criteria["ideal"])
        selectColumns = "" + criteria + "," + "Frame Time" + ""
        subDF = subDF(selectColumns)
        idealCriteriaEquation = "" + criteria + "==" + criteriavalue + ""
        criteriaErrors = {}

        errors = subDF.query(idealCriteriaEquation)
        if subDF.empty:
            pass
        else:
            if criteria.contains ("ideal"):
                errortype = "VREP"
            elif criteria.contains ("")


    def subDF (videodata, selectColumns):
        subDF = videodata[[selectColumns]]
        return subDF
