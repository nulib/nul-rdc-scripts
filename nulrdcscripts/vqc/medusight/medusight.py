"""
Video Quality Control Analysis Tool (Medusight)

This script processes QCTools XML/JSON files to analyze video quality metrics,
generate statistics, and produce detailed reports on quality control issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import progressbar
import pandas as pd
import re
from medusight.params import args
from medusight import dataparsing, framestatistics, qcsetup, overallStatistics
import datetime
import concurrent.futures
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)


# ============================================================================
# UTILITY FUNCTIONS (from output.py)
# ============================================================================

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", filename)


def safe_bitdepth(bitdepth):
    """Safely convert bitdepth to integer."""
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
    """Generate statistics for criteria that passed."""
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


# ============================================================================
# TEMPLATE VALIDATION
# ============================================================================

def validate_template_files():
    """Validate that required template files exist."""
    template_path = os.path.join(os.path.dirname(__file__), "data", "templateVideo.txt")
    template_frames_path = os.path.join(os.path.dirname(__file__), "data", "templateFrames.txt")
    
    missing_templates = []
    if not os.path.exists(template_path):
        missing_templates.append(template_path)
    if not os.path.exists(template_frames_path):
        missing_templates.append(template_frames_path)
    
    if missing_templates:
        error_msg = "Missing required template files:\n" + "\n".join(missing_templates)
        raise FileNotFoundError(error_msg)
    
    return template_path, template_frames_path


def get_output_directory(inputPath, outputPath):
    """Determine the output directory based on input and output paths."""
    if outputPath == "input":
        if os.path.isdir(inputPath):
            return inputPath
        else:
            return os.path.dirname(inputPath)
    else:
        return outputPath


# ============================================================================
# VIDEO ANALYSIS FUNCTIONS
# ============================================================================

def test_bitdepth_medians(videoDSDF):
    """Validate that bit depth medians are consistent and either 8 or 10."""
    y = videoDSDF.loc["50%", "ybitdepth"]
    u = videoDSDF.loc["50%", "ubitdepth"]
    v = videoDSDF.loc["50%", "vbitdepth"]
    
    if not (y == u == v and y in [8, 10]):
        raise AssertionError(
            f"Median bit depths are not all 8 or all 10: y={y}, u={u}, v={v}"
        )


def filter_errors_with_failed_frames(errors, videodata, standardDF):
    """
    Filter out errors that have zero failed frames.
    
    This prevents reporting errors at the video statistics level when
    no actual individual frames fail the criteria.
    
    Args:
        errors: List of error objects from overallStatistics.runstatsvideo
        videodata: DataFrame containing per-frame video data
        standardDF: DataFrame containing quality thresholds
    
    Returns:
        List of errors that have at least one failing frame
    """
    if not errors:
        return errors
    
    filtered_errors = []
    
    for err in errors:
        if isinstance(err, str):
            # Keep string errors as-is
            filtered_errors.append(err)
            continue
        
        # Get the criteria name
        criteria = err.criteria
        
        print(f"DEBUG FILTER: Checking {criteria}")
        
        # Count actual failing frames for this criteria
        if criteria in ("sat", "sathigh"):
            # For saturation, check all three sub-criteria using correct column names
            has_failures = False
            for label in ("illegal", "clippinglimit", "brnglimit"):
                col_name = f"sat_{label}" if label != "illegal" else "sat_illegal"
                # Map column names: illegal->sat_illegal, clippinglimit->sat_clipping, brnglimit->sat_brng
                if label == "clippinglimit":
                    col_name = "sat_clipping"
                elif label == "brnglimit":
                    col_name = "sat_brng"
                
                if col_name in videodata.columns:
                    if criteria in standardDF.index and label in standardDF.columns:
                        threshold = standardDF.loc[criteria, label]
                        failing_count = (videodata[col_name] > threshold).sum()
                        print(f"DEBUG FILTER:   {col_name} > {threshold}: {failing_count} failures")
                        if failing_count > 0:
                            has_failures = True
                            break
            
            if has_failures:
                print(f"DEBUG FILTER:   ✓ Keeping {criteria} (has failures)")
                filtered_errors.append(err)
            else:
                print(f"DEBUG FILTER:   ✗ Removing {criteria} (no failures)")
        else:
            # For other criteria (ymin, ymax, umin, umax, vmin, vmax)
            # The criteria name now matches the videodata column name directly!
            
            if criteria not in videodata.columns:
                print(f"DEBUG FILTER:   ! Column {criteria} not found in videodata")
                print(f"DEBUG FILTER:   Available columns: {list(videodata.columns)[:15]}...")
                filtered_errors.append(err)
                continue
            
            # Map criteria to standardDF row names
            # ymin -> ylow, ymax -> yhigh, etc.
            if 'min' in criteria.lower():
                standards_row = criteria.replace('min', 'low')
            elif 'max' in criteria.lower():
                standards_row = criteria.replace('max', 'high')
            else:
                print(f"DEBUG FILTER:   ! Unknown criteria type {criteria}, keeping to be safe")
                filtered_errors.append(err)
                continue
            
            # Check if we can get the threshold from standardDF
            if standards_row not in standardDF.index:
                print(f"DEBUG FILTER:   ! {standards_row} not in standardDF index")
                print(f"DEBUG FILTER:   standardDF index: {list(standardDF.index)[:10]}")
                filtered_errors.append(err)
                continue
            
            print(f"DEBUG FILTER:   ✓ {standards_row} found in standardDF index")
            print(f"DEBUG FILTER:   standardDF columns: {list(standardDF.columns)}")
            
            if "brngout" not in standardDF.columns:
                print(f"DEBUG FILTER:   ! brngout column not in standardDF")
                # Check if there's an alternative column name
                brng_cols = [col for col in standardDF.columns if 'brng' in col.lower() or 'out' in col.lower()]
                print(f"DEBUG FILTER:   Possible brng columns: {brng_cols}")
                filtered_errors.append(err)
                continue
            
            print(f"DEBUG FILTER:   ✓ brngout found in standardDF columns")
            threshold = standardDF.loc[standards_row, "brngout"]
            print(f"DEBUG FILTER:   ✓ Retrieved threshold: {threshold}")
            
            # Count failures based on min/max
            if 'min' in criteria.lower():
                # For MIN criteria: frames fail if value <= threshold
                failing_count = (videodata[criteria] <= threshold).sum()
                print(f"DEBUG FILTER:   {criteria} <= {threshold} (from {standards_row}): {failing_count} failures")
            else:  # max
                # For MAX criteria: frames fail if value >= threshold
                failing_count = (videodata[criteria] >= threshold).sum()
                print(f"DEBUG FILTER:   {criteria} >= {threshold} (from {standards_row}): {failing_count} failures")
            
            if failing_count > 0:
                print(f"DEBUG FILTER:   ✓ Keeping {criteria} (has failures)")
                filtered_errors.append(err)
            else:
                print(f"DEBUG FILTER:   ✗ Removing {criteria} (no failures)")
    
    print(f"DEBUG FILTER: Filtered {len(errors)} errors down to {len(filtered_errors)}")
    return filtered_errors


# ============================================================================
# REPORT GENERATION
# ============================================================================

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
    """
    Write video statistics and errors to a formatted text report.
    
    Properly handles both regular criteria (ylow, yhigh, etc.) and 
    saturation criteria (sat, sathigh) which have different structures.
    
    Uses the "most severe level" logic for saturation errors:
    - Reports only the first failing level (illegal > clipping > brng)
    - If none fail, reports brng with 0
    
    Args:
        errors: List of error objects
        template_path: Path to the report template file
        output_path: Where to write the output report
        videobitdepth: Bit depth of the video (8 or 10)
        filename: Name of the input file
        passfail_video: Overall PASS/FAIL status
        all_criteria: List of all criteria to check
        videoDSDF: DataFrame with video descriptive statistics
        standardDF: DataFrame with quality thresholds
        videodata: DataFrame with per-frame data
        fail_counts: Dictionary mapping criteria to failed frame counts
        total_frames: Total number of frames in the video
    """
    error_lines = []
    
    # Debug: Print what we received
    print(f"DEBUG: write_video_stats_to_txt received {len(errors)} errors")
    print(f"DEBUG: passfail_video = {passfail_video}")
    
    # Process errors if they exist
    if errors:
        for err in errors:
            if not isinstance(err, str):
                # Special handling for sat and sathigh
                if err.criteria in ("sat", "sathigh"):
                    # Only report the most severe level that has failures
                    levels = [
                        ("illegal", "Illegal"),
                        ("clipping", "Clipping"),
                        ("brng", "Broadcast Range"),
                    ]
                    found_failure = False
                    for label, label_pretty in levels:
                        key = f"{err.criteria}_{label}"
                        count = fail_counts.get(key, 0) if fail_counts else 0
                        percent = (count / total_frames) * 100 if total_frames else 0
                        
                        print(f"DEBUG: Checking {key}: count={count}")
                        
                        if count > 0:
                            # Get the actual values for this saturation level
                            col_name = f"sat_{label}"
                            if col_name in videodata.columns:
                                video_value = videodata[col_name].max()
                            else:
                                video_value = "N/A"
                            
                            # Get the standard threshold
                            if err.criteria in standardDF.index and label in standardDF.columns:
                                standard_value = standardDF.loc[err.criteria, label]
                            else:
                                standard_value = "N/A"
                            
                            error_lines.append(
                                f"Criteria: {err.criteria} ({label_pretty})\n"
                                f"  Status: {err.status}\n"
                                f"  Video Value (max): {video_value}\n"
                                f"  Standard Value (threshold): {standard_value}\n"
                                f"  Failed Frames: {count} ({percent:.2f}% of {total_frames})\n"
                            )
                            found_failure = True
                            break  # Only report the most severe level
                    
                    if not found_failure:
                        print(f"DEBUG: No failures found for {err.criteria}, but error still in list!")
                else:
                    # Regular criteria (ylow, yhigh, ulow, uhigh, vlow, vhigh, etc.)
                    count = fail_counts.get(err.criteria, 0) if fail_counts else 0
                    percent = (count / total_frames) * 100 if total_frames else 0
                    
                    print(f"DEBUG: Checking {err.criteria}: count={count}")
                    
                    if count > 0:
                        # Extract video and standard values from error object
                        video_value = getattr(err, 'video_value', 'N/A')
                        standard_value = getattr(err, 'standard_value', 'N/A')
                        
                        error_lines.append(
                            f"Criteria: {err.criteria}\n"
                            f"  Status: {err.status}\n"
                            f"  Video Value: {video_value}\n"
                            f"  Standard Value: {standard_value}\n"
                            f"  Failed Frames: {count} ({percent:.2f}% of {total_frames})\n"
                        )
                    else:
                        print(f"DEBUG: {err.criteria} has 0 failures but still in error list!")
            else:
                # String errors (legacy format)
                error_lines.append(err.replace("\n", " ").replace("\r", " "))
    
    print(f"DEBUG: Generated {len(error_lines)} error lines")
    
    # Determine error text based on whether we have errors
    if not errors:
        error_text = "No errors detected.\n"
    elif not error_lines:
        error_text = "No errors detected.\n"  # Changed: if no error_lines, treat as pass
    else:
        error_text = "\n".join(error_lines)
    
    # Load template
    with open(template_path, "r", encoding="utf-8") as template_file:
        template = template_file.read()
    
    # Get passing stats
    passing_stats_text = get_passing_stats(all_criteria, errors, videoDSDF, standardDF)
    
    # Format the output
    output_text = template.format(
        error_details=error_text,
        videobitdepth=videobitdepth,
        filename=filename,
        passfail_video=passfail_video,
        passing_stats=passing_stats_text,
        total_frames=total_frames,
    )
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(output_text)
    
    print(f"Video statistics written to: {output_path}")


def write_frames_report(template_frames_path, failing_frames_text, outputDir, 
                       base_filename, inputPath, videobitdepth, passfail_video, 
                       total_frames):
    """
    Write the failing frames report to a text file.
    
    Args:
        template_frames_path: Path to the frames report template
        failing_frames_text: Formatted text describing failing frames
        outputDir: Directory where the report will be saved
        base_filename: Base name of the file (without extension)
        inputPath: Path to the original input file
        videobitdepth: Bit depth of the video
        passfail_video: Overall PASS/FAIL status
        total_frames: Total number of frames
    """
    with open(template_frames_path, "r", encoding="utf-8") as f:
        frames_template = f.read()
    
    # Handle empty failing frames text
    if not failing_frames_text or not failing_frames_text.strip():
        failing_frames_text = "No frames failed any criteria."
    
    frames_report = frames_template.format(
        FAILING_FRAMES=failing_frames_text,
        filename=os.path.basename(inputPath),
        videobitdepth=videobitdepth,
        passfail_video=passfail_video,
        total_frames=total_frames,
    )
    
    output_path = os.path.join(
        outputDir, 
        f"{base_filename}_failing_frames_by_criteria.txt"
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(frames_report)
    
    print(f"Failing frames report written to: {output_path}")


# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def processfile(inputPath, outputPath):
    """
    Process a single video QC file and generate reports.
    
    Args:
        inputPath: Path to the XML/JSON file to process
        outputPath: Where to save output files ('input' or a specific directory)
    """
    try:
        # Validate templates at the start
        template_path, template_frames_path = validate_template_files()
        
        bitDepth = args.videobitdepth
        
        # Setup phase
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
        
        # Initialize base_filename before conditional blocks
        base_filename = os.path.splitext(os.path.basename(inputPath))[0]
        base_filename = base_filename.replace('.mkv.qctools', '')
        
        # Parse video data
        if inputFileType == "JSON":
            videodata = dataparsing.dataparsingandtabulatingvideoJSON(inputPath)
        else:
            videodata = dataparsing.dataparsingandtabulatingvideoXML(inputPath)
        
        # Determine output directory
        outputDir = get_output_directory(inputPath, outputPath)
        
        # Save raw video data
        outputdata = f"{outputDir}/{base_filename}_raw_video_data.csv"
        videodata.to_csv(outputdata, index=False)
        
        print("*****Parsing complete*****")
        print("*****Generating Full Video Descriptive Statistics*****")
        
        # Generate statistics
        videoDSDF = dataparsing.videodatastatistics(videodata)
        
        # Test and determine bit depth
        print("***Determining Video Bit Depth Standards***")
        test_bitdepth_medians(videoDSDF)
        videobitdepth = videoDSDF["ybitdepth"].mode()[0]
        standardDF = qcsetup.setVideoBitDepth(videobitdepth)
        
        # Save summary statistics
        sumVideoStatsCSV = dataparsing.videostatstocsv(videoDSDF, outputDir, base_filename)
        
        print("*****Generated Full Video Descriptive Statistics*****")
        print("*****Analysing Full Video Descriptive Statistics*****")
        
        # Analyze statistics and filter out errors with no failing frames
        errors = overallStatistics.runstatsvideo(videoDSDF, standardDF)
        
        # Debug: Show what we're working with
        print(f"DEBUG: videodata columns (first 15): {list(videodata.columns[:15])}")
        print(f"DEBUG: Errors before filtering: {[err.criteria if hasattr(err, 'criteria') else err for err in errors]}")
        
        errors = filter_errors_with_failed_frames(errors, videodata, standardDF)
        
        # Recalculate pass/fail status AFTER filtering
        passfail_video = "PASS" if not errors else "FAIL"
        
        all_criteria = [
            "ylow", "yhigh", "ulow", "uhigh", "vlow", "vhigh",
        ]
        
        # Get failing frames information
        failing_frames_text, fail_counts = framestatistics.get_failing_frametimes(
            errors, videodata, standardDF
        )
        total_frames = len(videodata)
        
        # Write video-level report
        write_video_stats_to_txt(
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
        
        # Write frame-level report
        write_frames_report(
            template_frames_path,
            failing_frames_text,
            outputDir,
            base_filename,
            inputPath,
            videobitdepth,
            passfail_video,
            total_frames
        )
        
        print(f"*****Processing complete for {base_filename}*****")
        
    except Exception as e:
        print(f"Error processing {inputPath}: {str(e)}")
        raise


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the video QC analysis tool."""
    inputPath = os.path.normpath(args.input_path)
    outputPath = args.output_path
    
    if os.path.isdir(inputPath):
        # Batch processing mode
        print(f"Batch processing directory: {inputPath}")
        supported_exts = (".xml", ".json")
        
        files_to_process = [
            os.path.join(inputPath, fname)
            for fname in os.listdir(inputPath)
            if os.path.isfile(os.path.join(inputPath, fname)) 
            and fname.lower().endswith(supported_exts)
        ]
        
        if not files_to_process:
            print(f"No files with extensions {supported_exts} found in {inputPath}")
            return
        
        print(f"Found {len(files_to_process)} files to process")
        
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
        # Single file processing mode
        print(f"Processing single file: {inputPath}")
        processfile(inputPath, outputPath)


if __name__ == "__main__":
    main()