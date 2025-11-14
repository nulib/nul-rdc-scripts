"""
Video Quality Control Analysis Tool (Medusight)

This script processes QCTools XML/JSON files OR raw video files to analyze 
video quality metrics, generate statistics, and produce detailed reports on 
quality control issues.

Supports:
- QCTools XML/JSON (external preprocessing)
- Direct video extraction with crop detection
- Audio quality analysis (LUFS, silence detection)
"""

import os
import sys
import progressbar
import pandas as pd
import re
from pathlib import Path
import traceback
import concurrent.futures
import multiprocessing
import warnings
from .mainprocessing.video_data_extractor import process_video_with_options
from .mainprocessing.dataparsing import (
    dataparsingandtabulatingvideoXML,
    videodatastatistics,
    videostatstocsv
)
from .mainprocessing.audioanalysis import analyze_audio_quality, generate_audio_report
from .mainprocessing.framestatistics import get_failing_frametimes, get_saturation_column
from .mainprocessing.qcsetup import inputCheck, outputCheck, setInputFileType, setVideoBitDepth
from .mainprocessing.overallStatistics import runstatsvideo
from .mainprocessing.params import args

warnings.filterwarnings("ignore", category=RuntimeWarning)


# ============================================================================
# UTILITY FUNCTIONS
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


# ============================================================================
# TEMPLATE VALIDATION
# ============================================================================

