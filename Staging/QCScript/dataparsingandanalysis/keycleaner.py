def tagkeycleaning(tagkey):
    tagkeyclean1 = tagkey.replace("lavfi.astats", "")
    tagkeyclean2 = tagkeyclean1.replace("lavfi.", "")
    tagkeyclean3 = tagkeyclean2.replace("signalstats.", "")
    tagkeyclean4 = tagkeyclean3.replace(".", " ")
    cleanedtagkey = tagkeyclean4.replace("_", " ")
    return cleanedtagkey
