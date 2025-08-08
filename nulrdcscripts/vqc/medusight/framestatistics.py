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
        if crit not in videodata.columns:
            continue

        # Special handling for 'sat' and 'satmax'
        if crit in ("sat", "satmax"):
            # Use the correct columns for sat/satmax
            brng = get_threshold(crit, "brnglimit", standardDF)
            clipping = get_threshold(crit, "clippinglimit", standardDF)
            illegal = get_threshold(crit, "illegal", standardDF)

            # Find failing frames for each threshold
            failing_illegal = (
                videodata[videodata[crit] > illegal]
                if illegal is not None
                else videodata.iloc[[]]
            )
            failing_clipping = (
                videodata[videodata[crit] > clipping]
                if clipping is not None
                else videodata.iloc[[]]
            )
            failing_brng = (
                videodata[videodata[crit] > brng]
                if brng is not None
                else videodata.iloc[[]]
            )

            # Always report all three, even if empty
            for label, failing in [
                ("illegal", failing_illegal),
                ("clipping", failing_clipping),
                ("brng", failing_brng),
            ]:
                frametimes = (
                    failing["Frame Time"].tolist()
                    if "Frame Time" in failing.columns
                    else failing.index.tolist()
                )
                lines.append(
                    f"Criteria: {crit} ({label})\n"
                    f"  Failed Frames: {len(frametimes)}\n"
                    f"  Failing Frame Times: {frametimes}\n"
                )
                fail_counts[f"{crit}_{label}"] = len(frametimes)
            continue  # skip the rest of the loop for sat/satmax

        # Example fail logic (customize as needed)
        try:
            standard_value = standardDF.at[crit, "brngout"]
        except Exception:
            standard_value = None

        if err.status == "out_of_range" and standard_value is not None:
            if "low" in crit:
                failing = videodata[videodata[crit] < standard_value]
            else:
                failing = videodata[videodata[crit] > standard_value]
        elif err.status == "clipping":
            try:
                clipping_value = standardDF.at[crit, "clipping"]
            except Exception:
                clipping_value = None
            if clipping_value is not None:
                if "low" in crit:
                    failing = videodata[videodata[crit] <= clipping_value]
                else:
                    failing = videodata[videodata[crit] >= clipping_value]
            else:
                failing = videodata[videodata[crit].isna()]
        else:
            failing = videodata[videodata[crit].isna()]

        frametimes = (
            failing["Frame Time"].tolist()
            if "Frame Time" in failing.columns
            else failing.index.tolist()
        )
        fail_counts[crit] = len(frametimes)
        if frametimes:
            lines.append(
                f"Criteria: {crit} ({err.status})\n"
                f"  Failing Frame Times: {frametimes}\n"
            )
    return ("\n".join(lines) if lines else "None"), fail_counts


def get_threshold(crit, col, standardDF):
    # If crit is 'satmax', use 'sat' thresholds
    if crit == "satmax":
        crit = "sat"
    try:
        return standardDF.at[crit, col]
    except Exception:
        return None