def validate_template_files():
    """Validate that required template files exist."""
    template_path = os.path.join(os.path.dirname(__file__),"mainprocessing", "data", "templateVideo.txt")
    template_frames_path = os.path.join(os.path.dirname(__file__),"mainprocessing", "data", "templateFrames.txt")
    
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
    """
    if not errors:
        return errors
    
    filtered_errors = []
    
    for err in errors:
        if isinstance(err, str):
            filtered_errors.append(err)
            continue
        
        criteria = err.criteria
        
        print(f"DEBUG FILTER: Checking {criteria}")
        
        # Count actual failing frames for this criteria
        if criteria in ("sat", "sathigh", "satmax"):
            # For saturation, check using the appropriate column
            try:
                sat_column = get_saturation_column(videodata)
            except ValueError:
                print(f"DEBUG FILTER: No saturation column found")
                filtered_errors.append(err)
                continue
                
            # Check against thresholds - using correct column names
            has_failures = False
            for label in ("illegal", "clippinglimit", "brnglimit"):
                try:
                    threshold = standardDF.loc["sat", label]
                    if pd.isna(threshold):
                        continue
                    failing_count = (videodata[sat_column] > threshold).sum()
                    print(f"DEBUG FILTER:   {sat_column} > {threshold}: {failing_count} failures")
                    if failing_count > 0:
                        has_failures = True
                        break
                except Exception as e:
                    print(f"DEBUG FILTER:   Could not check {label}: {e}")
                    continue
            
            if has_failures:
                print(f"DEBUG FILTER:   ✓ Keeping {criteria} (has failures)")
                filtered_errors.append(err)
            else:
                print(f"DEBUG FILTER:   ✗ Removing {criteria} (no failures)")
        else:
            # For Y/U/V criteria (ymin, ymax, umin, umax, vmin, vmax)
            if criteria not in videodata.columns:
                print(f"DEBUG FILTER:   ! Column {criteria} not found in videodata")
                filtered_errors.append(err)
                continue
            
            # Use criteria name directly for standards lookup
            if criteria not in standardDF.index:
                print(f"DEBUG FILTER:   ! {criteria} not in standardDF index")
                filtered_errors.append(err)
                continue
            
            if "brngout" not in standardDF.columns:
                print(f"DEBUG FILTER:   ! brngout column not in standardDF")
                filtered_errors.append(err)
                continue
            
            threshold = standardDF.loc[criteria, "brngout"]
            
            # Count failures based on min/max
            if 'min' in criteria:
                failing_count = (videodata[criteria] <= threshold).sum()
                print(f"DEBUG FILTER:   {criteria} <= {threshold}: {failing_count} failures")
            else:  # max
                failing_count = (videodata[criteria] >= threshold).sum()
                print(f"DEBUG FILTER:   {criteria} >= {threshold}: {failing_count} failures")
            
            if failing_count > 0:
                print(f"DEBUG FILTER:   ✓ Keeping {criteria} (has failures)")
                filtered_errors.append(err)
            else:
                print(f"DEBUG FILTER:   ✗ Removing {criteria} (no failures)")
    
    print(f"DEBUG FILTER: Filtered {len(errors)} errors down to {len(filtered_errors)}")
    return filtered_errors


def get_passing_stats(all_criteria, errors, videoDSDF, standardDF):
    """
    Generate statistics text for criteria that passed.
    
    Args:
        all_criteria: List of all criteria names (ymin, ymax, sat, etc.)
        errors: List of error objects
        videoDSDF: Video descriptive statistics
        standardDF: Standards dataframe
    
    Returns:
        Formatted string with passing criteria stats
    """
    # Extract error criteria
    error_criteria = set()
    for err in errors:
        if not isinstance(err, str) and hasattr(err, 'criteria'):
            # For saturation, match any sat variant
            if err.criteria in ("sat", "sathigh", "satmax"):
                error_criteria.add("sat")
            else:
                error_criteria.add(err.criteria)
    
    passing = [c for c in all_criteria if c not in error_criteria]

    passing_lines = []
    for crit in passing:
        if crit == "sat":
            # Special handling for saturation
            try:
                sat_column = get_saturation_column(videoDSDF)
                video_value = videoDSDF.at["max", sat_column]
            except Exception:
                video_value = "N/A"
                sat_column = "unknown"
            
            try:
                standard_value = standardDF.at["sat", "brnglimit"]
            except Exception:
                standard_value = "N/A"
            
            passing_lines.append(
                f"Criteria: sat [using {sat_column}]\n"
                f"  Video Value (max): {video_value}\n"
                f"  Standard Value (broadcast range): {standard_value}\n"
            )
        else:
            # Regular Y/U/V criteria
            stat_row = "min" if "min" in crit else "max"
            
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
    """Write video statistics and errors to a formatted text report."""
    error_lines = []
    
    print(f"DEBUG: write_video_stats_to_txt received {len(errors)} errors")
    print(f"DEBUG: passfail_video = {passfail_video}")
    
    # Get saturation column for reporting
    try:
        sat_column = get_saturation_column(videodata)
    except ValueError:
        sat_column = "unknown"
    
    # Process errors if they exist
    if errors:
        for err in errors:
            if not isinstance(err, str):
                # Special handling for saturation - report only most severe level
                if err.criteria in ("sat", "sathigh", "satmax"):
                    levels = [
                        ("illegal", "Illegal"),
                        ("clipping", "Clipping"),
                        ("brng", "Broadcast Range"),
                    ]
                    
                    for label, label_pretty in levels:
                        key = f"{err.criteria}_{label}"
                        count = fail_counts.get(key, 0) if fail_counts else 0
                        percent = (count / total_frames) * 100 if total_frames else 0
                        
                        print(f"DEBUG: Checking {key}: count={count}")
                        
                        if count > 0:
                            # Get the actual values for this saturation level
                            if sat_column in videodata.columns:
                                video_value = videodata[sat_column].max()
                            else:
                                video_value = "N/A"
                            
                            # Get the standard threshold
                            threshold_col = {
                                "illegal": "illegal",
                                "clipping": "clippinglimit",
                                "brng": "brnglimit"
                            }.get(label)
                            
                            try:
                                standard_value = standardDF.loc["sat", threshold_col]
                            except Exception:
                                standard_value = "N/A"
                            
                            # Report only this most severe level
                            error_lines.append(
                                f"Criteria: sat ({label_pretty}) [using {sat_column}]\n"
                                f"  Status: {err.status}\n"
                                f"  Video Value (max): {video_value}\n"
                                f"  Standard Value (threshold): {standard_value}\n"
                                f"  Failed Frames: {count} ({percent:.2f}% of {total_frames})\n"
                            )
                            break  # Only report most severe level
                    
                    continue
                else:
                    # Regular criteria (ymin, ymax, umin, umax, vmin, vmax)
                    count = fail_counts.get(err.criteria, 0) if fail_counts else 0
                    percent = (count / total_frames) * 100 if total_frames else 0
                    
                    print(f"DEBUG: Checking {err.criteria}: count={count}")
                    
                    if count > 0:
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
                error_lines.append(err.replace("\n", " ").replace("\r", " "))
    
    print(f"DEBUG: Generated {len(error_lines)} error lines")
    
    # Determine error text
    if not errors:
        error_text = "No errors detected.\n"
    elif not error_lines:
        error_text = "No errors detected.\n"
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
    """Write the failing frames report to a text file."""
    with open(template_frames_path, "r", encoding="utf-8") as f:
        frames_template = f.read()
    
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
    Process a single video file (raw or QCTools data) and generate reports.
    
    Supports:
    - Raw video files (.mkv, .mov, .mp4, etc.) - Direct extraction with crop detection
    - QCTools XML - External preprocessing
    - CSV files - Previous extraction results
    
    Args:
        inputPath: Path to the file to process
        outputPath: Where to save output files ('input' or a specific directory)
    """
    try:
        # Validate templates at the start
        template_path, template_frames_path = validate_template_files()
        
        bitDepth = args.videobitdepth
        
        # Determine input type
        file_ext = os.path.splitext(inputPath)[1].lower()
        
        # Initialize base_filename early
        base_filename = os.path.splitext(os.path.basename(inputPath))[0]
        base_filename = base_filename.replace('.mkv.qctools', '')
        
        # Setup phase
        with progressbar.ProgressBar(max_value=4) as qcsetupBar:
            qcsetupBar.update(0)
            inputCheck(inputPath)
            qcsetupBar.update(1)
            outputLocation = outputCheck(inputPath, outputPath)
            qcsetupBar.update(2)
            inputFileType = setInputFileType(inputPath)
            qcsetupBar.update(3)
        
        print("*****Setup Complete*****")
        
        # Determine output directory
        outputDir = get_output_directory(inputPath, outputPath)
        
        # ==================================================================
        # BRANCH 1: RAW VIDEO FILE - Direct extraction with crop detection
        # ==================================================================
        if file_ext in ('.mkv', '.mov', '.mp4', '.avi', '.mxf', '.dv'):
            print("*****Raw video detected - extracting statistics*****")
            
            # Extract video stats with crop options
            print("*****Extracting Video Statistics with Crop Detection*****")
            videodata = process_video_with_options(
                video_path=inputPath,
                output_dir=outputDir,
                crop_mode=args.crop_mode,
                manual_crop=args.manual_crop,
                sample_interval=args.sample_interval
            )
            
            if videodata is None:
                print(f"Error: Video extraction failed for {inputPath}")
                return
            
            # Audio analysis if requested
            if args.analyze_audio:
                print("*****Analyzing Audio Quality*****")
                
                # Build custom thresholds if provided
                custom_thresholds = {}
                if args.target_lufs is not None:
                    custom_thresholds['target_lufs'] = args.target_lufs
                if args.max_true_peak is not None:
                    custom_thresholds['max_true_peak'] = args.max_true_peak
                
                # Run audio analysis
                audio_result = analyze_audio_quality(
                    inputPath,
                    standard=args.audio_standard,
                    custom_thresholds=custom_thresholds if custom_thresholds else None
                )
                
                # Generate audio report
                if audio_result['success']:
                    audio_report_path = os.path.join(
                        outputDir,
                        f"{base_filename}_audio_report.txt"
                    )
                    generate_audio_report(audio_result, audio_report_path)
                    print(f"*****Audio Analysis Complete*****")
                else:
                    print(f"Audio analysis failed: {audio_result.get('error')}")
        
        # ==================================================================
        # BRANCH 2: CSV FILE - Previous extraction results
        # ==================================================================
        elif file_ext == '.csv':
            print("*****Parsing CSV Video Data*****")
            videodata = pd.read_csv(inputPath)
    
        # ==================================================================
        # BRANCH 3: QCTools XML - External preprocessing
        # ==================================================================
        else:  # .xml
            print("*****Parsing QCTools XML*****")
            videodata = dataparsingandtabulatingvideoXML(inputPath)
        
        # ==================================================================
        # COMMON ANALYSIS PATH - All input types converge here
        # ==================================================================
        
        # Save raw video data
        outputdata = f"{outputDir}/{base_filename}_raw_video_data.csv"
        videodata.to_csv(outputdata, index=False)
        
        print("*****Parsing complete*****")
        print("*****Generating Full Video Descriptive Statistics*****")
        
        # Generate statistics
        videoDSDF = videodatastatistics(videodata)
        
        # Test and determine bit depth
        print("***Determining Video Bit Depth Standards***")
        test_bitdepth_medians(videoDSDF)
        videobitdepth = videoDSDF["ybitdepth"].mode()[0]
        standardDF = setVideoBitDepth(videobitdepth)
        
        # Save summary statistics
        sumVideoStatsCSV = videostatstocsv(videoDSDF, outputDir, base_filename)
        
        print("*****Generated Full Video Descriptive Statistics*****")
        print("*****Analysing Full Video Descriptive Statistics*****")
        
        # Analyze statistics and filter out errors with no failing frames
        errors = runstatsvideo(videoDSDF, standardDF)
        
        print(f"DEBUG: videodata columns (first 15): {list(videodata.columns[:15])}")
        print(f"DEBUG: Errors before filtering: {[err.criteria if hasattr(err, 'criteria') else err for err in errors]}")
        
        errors = filter_errors_with_failed_frames(errors, videodata, standardDF)
        
        # Recalculate pass/fail status AFTER filtering
        passfail_video = "PASS" if not errors else "FAIL"
        
        # All criteria we're checking (using min/max naming consistently, plus sat)
        all_criteria = [
            "ymin", "ymax", "umin", "umax", "vmin", "vmax", "sat"
        ]
        
        # Get failing frames information
        failing_frames_text, fail_counts = get_failing_frametimes(
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


def process_file(input_path: str, output_path: str = 'input') -> dict:
    """
    Process a video file and generate QC reports.
    Returns a dictionary with processing results.
    """
    try:
        path = Path(input_path)
        print(f"Processing file: {path.name}")
        
        # Call the main processing function
        processfile(str(path), output_path)
        
        # Generate report paths
        base_name = path.stem.replace('.mkv.qctools', '').replace('.xml', '').replace('.json', '')
        output_dir = path.parent if output_path == 'input' else Path(output_path)
        video_report = output_dir / f"{base_name}_video_level_report.txt"
        detailed_report = output_dir / f"{base_name}_failing_frames_by_criteria.txt"
        
        return {
            'success': True,
            'filename': path.name,
            'path': str(path),
            'size': path.stat().st_size,
            'extension': path.suffix.lower(),
            'report_path': str(video_report),
            'detailed_report_path': str(detailed_report)
        }
        
    except Exception as e:
        print(f"Error processing {input_path}:")
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


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
        supported_exts = (".xml", ".csv", ".mkv", ".mov", ".mp4", ".avi", ".mxf", ".dv")
        
        files_to_process = [
            os.path.join(inputPath, fname)
            for fname in os.listdir(inputPath)
            if os.path.isfile(os.path.join(inputPath, fname)) 
            and fname.lower().endswith(supported_exts)
        ]
        
        if not files_to_process:
            print(f"No supported files found in {inputPath}")
            return
        
        print(f"Found {len(files_to_process)} files to process")
        
        # Adaptive worker calculation based on CPU cores
        cpu_count = multiprocessing.cpu_count()
        
        if cpu_count <= 4:
            max_workers = 1
        elif cpu_count <= 8:
            max_workers = 2
        elif cpu_count <= 16:
            max_workers = 3
        else:
            max_workers = 4
        
        print(f"Detected {cpu_count} CPU cores - using {max_workers} parallel worker(s)")
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
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

__all__ = ['processfile', 'process_file']