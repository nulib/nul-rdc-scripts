from collections import namedtuple

error = namedtuple("Error", ["criteria", "status", "video_value", "standard_value"])


def setOperatorIR(fullCriteria):
    """Sets the operator to assess if video value is in range"""
    if fullCriteria.endswith("low"):
        return ">"
    else:
        return "<"


def setOperatorCL(fullCriteria):
    """Sets operator to use to assess clipping"""
    if fullCriteria.endswith("min"):
        return "<="
    else:
        return ">="


def runyuvanalysis(videoDSDF, standardsDF, fullCriteria):
    # Determine which row to use
    if "low" in fullCriteria:
        stat_row = "min"
    else:
        stat_row = "max"
    try:
        # Extract the value from the descriptive stats DataFrame
        extractSumData = videoDSDF.at[stat_row, fullCriteria]
        extractStandDataBRNG = standardsDF.at[fullCriteria, "brngout"]
        extractStandDataClipping = standardsDF.at[fullCriteria, "clipping"]
    except Exception as e:
        return [f"Data missing for {fullCriteria}: {e}"]

    # In range check
    if "low" in fullCriteria:
        tfIR = extractSumData > extractStandDataBRNG
    else:
        tfIR = extractSumData < extractStandDataBRNG

    if tfIR:
        return None
    else:
        # Clipping check
        if "low" in fullCriteria:
            tfCL = extractSumData <= extractStandDataClipping
        else:
            tfCL = extractSumData >= extractStandDataClipping
        if tfCL:
            return [
                error(
                    fullCriteria,
                    "clipping",
                    extractSumData,
                    extractStandDataClipping,
                )
            ]
        else:
            return [
                error(
                    fullCriteria,
                    "out_of_range",
                    extractSumData,
                    extractStandDataBRNG,
                )
            ]


def runcheckyuv(videoDSDF, standardsDF):
    """Runs the yuvchecks by looping through each yuv value and then the level that is being checked. Returns errors."""
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    errorsYUV = []
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
        result = runyuvanalysis(videoDSDF, standardsDF, fullCriteria)
        if result:
            errorsYUV.extend(result)
    return errorsYUV


def runsatanalysis(videoDSDF, standardsDF, error):
    criteria = "sat"
    leveltoCheck = "high"
    fullCriteria = criteria + leveltoCheck
    try:
        extractSumData = videoDSDF.at[leveltoCheck, fullCriteria]
        extractStandDataBRNG = standardsDF.at[criteria, "brnglimit"]
        extractStandDataClipping = standardsDF.at[criteria, "clippinglimit"]
        extractStandDataIllegal = standardsDF.at[criteria, "illegal"]
    except Exception as e:
        return [f"Data missing for {fullCriteria}: {e}"]

    if extractSumData <= extractStandDataBRNG:
        status = "pass"
        return [error(fullCriteria, status, extractSumData, extractStandDataBRNG)]
    elif extractSumData >= extractStandDataIllegal:
        status = "fail"
        return [error(fullCriteria, status, extractSumData, extractStandDataIllegal)]
    else:
        status = "fail"
        return [error(fullCriteria, status, extractSumData, extractStandDataClipping)]


def runstatsvideo(videoDSDF, standardsDF):
    """Runs the video statistics checks and returns errors."""
    errors = []
    errorsYUV = runcheckyuv(videoDSDF, standardsDF)
    if errorsYUV:
        errors.extend(errorsYUV)

    errorsSat = runsatanalysis(videoDSDF, standardsDF, error)
    if errorsSat:
        errors.extend(errorsSat)

    return errors


def get_passing_stats(all_criteria, errors, videoDSDF, standardDF):
    error_criteria = set()
    for err in errors:
        if not isinstance(err, str):
            error_criteria.add(err.criteria)
    passing = [c for c in all_criteria if c not in error_criteria]

    passing_lines = []
    for crit in passing:
        # Determine which row to use
        stat_row = "min" if "low" in crit else "max"
        try:
            video_value = videoDSDF.at[stat_row, crit]
        except Exception:
            video_value = "N/A"
        try:
            standard_value = standardDF.at[crit, "brngout"]
        except Exception:
            standard_value = "N/A"
        passing_lines.append(
            f"Criteria: {crit}\n"
            f"  Video Value: {video_value}\n"
            f"  Standard Value: {standard_value}\n"
        )
    return "\n".join(passing_lines) if passing_lines else "None"


def get_threshold(crit, col, standardDF):
    # If crit is 'satmax', use 'sat' thresholds
    if crit == "sathigh":
        crit = "sat"
    try:
        return standardDF.at[crit, col]
    except Exception:
        return None

    if crit in ("sat", "satmax"):
        brng = get_threshold(crit, "brnglimit", standardDF)
        clipping = get_threshold(crit, "clippinglimit", standardDF)
        illegal = get_threshold(crit, "illegal", standardDF)
        # ...rest of your logic...
