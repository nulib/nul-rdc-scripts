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
):
    # Sanitize inputs
    safe_filename = sanitize_filename(filename)
    safe_videobitdepth = safe_bitdepth(videobitdepth)

    # Read the template
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Format the errors as multi-line blocks (Option 3)
    error_lines = []
    for err in errors:
        if not isinstance(err, str):
            error_lines.append(
                f"Criteria: {err.criteria}\n"
                f"    Status: {err.status}\n"
                f"    Video Value: {err.video_value}\n"
                f"    Standard Value: {err.standard_value}\n"
            )
        else:
            error_lines.append(err.replace("\n", " ").replace("\r", " "))
    error_text = "\n".join(error_lines)

    # Format passing stats with values
    passing_stats_text = get_passing_stats(all_criteria, errors, videoDSDF, standardDF)

    # Fill in the template
    output = template.format(
        filename=safe_filename,
        videobitdepth=safe_videobitdepth,
        passfail_video=passfail_video,
        ERRORS=error_text,
        PASSING_STATS=passing_stats_text,
    )

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)


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
