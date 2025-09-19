import os
import re


def sanitize_filename(filename):
    # Allow only alphanumeric, dash, underscore, and dot
    return re.sub(r"[^A-Za-z0-9._-]", "_", filename)


def safe_bitdepth(bitdepth):
    try:
        return int(bitdepth)
    except Exception:
        return "UNKNOWN"


def get_fail_percentages(errors, videodata, standardDF):
    """
    Returns a dict: {criteria: percentage_failed}
    """
    fail_percentages = {}
    try:
        total_frames = len(videodata)
    except Exception:
        total_frames = 0

    for err in errors:
        if not hasattr(err, "criteria"):
            continue
        crit = err.criteria
        if crit not in videodata.columns:
            continue

        # Fallback: count NaNs as fails
        fail_count = videodata[crit].isna().sum()
        percent = (fail_count / total_frames) * 100 if total_frames else 0
        fail_percentages[crit] = percent
    return fail_percentages


def get_passing_stats(all_criteria, errors, videoDSDF, standardDF):
    error_criteria = set()
    for err in errors:
        if not isinstance(err, str):
            error_criteria.add(err.criteria)
    passing = [c for c in all_criteria if c not in error_criteria]

    passing_lines = []
    for crit in passing:
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


def write_video_stats_to_txt(
    errors,
    template_path,
    output_path,
    videobitdepth,
    filename,
    passfail_video,
    all_criteria,
    videoDSDF,
    standardDF,
    videodata,
    fail_counts=None,
    total_frames=None,
):
    error_lines = []
    for err in errors:
        if not isinstance(err, str):
            # Special handling for sat and satmax
            if err.criteria in ("sat", "satmax"):
                # Only report the most severe level that has failures
                levels = [
                    ("illegal", "Illegal"),
                    ("clipping", "Clipping"),
                    ("brng", "Broadcast Range"),
                ]
                for label, label_pretty in levels:
                    key = f"{err.criteria}_{label}"
                    count = fail_counts.get(key, 0) if fail_counts else 0
                    percent = (count / total_frames) * 100 if total_frames else 0
                    if count > 0:
                        error_lines.append(
                            f"Criteria: {err.criteria} ({label_pretty})\n"
                            f"  Status: {err.status}\n"
                            f"  Failed Frames: {count} ({percent:.2f}% of {total_frames})\n"
                        )
                        break  # Only report the most severe level
                else:
                    # If no failures at any level, still report 0 for brng
                    count = fail_counts.get(f"{err.criteria}_brng", 0)
                    percent = (count / total_frames) * 100 if total_frames else 0
                    error_lines.append(
                        f"Criteria: {err.criteria} (Broadcast Range)\n"
                        f"  Status: {err.status}\n"
                        f"  Failed Frames: {count} ({percent:.2f}% of {total_frames})\n"
                    )
            else:
                count = fail_counts.get(err.criteria, 0) if fail_counts else 0
                percent = (count / total_frames) * 100 if total_frames else 0
                error_lines.append(
                    f"Criteria: {err.criteria}\n"
                    f"  Status: {err.status}\n"
                    f"  Video Value: {err.video_value}\n"
                    f"  Standard Value: {err.standard_value}\n"
                    f"  Failed Frames: {count} ({percent:.2f}% of {total_frames})\n"
                )
        else:
            error_lines.append(err.replace("\n", " ").replace("\r", " "))
    error_text = "\n".join(error_lines)

    with open(template_path, "r") as template_file:
        template = template_file.read()

    passing_stats_text = get_passing_stats(all_criteria, errors, videoDSDF, standardDF)

    output_text = template.format(
        error_details=error_text,
        videobitdepth=videobitdepth,
        filename=filename,
        passfail_video=passfail_video,
        passing_stats=passing_stats_text,
        total_frames=total_frames,  # <-- Add this line
    )

    with open(output_path, "w") as output_file:
        output_file.write(output_text)

    print(f"Video statistics written to: {output_path}")


# Example usage after running your stats:
# errors = runstatsvideo(videoDSDF, standardsDF)
# passfail_video = "PASS" if not errors else "FAIL"
# write_video_stats_to_txt(
#     errors,
#     template_path,  # use the variable above
#     output_path,
#     videobitdepth,
#     os.path.basename(inputPath),
#     passfail_video,
#     all_criteria,
#     videoDSDF,
#     standardDF
# )

template_path = os.path.join(os.path.dirname(__file__), "data", "templateVideo.txt")
if not os.path.exists(template_path):
    print(f"Template not found at: {template_path}")
    # Optionally, raise an error or exit

