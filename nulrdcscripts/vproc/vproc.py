#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import subprocess
import datetime
import concurrent.futures
from nulrdcscripts.vproc.params import args
import nulrdcscripts.vproc.helpers as helpers
import nulrdcscripts.vproc.corefuncs as corefuncs
import nulrdcscripts.vproc.checks as checks
import nulrdcscripts.vproc.metadata as metadata
import nulrdcscripts.vproc.csvfunctions as csvfunctions

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")


class ProcessingError(Exception):
    """Custom exception for clear error reporting"""
    pass


def detect_input_structure(input_path, file_extension=".mkv"):
    """
    Auto-detect input structure and return processing mode.
    
    Returns:
        dict with:
            - mode: 'single' or 'batch'
            - files: list of files to process
            - structure: 'flat', 'organized', or 'mixed'
    """
    if not os.path.isdir(input_path):
        raise ProcessingError(
            f"❌ INPUT ERROR: '{input_path}' is not a valid directory\n"
            f"   Please provide a valid directory path using --input or -i"
        )
    
    # Check for files directly in input directory (skip qctools files)
    direct_files = glob.glob(os.path.join(input_path, f"*{file_extension}"))
    direct_files = [f for f in direct_files 
                    if not os.path.basename(f).startswith('.') 
                    and 'qctools' not in f.lower()]
    
    # Check for subdirectories with files
    subdirs = [d for d in os.listdir(input_path) 
               if os.path.isdir(os.path.join(input_path, d)) 
               and not d.startswith('.')]
    
    subdir_files = {}
    for subdir in subdirs:
        subdir_path = os.path.join(input_path, subdir)
        
        # Check for files directly in subdir
        files_in_subdir = glob.glob(os.path.join(subdir_path, f"*{file_extension}"))
        files_in_subdir = [f for f in files_in_subdir if 'qctools' not in f.lower()]
        
        # Check for files in p/ subfolder
        p_folder = os.path.join(subdir_path, 'p')
        files_in_p = []
        if os.path.isdir(p_folder):
            files_in_p = glob.glob(os.path.join(p_folder, f"*{file_extension}"))
            files_in_p = [f for f in files_in_p if 'qctools' not in f.lower()]
        
        all_files = files_in_subdir + files_in_p
        if all_files:
            subdir_files[subdir] = {
                'direct': files_in_subdir,
                'in_p_folder': files_in_p,
                'all': all_files
            }
    
    # Determine mode and structure
    if direct_files and not subdir_files:
        # Single object mode
        print(f"✓ Detected: SINGLE object with {len(direct_files)} {file_extension} file(s)")
        return {
            'mode': 'single',
            'files': direct_files,
            'structure': 'flat',
            'base_dir': input_path
        }
    
    elif not direct_files and subdir_files:
        # Batch mode
        total_files = sum(len(info['all']) for info in subdir_files.values())
        print(f"✓ Detected: BATCH mode with {len(subdir_files)} object(s) containing {total_files} {file_extension} file(s)")
        
        has_p_folders = any(info['in_p_folder'] for info in subdir_files.values())
        has_direct = any(info['direct'] for info in subdir_files.values())
        
        if has_p_folders and not has_direct:
            structure = 'organized'
        elif has_direct and not has_p_folders:
            structure = 'flat'
        else:
            structure = 'mixed'
        
        return {
            'mode': 'batch',
            'subdirs': subdir_files,
            'structure': structure,
            'base_dir': input_path
        }
    
    elif direct_files and subdir_files:
        raise ProcessingError(
            f"❌ STRUCTURE ERROR: Found {file_extension} files both in root directory AND subdirectories\n"
            f"   Found in root: {len(direct_files)} file(s)\n"
            f"   Found in subdirs: {len(subdir_files)} folder(s)\n\n"
            f"   Please organize your files in ONE of these ways:\n"
            f"   1. All files in root directory (single object)\n"
            f"   2. Separate folders for each object (batch mode)\n"
        )
    
    else:
        # No files found
        available_exts = set()
        for root, dirs, files in os.walk(input_path):
            for f in files:
                if not f.startswith('.') and 'qctools' not in f.lower():
                    ext = os.path.splitext(f)[1]
                    if ext:
                        available_exts.add(ext)
        
        if available_exts:
            raise ProcessingError(
                f"❌ NO FILES FOUND: No {file_extension} files in '{input_path}'\n"
                f"   Found these file types instead: {', '.join(sorted(available_exts))}\n"
                f"   Expected: {file_extension} files\n"
            )
        else:
            raise ProcessingError(
                f"❌ EMPTY DIRECTORY: No files found in '{input_path}'\n"
                f"   The directory appears to be empty\n"
            )


