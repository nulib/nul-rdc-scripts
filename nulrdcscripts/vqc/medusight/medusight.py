import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import progressbar
import pandas as pd
from nulrdcscripts.vqc.medusight.params import args
from nulrdcscripts.vqc.medusight import dataparsing, output, framestatistics, qcsetup, overallStatistics
import uuid
import datetime
import concurrent.futures
import os
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

template_path = os.path.join(os.path.dirname(__file__), "data", "templateVideo.txt")

if not os.path.exists(template_path):
    print(f"Template not found at: {template_path}")
    # Optionally, raise an error or exit


def processfile(inputPath, outputPath):
    bitDepth = args.videobitdepth

    # Removed print statements about processing mode
    with progressbar.ProgressBar(max_value=4) as qcsetupBar:
        qcsetupBar.update(0)
        qcsetup.inputCheck(inputPath)
        qcsetupBar.update(1)
        outputLocation = qcsetup.outputCheck(inputPath, outputPath)
        qcsetupBar.update(2)
        inputFileType = qcsetup.setInputFileType(inputPath)
        qcsetupBar.update(3)
    print("*****Setup Complete*****")

    print("*****Parsing File Video*****")
    if inputFileType == "JSON":
        videodata = dataparsing.dataparsingandtabulatingvideoJSON(inputPath)
    else:
        videodata = dataparsing.dataparsingandtabulatingvideoXML(inputPath)
        base_filename = os.path.splitext(os.path.basename(inputPath))[0]
        base_filename = base_filename.replace('.mkv.qctools', '')
        outputdata = f"{outputLocation}/{base_filename}_raw_video_data.csv"
        videodata.to_csv(outputdata, index=False)
    print("*****Parsing complete*****")

    print("*****Generating Full Video Descriptive Statistics*****")
    videoDSDF = dataparsing.videodatastatistics(videodata)

    def test_bitdepth_medians(videoDSDF):
        y = videoDSDF.loc["50%", "ybitdepth"]
        u = videoDSDF.loc["50%", "ubitdepth"]
        v = videoDSDF.loc["50%", "vbitdepth"]
        assert (y == u == v == 8) or (
            y == u == v == 10
        ), f"Median bit depths are not all 8 or all 10: y={y}, u={u}, v={v}"

    print("***Determining Video Bit Depth Standards***")
    test_bitdepth_medians(videoDSDF)
    videobitdepth = videoDSDF["ybitdepth"].mode()[0]
    standardDF = qcsetup.setVideoBitDepth(videobitdepth)

    if outputPath == "input":
        if os.path.isdir(inputPath):
            outputDir = inputPath
        else:
            outputDir = os.path.dirname(inputPath)
    else:
        outputDir = outputPath

    sumVideoStatsCSV = dataparsing.videostatstocsv(videoDSDF, outputDir,base_filename)
    print("*****Generated Full Video Descriptive Statistics*****")

    print("*****Analysing Full Video Descriptive Statistics*****")
    errors = overallStatistics.runstatsvideo(videoDSDF, standardDF)
    passfail_video = "PASS" if not errors else "FAIL"

    all_criteria = [
        "ylow", "yhigh", "ulow", "uhigh", "vlow", "vhigh",
    ]
    failing_frames_text, fail_counts = framestatistics.get_failing_frametimes(
        errors, videodata, standardDF
    )
    total_frames = len(videodata)

    output.write_video_stats_to_txt(
        errors,
        template_path,
        f"{outputDir}/{base_filename}_video_level_report.txt",
        videobitdepth,
        os.path.basename(inputPath),
        passfail_video,
        all_criteria,
        videoDSDF,
        standardDF,
        videodata,
        fail_counts=fail_counts,
        total_frames=total_frames,
    )

    print("*****Analysed Full Video Descriptive Statistics*****")
    print("*****Analyzing Frame statistics*****")
    failing_frames_text, fail_counts = framestatistics.get_failing_frametimes(
        errors, videodata, standardDF
    )
    total_frames = len(videodata)

    template_frames_path = os.path.join(
        os.path.dirname(__file__), "data", "templateFrames.txt"
    )
    if not os.path.exists(template_frames_path):
        print(f"Template not found at: {template_frames_path}")

    with open(template_frames_path, "r", encoding="utf-8") as f:
        frames_template = f.read()

    frames_report = frames_template.format(
        FAILING_FRAMES=failing_frames_text,
        filename=os.path.basename(inputPath),
        videobitdepth=videobitdepth,
        passfail_video=passfail_video,
        total_frames=total_frames,  # <-- Add this line
    )

    with open(
        os.path.join(outputDir, base_filename,"failing_frames_by_criteria.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(frames_report)


def main():
    inputPath = os.path.normpath(args.input_path)
    outputPath = args.output_path

    if os.path.isdir(inputPath):
        print(f"Batch processing directory: {inputPath}")
        supported_exts = (".xml", ".json")  # Add more extensions if needed
        files_to_process = [
            os.path.join(inputPath, fname)
            for fname in os.listdir(inputPath)
            if os.path.isfile(os.path.join(inputPath, fname)) and fname.lower().endswith(supported_exts)
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(processfile, fpath, outputPath)
                for fpath in files_to_process
            ]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print(f"File processing generated an exception: {exc}")
    else:
        processfile(inputPath, outputPath)


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
    # If there are no errors, set status to PASS and skip error details
    if not errors:
        passfail_video = "PASS"
        error_text = "No errors detected.\n"
    else:
        for err in errors:
            if not isinstance(err, str):
                # Special handling for sat and satmax
                if err.criteria in ("sat", "satmax"):
                    for label in ("illegal", "clipping", "brng"):
                        key = f"{err.criteria}_{label}"
                        count = fail_counts.get(key, 0) if fail_counts else 0
                        percent = (count / total_frames) * 100 if total_frames else 0
                        if count > 0:
                            error_lines.append(
                                f"Criteria: {err.criteria} ({label})\n"
                                f"  Status: {err.status}\n"
                                f"  Failed Frames: {count} ({percent:.2f}% of {total_frames})\n"
                            )
                else:
                    count = fail_counts.get(err.criteria, 0) if fail_counts else 0
                    percent = (count / total_frames) * 100 if total_frames else 0
                    if count > 0:
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

    passing_stats_text = overallStatistics.get_passing_stats(
        all_criteria, errors, videoDSDF, standardDF
    )

    output_text = template.format(
        error_details=error_text,
        videobitdepth=videobitdepth,
        filename=filename,
        passfail_video=passfail_video,
        passing_stats=passing_stats_text,
    )

    total_frames_line = f"Total Frames: {total_frames}\n" if total_frames is not None else ""
    passfail_str = f"{passfail_video}"
    if passfail_str in output_text:
        idx = output_text.find(passfail_str) + len(passfail_str)
        output_text = output_text[:idx] + "\n" + total_frames_line + output_text[idx:]
    else:
        output_text = total_frames_line + output_text

    with open(output_path, "w") as output_file:
        output_file.write(output_text)

    print(f"Video statistics written to: {output_path}")


def create_new_item(original_filepath, unique_part):
    base_filename = os.path.splitext(os.path.basename(original_filepath))[0]
    new_filename = f"{base_filename}_{unique_part}"
    return new_filename


def seconds_to_hms(seconds):
    return str(datetime.timedelta(seconds=int(seconds)))


# Example usage in your stats output
# hms_time = seconds_to_hms(time_in_seconds)


if __name__ == "__main__":
    main()
