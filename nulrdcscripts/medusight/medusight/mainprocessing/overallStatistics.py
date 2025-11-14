from collections import namedtuple

error = namedtuple("Error", ["criteria", "status", "video_value", "standard_value"])


def get_saturation_column(videoDSDF):
    """
    Determine which saturation column to use from descriptive statistics.
    
    Priority:
    1. 'sathigh' if available (QCTools - robust against headswitching)
    2. 'satmax' if sathigh not available (Direct extraction - clean due to cropping)
    
    Returns:
        str: 'sathigh' or 'satmax'
    """
    if 'sathigh' in videoDSDF.columns:
        return 'sathigh'
    elif 'satmax' in videoDSDF.columns:
        return 'satmax'
    else:
        raise ValueError("No saturation column found in video statistics")


def runyuvanalysis(videoDSDF, standardsDF, fullCriteria):
    """
    Analyze Y/U/V criteria against standards.
    
    Args:
        videoDSDF: DataFrame with video descriptive statistics (columns: ymin, ymax, etc.)
        standardsDF: DataFrame with standards (index: ymin, ymax, etc., column: brngout)
        fullCriteria: Criteria name like 'ymin', 'ymax', 'umin', etc.
    
    Returns:
        None if passing, list of error objects if failing
    """
    # Determine which row to use from descriptive stats
    stat_row = "min" if "min" in fullCriteria else "max"
    
    try:
        # Extract values directly - no mapping needed
        extractSumData = videoDSDF.at[stat_row, fullCriteria]
        extractStandDataBRNG = standardsDF.at[fullCriteria, "brngout"]
        
        # Clipping threshold (if available)
        try:
            extractStandDataClipping = standardsDF.at[fullCriteria, "clipping"]
        except:
            extractStandDataClipping = None
            
    except Exception as e:
        return [f"Data missing for {fullCriteria}: {e}"]

    # Broadcast range check
    # MIN criteria: video value must be > threshold (fail if <=)
    # MAX criteria: video value must be < threshold (fail if >=)
    if "min" in fullCriteria:
        tfIR = extractSumData > extractStandDataBRNG
    else:
        tfIR = extractSumData < extractStandDataBRNG

    if tfIR:
        # Passes broadcast range check
        return None
    else:
        # Failed broadcast range check
        # Check if it's clipping level failure (more severe)
        if extractStandDataClipping is not None:
            if "min" in fullCriteria:
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
        
        # Out of broadcast range but not clipping
        return [
            error(
                fullCriteria,
                "out_of_range",
                extractSumData,
                extractStandDataBRNG,
            )
        ]


def runcheckyuv(videoDSDF, standardsDF):
    """
    Runs the yuv checks by looping through each yuv value.
    
    Returns:
        List of error objects for failing criteria
    """
    criteria = ["y", "u", "v"]
    minmax = ["min", "max"]
    errorsYUV = []
    
    for fullCriteria in (f"{c}{mm}" for c in criteria for mm in minmax):
        result = runyuvanalysis(videoDSDF, standardsDF, fullCriteria)
        if result:
            errorsYUV.extend(result)
    
    return errorsYUV


def runsatanalysis(videoDSDF, standardsDF, error):
    """
    Analyze saturation against standards.
    
    Automatically detects whether to use 'sathigh' (QCTools) or 'satmax' (direct extraction).
    
    Args:
        videoDSDF: DataFrame with video descriptive statistics
        standardsDF: DataFrame with saturation standards
        error: The error namedtuple constructor
    
    Returns:
        List with one error object indicating saturation status, or empty list if passing
    """
    criteria = "sat"
    
    try:
        # Determine which saturation column to use
        sat_column = get_saturation_column(videoDSDF)
        print(f"DEBUG: Using saturation column for overall stats: {sat_column}")
        
        # Get max saturation value from video stats using the determined column
        extractSumData = videoDSDF.at["max", sat_column]
        
        # Get thresholds from standards - column names from your CSV
        extractStandDataBRNG = standardsDF.at[criteria, "brnglimit"]
        extractStandDataClipping = standardsDF.at[criteria, "clippinglimit"]
        extractStandDataIllegal = standardsDF.at[criteria, "illegal"]
    except Exception as e:
        return [f"Data missing for saturation analysis: {e}"]

    # Check saturation levels (from least to most severe)
    if extractSumData <= extractStandDataBRNG:
        # Passes - within broadcast range
        return []  # Return empty list for pass
    elif extractSumData > extractStandDataIllegal:
        # Most severe - illegal level
        status = "fail_illegal"
        return [error(sat_column, status, extractSumData, extractStandDataIllegal)]
    elif extractSumData > extractStandDataClipping:
        # Medium severity - clipping level
        status = "fail_clipping"
        return [error(sat_column, status, extractSumData, extractStandDataClipping)]
    else:
        # extractSumData > extractStandDataBRNG but <= extractStandDataClipping
        # Out of broadcast range but not clipping
        status = "fail_broadcast_range"
        return [error(sat_column, status, extractSumData, extractStandDataBRNG)]


def runstatsvideo(videoDSDF, standardsDF):
    """
    Runs all video statistics checks and returns errors.
    
    Returns:
        List of error objects for all failing criteria
    """
    errors = []
    
    # Check Y/U/V values
    errorsYUV = runcheckyuv(videoDSDF, standardsDF)
    if errorsYUV:
        errors.extend(errorsYUV)

    # Check saturation
    errorsSat = runsatanalysis(videoDSDF, standardsDF, error)
    if errorsSat:
        errors.extend(errorsSat)

    return errors