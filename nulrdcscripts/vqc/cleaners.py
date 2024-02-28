def criteriacleaner(criteria):
    criteriaclean1 = criteria.replace("lavfi.astats", "")
    criteriaclean2 = criteriaclean1.replace("lavfi.", "")
    criteriaclean3 = criteriaclean2.replace("signalstats.", "")
    criteriaclean4 = criteriaclean3.replace(".", " ")
    cleanedcriteria = criteriaclean4.replace("_", " ")
    cleanCriteria = cleanedcriteria.lower()
    return cleanCriteria


# Makes the criteria more legible so that it can be strung together later for a easy interpretation without relying on acronyms


def cleanCriteria(criteria):
    for i in criteria:
        if criteria.contains("MIN"):
            criteria = criteria.replace("MIN", "minimum")
        elif criteria.contains("LOW"):
            criteria = criteria.lower()
        elif criteria.contains("AVG"):
            criteria = criteria.replace("AVG", "average")
        elif criteria.contains("HIGH"):
            criteria = criteria.lower()
        elif criteria.contains("MAX"):
            criteria = criteria("maximum")

        if criteria.contains("Y"):
            criteria = criteria.replace("Y", "Y ")
        # U has to use the startswith method instead as otherwise it will replace the U in TOUT which is not wanted
        elif criteria.startswith("U"):
            criteria = criteria.replace("U", "U ")
        # V has to use the startswith method instead as otherwise it will replace the V in VREP which is not wanted
        elif criteria.startswith("V"):
            criteria = criteria.replace("V", "V ")
        elif criteria.contains("BRNG"):
            criteria = criteria.replace("BRNG", "Broadcasting Range ")
        elif criteria.contains("TOUT"):
            criteria = criteria.replace("TOUT", "Temporal Outliers ")
        elif criteria.contains("SAT"):
            criteria = criteria.replace("SAT", "Saturation")
        elif criteria.conains("VREP"):
            criteria = criteria.replace("VREP", "Vertical Line Repetitions")

    return criteria