def organize_files(detection_result, pm_identifier='p', add_p_suffix=True):
    """
    Organize files into p/ subfolders and add _p suffix if needed.
    Returns list of organized file paths.
    """
    organized_files = {}
    changes_made = []
    
    if detection_result['mode'] == 'single':
        # Single mode - create p/ folder structure
        base_dir = detection_result['base_dir']
        
        for file_path in detection_result['files']:
            filename = os.path.basename(file_path)
            file_base, ext = os.path.splitext(filename)
            
            # Check if already in organized structure
            parent_dir = os.path.dirname(file_path)
            if filename.endswith(f'_{pm_identifier}{ext}') and os.path.basename(parent_dir) == pm_identifier:
                organized_files[base_dir] = [file_path]
                print(f"  ✓ {filename} - already organized")
                continue
            
            # Create p/ folder
            p_folder = os.path.join(base_dir, pm_identifier)
            if not os.path.isdir(p_folder):
                os.makedirs(p_folder, exist_ok=True)
                print(f"  Created folder: {pm_identifier}/")
            
            # Add _p suffix if needed
            if add_p_suffix and not filename.endswith(f'_{pm_identifier}{ext}'):
                new_filename = f"{file_base}_{pm_identifier}{ext}"
            else:
                new_filename = filename
            
            new_path = os.path.join(p_folder, new_filename)
            
            # Move file
            if file_path != new_path:
                os.rename(file_path, new_path)
                changes_made.append(f"  Moved: {filename} → {pm_identifier}/{new_filename}")
            
            organized_files[base_dir] = [new_path]
    
    else:  # batch mode
        for subdir, info in detection_result['subdirs'].items():
            subdir_path = os.path.join(detection_result['base_dir'], subdir)
            p_folder = os.path.join(subdir_path, pm_identifier)
            subdir_organized_files = []
            
            # If files already in p/ folder, check suffix
            if info['in_p_folder']:
                for file_path in info['in_p_folder']:
                    filename = os.path.basename(file_path)
                    file_base, ext = os.path.splitext(filename)
                    
                    # Check if needs _p suffix
                    if add_p_suffix and not filename.endswith(f'_{pm_identifier}{ext}'):
                        new_filename = f"{file_base}_{pm_identifier}{ext}"
                        new_path = os.path.join(p_folder, new_filename)
                        os.rename(file_path, new_path)
                        changes_made.append(f"  {subdir}: Renamed {filename} → {new_filename}")
                        subdir_organized_files.append(new_path)
                    else:
                        subdir_organized_files.append(file_path)
                        print(f"  ✓ {subdir}/{filename} - already organized")
            
            # Move direct files to p/ folder
            if info['direct']:
                if not os.path.isdir(p_folder):
                    os.makedirs(p_folder, exist_ok=True)
                    print(f"  Created: {subdir}/{pm_identifier}/")
                
                for file_path in info['direct']:
                    filename = os.path.basename(file_path)
                    file_base, ext = os.path.splitext(filename)
                    
                    # Add _p suffix if needed
                    if add_p_suffix and not filename.endswith(f'_{pm_identifier}{ext}'):
                        new_filename = f"{file_base}_{pm_identifier}{ext}"
                    else:
                        new_filename = filename
                    
                    new_path = os.path.join(p_folder, new_filename)
                    os.rename(file_path, new_path)
                    changes_made.append(f"  {subdir}: Moved {filename} → {pm_identifier}/{new_filename}")
                    subdir_organized_files.append(new_path)
            
            if subdir_organized_files:
                organized_files[subdir_path] = subdir_organized_files
    
    if changes_made:
        print(f"\n📁 File organization changes:")
        for change in changes_made:
            print(change)
        print()
    
    return organized_files


