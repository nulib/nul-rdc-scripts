def lossless_check(input_metadata, output_metadata, streamMD5status):
    if output_metadata.get("output_techMetaA") == input_metadata.get("input_techMetaV"):
        QC_techMeta = "PASS"
    else:
        print("input and output technical metadata do not match")
        QC_techMeta = "FAIL"

    losslessCheckDict = {
        "technical metadata": QC_techMeta,
        "stream checksums": streamMD5status,
    }
    if "FAIL" in losslessCheckDict.values():
        losslessCheck = "FAIL"
        losslessFail = []
        for key in losslessCheckDict.keys():
            if "FAIL" in losslessCheckDict.get(key):
                losslessFail.append(key)
                losslessCheck = losslessCheck + ": " + str(losslessFail).strip("[]")
            else:
                lossless_check = "PASS"
            return lossless_check
