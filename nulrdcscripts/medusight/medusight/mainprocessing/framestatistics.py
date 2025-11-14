import datetime
import pandas as pd


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
        
        # Special handling for saturation - report only most severe level
        if crit in ("sat", "sathigh", "satmax"):
            if sat_column is None:
                print(f"WARNING: Cannot process {crit} - no saturation column available")
                continue
                
            # Get thresholds from standardDF - using your column names
            try:
                illegal = standardDF.at["sat", "illegal"]
                clipping = standardDF.at["sat", "clippinglimit"]
                brng = standardDF.at["sat", "brnglimit"]
            except Exception as e:
                print(f"WARNING: Could not read saturation thresholds: {e}")
                continue
            
            # Check levels from most to least severe
            # Only report the MOST SEVERE level that has failures
            for label, threshold in [
                ("illegal", illegal),
                ("clipping", clipping),
                ("brng", brng),
            ]:
                if threshold is None or pd.isna(threshold):
                    continue
                    
                failing = videodata[videodata[sat_column] > threshold]
                count = len(failing)
                
                if count > 0:
                    # Found failures at this level - report and stop
                    frametimes = (
                        failing["Frame Time"].tolist()
                        if "Frame Time" in failing.columns
                        else failing.index.tolist()
                    )
                    frametimes_hms = [format_seconds_to_hms(ft) for ft in frametimes]
                    
                    lines.append(
                        f"Criteria: {crit} ({label}) [using {sat_column}]\n"
                        f"  Failed Frames: {count}\n"
                        f"  Failing Frame Times: {frametimes_hms}\n"
                    )
                    fail_counts[f"{crit}_{label}"] = count
                    break  # Stop at most severe level
            
            continue

        # For Y/U/V criteria (ymin, ymax, umin, umax, vmin, vmax)
        if crit not in videodata.columns:
            continue

        # Get threshold from standardDF - use criteria name directly
        try:
            standard_value = standardDF.at[crit, "brngout"]
        except Exception:
            standard_value = None

        if standard_value is None or pd.isna(standard_value):
            continue

        # Apply the correct comparison operators
        if "min" in crit:
            failing = videodata[videodata[crit] <= standard_value]
        else:  # max
            failing = videodata[videodata[crit] >= standard_value]

        frametimes = (
            failing["Frame Time"].tolist()
            if "Frame Time" in failing.columns
            else failing.index.tolist()
        )
        
        frametimes_hms = [format_seconds_to_hms(ft) for ft in frametimes]
        fail_counts[crit] = len(frametimes)
        
        if frametimes:
            lines.append(
                f"Criteria: {crit} ({err.status})\n"
                f"  Failing Frame Times: {frametimes_hms}\n"
            )
    
    return ("\n".join(lines) if lines else "None"), fail_counts