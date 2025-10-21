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


def get_failing_frametimes(errors, videodata, standardDF):
    """
    Returns:
      - A string listing failing frame times for each failing criteria.
      - A dict {criteria: number_of_failed_frames}
    """
    lines = []
    fail_counts = {}
    
    for err in errors:
        if not hasattr(err, "criteria"):
            continue
        crit = err.criteria
        
        # Special handling for 'sat' and 'sathigh'
        if crit in ("sat", "sathigh"):
            # Saturation uses special columns in standardDF: brnglimit, clippinglimit, illegal
            illegal = get_threshold(crit, "illegal", standardDF)
            clipping = get_threshold(crit, "clippinglimit", standardDF)
            brng = get_threshold(crit, "brnglimit", standardDF)
            
            # The column in videodata for saturation
            sat_columns = {
                "illegal": "sat_illegal",
                "clipping": "sat_clipping", 
                "brng": "sat_brng"
            }

            # Find failing frames for each threshold
            for label, threshold in [
                ("illegal", illegal),
                ("clipping", clipping),
                ("brng", brng),
            ]:
                col_name = sat_columns.get(label, f"sat_{label}")
                
                if col_name not in videodata.columns or threshold is None:
                    frametimes_hms = []
                else:
                    failing = videodata[videodata[col_name] > threshold]
                    frametimes = (
                        failing["Frame Time"].tolist()
                        if "Frame Time" in failing.columns
                        else failing.index.tolist()
                    )
                    frametimes_hms = [format_seconds_to_hms(ft) for ft in frametimes]
                
                lines.append(
                    f"Criteria: {crit} ({label})\n"
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