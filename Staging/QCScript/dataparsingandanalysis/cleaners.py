def tagkeycleaning(tagkey):
    tagkeyclean1 = tagkey.replace("lavfi.astats", "")
    tagkeyclean2 = tagkeyclean1.replace("lavfi.", "")
    tagkeyclean3 = tagkeyclean2.replace("signalstats.", "")
    tagkeyclean4 = tagkeyclean3.replace(".", " ")
    cleanedtagkey = tagkeyclean4.replace("_", " ")
    return cleanedtagkey

# Makes the criteria more legible so that it can be strung together later for a easy interpretation without relying on acronyms

def cleanCriteria (errorintake):
    for criteria in errorintake:
        if criteria.contains("MIN"):
            criteria = criteria.replace ("MIN", "minimum")
        elif criteria.contains ("LOW"):
            criteria = criteria.lower()
        elif criteria.contains ("AVG"):
            criteria = criteria.replace ("AVG", "average")
        elif criteria.contains ("HIGH"):
            criteria = criteria.lower()
        elif criteria.contains ("MAX"):
            criteria = criteria ("maximum")

        if criteria.contains ("Y"):
            criteria = criteria.replace("Y", "Y ")
        # U has to use the startswith method instead as otherwise it will replace the U in TOUT which is not wanted
        elif criteria.startswith ("U"):
            criteria = criteria.replace("U", "U ")
        elif criteria.contains ("V"):
            criteria = criteria.replace("V", "V ")
        elif criteria.contains ("BRNG"):
            criteria = criteria.replace ("BRNG", "Broadcasting Range ")
        elif criteria.contains ("TOUT"):
            criteria= criteria.replace ("TOUT", "Temporal Outliers ")
        elif criteria.contains ("SAT"):
            criteria = criteria.replace("SAT", "Saturation")
    return criteria