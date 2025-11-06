import datetime


def format_seconds_to_hms(seconds):
    """
    Format seconds to HH:MM:SS.mmm format with milliseconds.
    
    Args:
        seconds: Time in seconds (can be float with fractional seconds)
    
    Returns:
        Formatted string like "00:01:23.456"
    """
    try:
        # Separate whole seconds and fractional part
        total_seconds = float(seconds)
        whole_seconds = int(total_seconds)
        milliseconds = int((total_seconds - whole_seconds) * 1000)
        
        # Convert to timedelta for HH:MM:SS formatting
        td = datetime.timedelta(seconds=whole_seconds)
        
        # Format as HH:MM:SS.mmm
        return f"{str(td)}.{milliseconds:03d}"
    except Exception:
        return str(seconds)


def get_saturation_column(videodata):
    """
    Determine which saturation column to use.
    
    Priority:
    1. 'sathigh' if available (QCTools - robust against headswitching)
    2. 'satmax' if sathigh not available (Direct extraction - clean due to cropping)
    
    Returns:
        str: 'sathigh' or 'satmax'
    """
    if 'sathigh' in videodata.columns:
        return 'sathigh'
    elif 'satmax' in videodata.columns:
        return 'satmax'
    else:
        raise ValueError("No saturation column found in data")


def get_failing_frametimes(errors, videodata, standardDF):
    """
    Returns:
      - A string listing failing frame times for each failing criteria.
      - A dict {criteria: number_of_failed_frames}
    """
    lines = []
    fail_counts = {}
    
    # Determine which saturation column to use in videodata
    try:
        sat_column = get_saturation_column(videodata)
        print(f"DEBUG: Using saturation column: {sat_column}")
    except ValueError as e:
        print(f"WARNING: {e}")
        sat_column = None
    
    for err in errors:
        if not hasattr(err, "criteria"):
            continue
        crit = err.criteria
        
        # Special handling for 'sat' and 'sathigh'
        if crit in ("sat", "sathigh"):
            if sat_column is None:
                print(f"WARNING: Cannot process {crit} - no saturation column available")
                continue
                
            # Get thresholds from standardDF (these are threshold values, not column names)
            illegal = get_threshold(crit, "illegal", standardDF)
            clipping = get_threshold(crit, "clippinglimit", standardDF)
            brng = get_threshold(crit, "brnglimit", standardDF)
            
            # Check the single saturation column (sathigh or satmax) against each threshold
            for label, threshold in [
                ("illegal", illegal),
                ("clipping", clipping),
                ("brng", brng),
            ]:
                if threshold is None:
                    frametimes_hms = []
                else:
                    # Compare sat_column (sathigh or satmax) against threshold
                    failing = videodata[videodata[sat_column] > threshold]
                    frametimes = (
                        failing["Frame Time"].tolist()
                        if "Frame Time" in failing.columns
                        else failing.index.tolist()
                    )
                    frametimes_hms = [format_seconds_to_hms(ft) for ft in frametimes]
                
                lines.append(
                    f"Criteria: {crit} ({label}) [using {sat_column}]\n"
                    f"  Failed Frames: {len(frametimes_hms)}\n"
                    f"  Failing Frame Times: {frametimes_hms}\n"
                )
                fail_counts[f"{crit}_{label}"] = len(frametimes_hms)
            
            continue

        # For Y/U/V criteria (ymin, ymax, umin, umax, vmin, vmax)
        # The criteria name now matches the videodata column directly
        
        # Check if column exists in videodata
        if crit not in videodata.columns:
            continue

        # Map criteria to standardDF row names
        # ymin -> ylow, ymax -> yhigh, etc.
        if 'min' in crit.lower():
            standards_row = crit.replace('min', 'low')
        elif 'max' in crit.lower():
            standards_row = crit.replace('max', 'high')
        else:
            # Unknown criteria type, skip
            continue

        # Get threshold from standardDF using brngout column
        try:
            standard_value = standardDF.at[standards_row, "brngout"]
        except Exception:
            standard_value = None

        if standard_value is None:
            continue

        # Apply the correct comparison operators
        # MIN criteria: fail if value <= threshold (must be > threshold to pass)
        # MAX criteria: fail if value >= threshold (must be < threshold to pass)
        if "min" in crit:
            failing = videodata[videodata[crit] <= standard_value]
        else:  # max
            failing = videodata[videodata[crit] >= standard_value]

        frametimes = (
            failing["Frame Time"].tolist()
            if "Frame Time" in failing.columns
            else failing.index.tolist()
        )
        
        # Format frametimes to 00:00:00
        frametimes_hms = [format_seconds_to_hms(ft) for ft in frametimes]
        fail_counts[crit] = len(frametimes)
        
        if frametimes:
            lines.append(
                f"Criteria: {crit} ({err.status})\n"
                f"  Failing Frame Times: {frametimes_hms}\n"
            )
    
    return ("\n".join(lines) if lines else "None"), fail_counts


def get_threshold(crit, col, standardDF):
    """Get threshold value from standardDF for saturation criteria."""
    # If crit is 'sathigh', use 'sat' row in standardDF
    lookup_crit = "sat" if crit == "sathigh" else crit
    
    try:
        return standardDF.at[lookup_crit, col]
    except Exception:
        return None