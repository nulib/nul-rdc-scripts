import json
tier1errors = ["SAT", "VREP", "BRNG"]
tier2errors = [""]
def errorsvideo (summaryvideoerrors):
    if summaryvideoerrors.contains(tier1errors):
        pass









failstier1 = {}
failstier2 = {}
failstier3 = {}
videoreportbycriteria = [failstier1, failstier2, failstier3]
# A fail for tier one is a critical failure and should be top priority for assessment

def tier1error (criteria, description, value):
    failstier1 = {criteria[value, description]}
    return failstier1

# A fail for tier two is a moderate failure, requires attention but is not as severe as a tier one

def tier2error(criteria, description, value):
    failstier2 = {criteria[value, description]}
    return failstier2

# A fail for tier three is a mild error that is of the lowest priority for assessment, but should still be assessed

def tier3error (criteria, description, value):
    failstier3 = {criteria[value, description]}
    return failstier3


def assignVideoSummaryTiers (failstier1,failstier2,failstier3):
    if failstier1: 
        videosummaryreport = "Error Rank: Critical - High priority for assessment"
    elif failstier2:
        videosummaryreport = "Error Rank: Moderate - Mid-level priority for assessment"
    elif failstier3:
        videosummaryreport = "Error Rank: Mild - Lowest priority for assessment"
    else:
        videosummaryreport = "Cleared Automated QC"
    return videosummaryreport







# These results will now be pooled into a JSON file that will list the ranking of videos criterias as well as an overall score.