def print_processing_summary(detection_result, steps_enabled):
    """Print a clear summary of what will be processed."""
    print("\n" + "="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    
    if detection_result['mode'] == 'single':
        print(f"Mode:       Single object")
        print(f"Files:      {len(detection_result.get('files', []))} file(s)")
    else:
        total_files = sum(len(info['all']) for info in detection_result['subdirs'].values())
        print(f"Mode:       Batch ({len(detection_result['subdirs'])} objects)")
        print(f"Files:      {total_files} total file(s)")
    
    print(f"\nSteps to run:")
    for step, enabled in steps_enabled.items():
        status = "✓ ON " if enabled else "✗ OFF"
        print(f"  {status}  {step}")
    
    print("="*80 + "\n")


def main():
    pm_identifier = "p"
    ac_identifier = "a"
    metadata_identifier = "meta"
    if not args.keep_filename:
        pm_filename_identifier = "_p"
    else:
        pm_filename_identifier = None
    inventoryName = "transcode_inventory.csv"
    if not args.output_policy:
        mkvPolicy = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/mediaconch_policies/MKVFFV1_policy.xml",
        )
    else:
        mkvPolicy = args.output_policy

    try:
        # Step 1: Detect input structure
        print("\n" + "="*80)
        print("ANALYZING INPUT DIRECTORY")
        print("="*80)
        
        indir = corefuncs.input_check()
        outdir = corefuncs.output_check(indir)
        
        detection = detect_input_structure(indir, ".mkv")
        
        # Step 2: Auto-organize files
        print("\n📁 Organizing files...")
        organized_files = organize_files(detection, pm_identifier='p', add_p_suffix=True)
        
        # Step 3: Check required tools
        helpers.check_mixdown_arg()
        if not args.skip_qcli:
            corefuncs.qcli_check()
        corefuncs.mediaconch_check()
        corefuncs.ffprobe_check()
        ffvers = corefuncs.get_ffmpeg_version()
        corefuncs.mediaconch_policy_exists(mkvPolicy)
        
        # Step 4: Load inventory
        print("\n📋 Checking inventory...")
        csvInventory = os.path.join(indir, inventoryName)
        csvDict = csvfunctions.import_csv(csvInventory)
        
        csvHeaderList = [
            "inventory check",
            "date",
            "file format & metadata verification",
            "date",
            "file inspection",
            "date",
            "QC notes",
            "AC filename",
            "PM filename",
            "runtime",
        ]
        
        # Step 5: Print processing summary
        steps_enabled = {
            'Create access copies': not args.skip_ac,
            'Generate JSON files': True,
            'Generate spectrograms': not args.skip_spectrogram,
            'Generate QCTools reports': not args.skip_qcli,
        }
        print_processing_summary(detection, steps_enabled)
        
        print("🔄 Starting processing...\n")
        
        # Step 6: Process based on mode
        if detection['mode'] == 'single':
            # Process single mode
            for base_dir, files in organized_files.items():
                for preservationAbsPath in files:
                    process_single_file(
                        preservationAbsPath, base_dir, outdir, 
                        pm_identifier, ac_identifier, metadata_identifier,
                        csvDict, csvHeaderList, mkvPolicy, ffvers
                    )
        else:
            # Process batch mode with parallel processing
            items_to_process = []
            for base_dir, files in organized_files.items():
                if files:
                    items_to_process.append(base_dir)
            
            print(f"Batch processing {len(items_to_process)} video object(s) in parallel...\n")
            
            with concurrent.futures.ProcessPoolExecutor() as executor:
                futures = [
                    executor.submit(process_batch_item, item, item, pm_identifier, ac_identifier, 
                                  metadata_identifier, csvDict, csvHeaderList, mkvPolicy, ffvers)
                    for item in items_to_process
                ]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as exc:
                        print(f"Batch item generated an exception: {exc}")
        
        print("\n" + "="*80)
        print("✅ PROCESSING COMPLETE")
        print("="*80)
        print(f"\nCheck QC logs in each object folder for FAIL entries that need attention\n")

    except ProcessingError as e:
        print(f"\n{str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print("   Run with --verbose flag for more details")
        sys.exit(1)


def process_single_file(preservationAbsPath, input_dir, output_dir, 
                       pm_identifier, ac_identifier, metadata_identifier,
                       csvDict, csvHeaderList, mkvPolicy, ffvers):
    """Process a single video file"""
    
    preservationFilename = os.path.basename(preservationAbsPath)
    
    # Skip if file doesn't exist or is empty
    if not os.path.isfile(preservationAbsPath) or os.path.getsize(preservationAbsPath) == 0:
        print(f"ERROR: {preservationAbsPath} is missing or empty. Skipping.")
        return
    
    baseFilename = preservationFilename.replace("_p.mkv", "").replace(".mkv", "")
    baseOutput = os.path.join(output_dir, baseFilename)
    preservationOutputFolder = os.path.join(baseOutput, pm_identifier)
    accessOutputFolder = os.path.join(baseOutput, ac_identifier)
    accessAbsPath = os.path.join(accessOutputFolder, baseFilename + "_" + ac_identifier + ".mp4")
    accessFilename = baseFilename + "_" + ac_identifier + ".mp4"
    metaOutputFolder = os.path.join(baseOutput, metadata_identifier)
    jsonAbsPath = os.path.join(metaOutputFolder, baseFilename + "_s" + ".json")

    print("="*80)
    print(f"Processing {preservationFilename}")
    print("="*80)

    # generate ffprobe metadata from input
    preservation_metadata = helpers.ffprobe_report(preservationFilename, preservationAbsPath)

    # create output folders
    if not args.skip_ac:
        outFolders = [preservationOutputFolder, accessOutputFolder, metaOutputFolder]
    else:
        outFolders = [preservationOutputFolder, metaOutputFolder]
    helpers.create_transcode_output_folders(baseOutput, outFolders)

    # get information about item from csv inventory
    print("*checking inventory for", baseFilename + "*")
    item_csvDict = csvDict.get(baseFilename)
    inventoryCheck = checks.inventory_check(item_csvDict)

    # log transcode times
    tstime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    audioStreamCounter = preservation_metadata["techMetaA"]["audio stream count"]
    tftime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    if not args.skip_ac:
        # create access copy
        print("*transcoding access copy*")
        logfile = accessAbsPath + ".log"
        helpers.two_pass_h264_encoding(
            audioStreamCounter, preservationAbsPath, accessAbsPath, logfile=logfile
        )
        print("*successfully transcoded access copy*")

    # log access copy filename if access copy was created
    if os.path.isfile(accessAbsPath):
        acFilename = baseFilename + "_" + ac_identifier + ".mp4"
    else:
        acFilename = "No access copy found"

    # If access file was successfully created, do remaining verification
    if os.path.isfile(accessAbsPath) or args.skip_ac:
        mediaconchResults_dict = {
            "MKV Implementation": helpers.mediaconch_implementation_check(preservationAbsPath),
            "MKV Mediaconch Policy": helpers.mediaconch_policy_check(preservationAbsPath, mkvPolicy),
        }
        
        mediaconchResults = checks.parse_mediaconchResults(mediaconchResults_dict)

        # run ffprobe on the output file if it exists
        if os.path.isfile(accessAbsPath):
            access_metadata = helpers.ffprobe_report(accessFilename, accessAbsPath)
        else:
            access_metadata = None
            
        # log system info
        systemInfo = helpers.generate_system_log(ffvers, tstime, tftime)
        
        # create a dictionary containing QC results
        qcResults = helpers.qc_results(inventoryCheck, mediaconchResults)

        encoding_chain = helpers.generate_coding_history(csvDict, baseFilename)
        
        # create json metadata file
        metadata.create_json(
            jsonAbsPath,
            systemInfo,
            preservation_metadata,
            baseFilename,
            access_metadata,
            item_csvDict,
            qcResults,
            encoding_chain,
        )

        # get current date for logging when QC happened
        qcDate = str(datetime.datetime.today().strftime("%Y-%m-%d"))

        # create the list that will go in the qc log csv file
        csvWriteList = [
            qcResults["QC"]["inventory check"],
            qcDate,
            qcResults["QC"]["mediaconch results"],
            qcDate,
            None,
            None,
            None,
            accessFilename,
            preservationFilename,
            helpers.convert_runtime(preservation_metadata["file metadata"]["duration"]),
        ]

        # Add QC results to QC log csv file
        csvfunctions.write_output_csv(
            output_dir, csvHeaderList, csvWriteList, preservation_metadata, qcResults
        )

        # create spectrogram for audio channels
        if audioStreamCounter > 0 and not args.skip_spectrogram:
            print("*generating QC spectrograms*")
            channel_layout_list = preservation_metadata["techMetaA"]["channels"]
            helpers.generate_spectrogram(
                preservationAbsPath, channel_layout_list, metaOutputFolder, baseFilename
            )
        
        print(f"✓ Successfully processed {preservationFilename}\n")


def process_batch_item(input_dir, output_dir, pm_identifier, ac_identifier, 
                      metadata_identifier, csvDict, csvHeaderList, mkvPolicy, ffvers):
    """Process a batch item (called in parallel)"""
    
    p_folder = os.path.join(input_dir, pm_identifier)
    
    # Get all MKV files in p/ folder
    mkv_files = glob.glob(os.path.join(p_folder, "*.mkv"))
    mkv_files = [f for f in mkv_files if 'qctools' not in f.lower()]
    
    if not mkv_files:
        print(f"⚠️  Skipping {os.path.basename(input_dir)} - no files in p/ folder")
        return
    
    for preservationAbsPath in mkv_files:
        process_single_file(
            preservationAbsPath, input_dir, output_dir,
            pm_identifier, ac_identifier, metadata_identifier,
            csvDict, csvHeaderList, mkvPolicy, ffvers
        )


if __name__ == "__main__":
    main()