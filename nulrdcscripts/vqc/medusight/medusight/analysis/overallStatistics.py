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
        standardsDF: DataFrame with standards (index: ylow, yhigh, etc., column: brngout)
        fullCriteria: Criteria name like 'ylow', 'yhigh', 'ulow', etc.
    
    Returns:
        None if passing, list of error objects if failing
    """
    # Map criteria to videoDSDF column names
    # ylow -> ymin, yhigh -> ymax, etc.
    if "low" in fullCriteria:
        stat_row = "min"
        videodata_column = fullCriteria.replace('low', 'min')
    else:
        stat_row = "max"
        videodata_column = fullCriteria.replace('high', 'max')
    
    try:
        # Extract the value from the descriptive stats DataFrame
        # Use the mapped column name (ymin, ymax, etc.)
        extractSumData = videoDSDF.at[stat_row, videodata_column]
        extractStandDataBRNG = standardsDF.at[fullCriteria, "brngout"]
        
        # Clipping threshold (if available)
        try:
            extractStandDataClipping = standardsDF.at[fullCriteria, "clipping"]
        except:
            extractStandDataClipping = None
            
    except Exception as e:
        return [f"Data missing for {fullCriteria}: {e}"]

    # Broadcast range check
    # LOW criteria: video value must be > threshold (fail if <=)
    # HIGH criteria: video value must be < threshold (fail if >=)
    if "low" in fullCriteria:
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
            if "low" in fullCriteria:
                tfCL = extractSumData <= extractStandDataClipping
            else:
                tfCL = extractSumData >= extractStandDataClipping
            
            if tfCL:
                return [
                    error(
                        videodata_column,  # Use ymin/ymax instead of ylow/yhigh
                        "clipping",
                        extractSumData,
                        extractStandDataClipping,
                    )
                ]
        
        # Out of broadcast range but not clipping
        return [
            error(
                videodata_column,  # Use ymin/ymax instead of ylow/yhigh
                "out_of_range",
                extractSumData,
                extractStandDataBRNG,
            )
        ]


def runcheckyuv(videoDSDF, standardsDF):
    """
    Runs the yuv checks by looping through each yuv value and level.
    
    Returns:
        List of error objects for failing criteria
    """
    criteria = ["y", "u", "v"]
    levels = ["low", "high"]
    errorsYUV = []
    
    for fullCriteria in (f"{c}{l}" for c in criteria for l in levels):
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
        List with one error object indicating saturation status
    """
    criteria = "sat"
    
    try:
        # Determine which saturation column to use
        sat_column = get_saturation_column(videoDSDF)
        print(f"DEBUG: Using saturation column for overall stats: {sat_column}")
        
        # Get max saturation value from video stats using the determined column
        extractSumData = videoDSDF.at["max", sat_column]
        
        # Get thresholds from standards - use correct column names from CSV
        extractStandDataBRNG = standardsDF.at[criteria, "brnglimit"]
        extractStandDataClipping = standardsDF.at[criteria, "clippinglimit"]
        extractStandDataIllegal = standardsDF.at[criteria, "illegal"]
    except Exception as e:
        return [f"Data missing for saturation analysis: {e}"]

    # Check saturation levels (from least to most severe)
    if extractSumData <= extractStandDataBRNG:
        # Passes - within broadcast range
        status = "pass"
        return [error(sat_column, status, extractSumData, extractStandDataBRNG)]
    elif extractSumData > extractStandDataIllegal:
        # Most severe - illegal level
        status = "fail"
        return [error(sat_column, status, extractSumData, extractStandDataIllegal)]
    elif extractSumData > extractStandDataClipping:
        # Medium severity - clipping level
        status = "fail"
        return [error(sat_column, status, extractSumData, extractStandDataClipping)]
    else:
        # extractSumData > extractStandDataBRNG but <= extractStandDataClipping
        # Out of broadcast range but not clipping
        status = "fail"
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


def get_passing_stats(all_criteria, errors, videoDSDF, standardDF):
    """
    Generate statistics text for criteria that passed.
    
    Args:
        all_criteria: List of all criteria names (ylow, yhigh, etc.)
        errors: List of error objects (with criteria like ymin, ymax, etc.)
        videoDSDF: Video descriptive statistics
        standardDF: Standards dataframe
    
    Returns:
        Formatted string with passing criteria stats
    """
    # Extract error criteria - these are now ymin, ymax, etc.
    error_criteria = set()
    for err in errors:
        if not isinstance(err, str) and hasattr(err, 'criteria'):
            # Map back to ylow/yhigh format for comparison with all_criteria
            crit = err.criteria
            if 'min' in crit:
                error_criteria.add(crit.replace('min', 'low'))
            elif 'max' in crit:
                error_criteria.add(crit.replace('max', 'high'))
            else:
                error_criteria.add(crit)
    
    passing = [c for c in all_criteria if c not in error_criteria]

    passing_lines = []
    for crit in passing:
        # Map criteria to videoDSDF column names
        if "low" in crit:
            stat_row = "min"
            videodata_column = crit.replace('low', 'min')
        elif "high" in crit:
            stat_row = "max"
            videodata_column = crit.replace('high', 'max')
        else:
            continue
        
        try:
            video_value = videoDSDF.at[stat_row, videodata_column]
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