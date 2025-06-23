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


def write_video_stats_to_txt(
    errors, template_path, output_path, videobitdepth, filename, passfail_video
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

    # Fill in the template
    output = template.format(
        filename=safe_filename,
        videobitdepth=safe_videobitdepth,
        passfail_video=passfail_video,
        ERRORS=error_text,
    )

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)


# Example usage after running your stats:
# errors = runstatsvideo(videoDSDF, standardsDF)
# passfail_video = "PASS" if not errors else "FAIL"
# write_video_stats_to_txt(
#     errors,
#     os.path.join(os.path.dirname(__file__), "data//templateVideo.txt"),
#     os.path.join(outputDir, "video_report.txt"),
#     videobitdepth,
#     os.path.basename(inputPath),
#     passfail_video
# )
