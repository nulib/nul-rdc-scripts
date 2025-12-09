#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import subprocess
import datetime
import json
from nulrdcscripts.aproc.params import args
import nulrdcscripts.aproc.helpers as helpers
import nulrdcscripts.aproc.corefuncs as corefuncs

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")


class ProcessingError(Exception):
    """Custom exception for clear error reporting"""
    pass


def detect_input_structure(input_path, file_extension=".wav"):
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
    
    # Check for files directly in input directory
    direct_files = glob.glob(os.path.join(input_path, f"*{file_extension}"))
    direct_files = [f for f in direct_files if not os.path.basename(f).startswith('.')]
    
    # Check for subdirectories with files
    subdirs = [d for d in os.listdir(input_path) 
               if os.path.isdir(os.path.join(input_path, d)) 
               and not d.startswith('.')]
    
    subdir_files = {}
    for subdir in subdirs:
        subdir_path = os.path.join(input_path, subdir)
        
        # Check for files directly in subdir
        files_in_subdir = glob.glob(os.path.join(subdir_path, f"*{file_extension}"))
        
        # Check for files in p/ subfolder
        p_folder = os.path.join(subdir_path, 'p')
        files_in_p = []
        if os.path.isdir(p_folder):
            files_in_p = glob.glob(os.path.join(p_folder, f"*{file_extension}"))
        
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
                if not f.startswith('.'):
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
    Returns updated file paths and their parent directories.
    """
    organized_items = []
    changes_made = []
    
    if detection_result['mode'] == 'single':
        # Single mode - create object folder structure
        base_dir = detection_result['base_dir']
        
        for file_path in detection_result['files']:
            filename = os.path.basename(file_path)
            file_base, ext = os.path.splitext(filename)
            
            # Check if already in organized structure
            parent_dir = os.path.dirname(file_path)
            if filename.endswith(f'_{pm_identifier}{ext}') and os.path.basename(parent_dir) == pm_identifier:
                organized_items.append({'file': file_path, 'base_dir': os.path.dirname(parent_dir)})
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
                
            organized_items.append({'file': new_path, 'base_dir': base_dir})
    
    else:  # batch mode
        for subdir, info in detection_result['subdirs'].items():
            subdir_path = os.path.join(detection_result['base_dir'], subdir)
            p_folder = os.path.join(subdir_path, pm_identifier)
            
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
                        organized_items.append({'file': new_path, 'base_dir': subdir_path})
                    else:
                        organized_items.append({'file': file_path, 'base_dir': subdir_path})
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
                    organized_items.append({'file': new_path, 'base_dir': subdir_path})
    
    if changes_made:
        print(f"\n📁 File organization changes:")
        for change in changes_made:
            print(change)
        print()
    
    return organized_items


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
    preservation_extension = ".wav"
    access_extension = ".wav"
    inventoryName = "transcode_inventory.csv"

    # assign mediaconch policies to use  
    if not args.input_policy:
        p_wav_policy = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/mediaconch_policies/preservation_wav-96k24-tech.xml",
        )
    else:
        p_wav_policy = args.input_policy
    if not args.output_policy:
        a_wav_policy = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/mediaconch_policies/access_wav-44k16-tech.xml",
        )
    else:
        a_wav_policy = args.output_policy
    bwf_policy = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "data/mediaconch_policies/wav-bwf.xml"
    )
    
    try:
        # Step 1: Detect input structure
        print("\n" + "="*80)
        print("ANALYZING INPUT DIRECTORY")
        print("="*80)
        
        indir = corefuncs.input_check()
        detection = detect_input_structure(indir, preservation_extension)
        
        # Step 2: Auto-organize files
        print("\n📁 Organizing files...")
        organized_items = organize_files(detection, pm_identifier='p', add_p_suffix=True)
        
        # Step 3: Set up output
        if args.output_path:
            qc_csv_file = args.output_path
        else:
            base_folder_name = os.path.basename(indir)
            qc_csv_file = os.path.join(indir, base_folder_name + "-qc_log.csv")
        corefuncs.output_check(qc_csv_file)
        
        # Step 4: Check that required programs are present
        corefuncs.mediaconch_check()
        corefuncs.ffprobe_check()
        if args.transcode:
            ffvers = corefuncs.get_ffmpeg_version()
        if args.write_bwf_metadata:
            metaedit_version = corefuncs.get_bwf_metaedit_version()
        sox_version = corefuncs.get_sox_version()

        # verify that mediaconch policies are present
        corefuncs.mediaconch_policy_exists(p_wav_policy)
        corefuncs.mediaconch_policy_exists(a_wav_policy)

        # Step 5: Check inventory
        print("\n📋 Checking inventory...")
        if args.source_inventory:
            source_inventories = args.source_inventory
            source_inventory_dict = helpers.import_inventories(
                source_inventories, args.skip_coding_history
            )
        else:
            print("\n*** Checking input directory for CSV files ***")
            source_inventories = glob.glob(os.path.join(indir, "*.csv"))
            source_inventories = [i for i in source_inventories if not ("qc_log.csv" in i or "ingest.csv" in i) ]
            if not source_inventories:
                print("\n⚠️  WARNING: Unable to find CSV inventory file")
                print("   The script will continue but some metadata fields will be empty")
                print("   CONTINUE? (y/n)")
                yes = {"yes", "y", "ye", ""}
                no = {"no", "n"}
                choice = input().lower()
                if choice in yes:
                    source_inventory_dict = {}
                elif choice in no:
                    sys.exit(0)
                else:
                    print("Please respond with 'yes' or 'no'")
                    sys.exit(0)
            else:
                print(f"✓ Using inventory: {os.path.basename(source_inventories[0])}")
                source_inventory_dict = helpers.import_inventories(
                    source_inventories, args.skip_coding_history
                )

        csvHeaderList = [
            "filename",
            "shot sheet check",
            "date",
            "file format & metadata verification",
            "date",
            "file inspection",
            "date",
            "QC notes",
            "runtime",
        ]
        
        # Step 6: Print processing summary
        steps_enabled = {
            'Create access copies': args.transcode,
            'Embed BWF metadata': args.write_bwf_metadata,
            'Generate JSON files': args.write_json,
            'Generate spectrograms': args.spectrogram,
        }
        
        if args.reembed_only:
            print("NOTE: Using existing access copies (no re-transcoding)")
        
        print_processing_summary(detection, steps_enabled)
        
        print("🔄 Starting processing...\n")

        # load bwf metadata into dictionary
        if args.write_bwf_metadata:
            bwf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bwf_metadata.json")
            with open(bwf_file) as standard_metadata:
                bwf_dict = json.load(standard_metadata)

        # Step 7: Process files
        for item in organized_items:
            pm_file_abspath = item['file']
            object_folder_abspath = item['base_dir']
            file = os.path.basename(pm_file_abspath)
            
            if not file.endswith(pm_identifier + preservation_extension):
                print(f"⚠️  WARNING: {file} doesn't end with expected pattern, skipping")
                continue
            
            base_filename = file.replace(pm_identifier + preservation_extension, "")
            
            ac_folder_abspath = os.path.join(object_folder_abspath, ac_identifier)
            ac_file_abspath = os.path.join(
                ac_folder_abspath, base_filename + ac_identifier + access_extension
            )
            meta_folder_abspath = os.path.join(
                object_folder_abspath, metadata_identifier
            )
            pm_md5_abspath = pm_file_abspath.replace(preservation_extension, ".md5")
            ac_md5_abspath = ac_file_abspath.replace(access_extension, ".md5")

            print("="*80)
            print(f"Processing {file}")
            print("="*80)

            # load inventory metadata related to the file
            loaded_metadata = helpers.load_item_metadata(
                file, source_inventory_dict
            )
            # loading inventory metadata means the item was found in the inventory
            inventory_check = "PASS"
            inventory_filename = []
            for key in loaded_metadata:
                inventory_filename.append(key)
            inventory_filename = "".join(inventory_filename)

            # json filename should use the filename found in the inventory
            json_file_abspath = os.path.join(
                meta_folder_abspath,
                inventory_filename + "_s" + ".json",
            )

            # generate ffprobe metadata from input
            input_metadata = helpers.ffprobe_report(
                file, pm_file_abspath
            )

            # embed BWF metadata
            if args.write_bwf_metadata:
                print("*embedding BWF metadata*")
                inventory_bwf_metadata = loaded_metadata[inventory_filename][
                    "BWF Metadata"
                ]
                source_format = inventory_bwf_metadata["format"].lower()
                bwf_dict["ISRF"]["write"] = source_format
                coding_history = inventory_bwf_metadata["coding history"]
                if input_metadata["file metadata"]["channels"] == 1:
                    file_sound_mode = "mono"
                elif input_metadata["file metadata"]["channels"] == 2:
                    file_sound_mode = "stereo"
                else:
                    pass
                # if coding history was created
                if coding_history:
                    coding_history_update = (
                        "A=PCM,F="
                        + input_metadata["file metadata"]["audio sample rate"]
                        + ",W="
                        + input_metadata["file metadata"]["audio bitrate"]
                        + ",M="
                        + file_sound_mode
                        + ",T=BWFMetaEdit "
                        + metaedit_version
                    )
                    coding_history = coding_history + "\r\n" + coding_history_update
                    bwf_dict["CodingHistory"]["write"] = coding_history

                bwf_command = [
                    args.metaedit_path,
                    pm_file_abspath,
                    "--MD5-Embed",
                    "--BextVersion=1",
                ]
                for key in bwf_dict:
                    if bwf_dict[key]["write"]:
                        bwf_command += [
                            bwf_dict[key]["command"] + bwf_dict[key]["write"]
                        ]
                subprocess.run(bwf_command)

                # create checksum sidecar file for preservation master (only if not reembed-only mode)
                if not args.reembed_only:
                    print("*creating checksum for preservation file*")
                    pm_hash = corefuncs.hashlib_md5(pm_file_abspath)
                    with open(pm_md5_abspath, "w", newline="\n") as f:
                        print(pm_hash, "*" + file, file=f)

            if args.transcode:
                print("*transcoding access file*")
                helpers.create_output_folder(ac_folder_abspath)
                ffmpeg_command = [
                    args.ffmpeg_path,
                    "-loglevel",
                    "error",
                    "-i",
                    pm_file_abspath,
                ]
                ffmpeg_command += [
                    "-af",
                    "aresample=resampler=soxr",
                    "-ar",
                    "44100",
                    "-c:a",
                    "pcm_s16le",
                    ac_file_abspath,
                ]
                subprocess.run(ffmpeg_command)
                # generate md5 for access file
                print("*creating checksum for access file*")
                acHash = corefuncs.hashlib_md5(ac_file_abspath)
                with open(os.path.join(ac_md5_abspath), "w", newline="\n") as f:
                    print(
                        acHash,
                        "*" + base_filename + ac_identifier + access_extension,
                        file=f,
                    )
            
            # embed BWF metadata for access file (if it exists or was just created)
            if args.write_bwf_metadata and os.path.isfile(ac_file_abspath):
                print("*embedding BWF metadata in access file*")
                
                try:
                    inventory_bwf_metadata = loaded_metadata[inventory_filename][
                        "BWF Metadata"
                    ]
                    source_format = inventory_bwf_metadata["format"].lower()
                    bwf_dict["ISRF"]["write"] = source_format
                    
                    # Get metadata from access file
                    access_metadata = helpers.ffprobe_report(
                        base_filename + ac_identifier + access_extension, ac_file_abspath
                    )
                    
                    coding_history = inventory_bwf_metadata["coding history"]
                    if access_metadata["file metadata"]["channels"] == 1:
                        file_sound_mode = "mono"
                    elif access_metadata["file metadata"]["channels"] == 2:
                        file_sound_mode = "stereo"
                    else:
                        file_sound_mode = "unknown"
                    
                    # if coding history was created, add access file processing
                    if coding_history:
                        # Ensure all values are strings
                        sample_rate = str(access_metadata["file metadata"]["audio sample rate"])
                        bitrate = str(access_metadata["file metadata"]["audio bitrate"])
                        
                        coding_history_update = (
                            "A=PCM,F="
                            + sample_rate
                            + ",W="
                            + bitrate
                            + ",M="
                            + file_sound_mode
                            + ",T=BWFMetaEdit "
                            + metaedit_version
                        )
                        coding_history = coding_history + "\r\n" + coding_history_update
                        bwf_dict["CodingHistory"]["write"] = coding_history

                    bwf_command = [
                        args.metaedit_path,
                        ac_file_abspath,
                        "--MD5-Embed",
                        "--BextVersion=1",
                    ]
                    for key in bwf_dict:
                        if bwf_dict[key]["write"]:
                            bwf_command += [
                                bwf_dict[key]["command"] + bwf_dict[key]["write"]
                            ]
                    subprocess.run(bwf_command)
                    print("  ✓ Access file BWF metadata embedded")
                    
                except Exception as e:
                    print(f"  ⚠️  Warning: Could not embed BWF metadata in access file: {str(e)}")
                    if args.verbose:
                        import traceback
                        traceback.print_exc()

            # create folder for metadata if needed
            if args.spectrogram or args.write_json:
                helpers.create_output_folder(
                    meta_folder_abspath
                )

            # create spectrogram for pm audio channels
            if args.spectrogram:
                print("*generating QC spectrograms*")
                sox_spectrogram_command = [
                    args.sox_path,
                    pm_file_abspath,
                    "-n",
                    "spectrogram",
                    "-Y",
                    "1080",
                    "-x",
                    "1920",
                    "-o",
                    os.path.join(
                        meta_folder_abspath, base_filename + "spectrogram_s.png"
                    ),
                ]
                subprocess.run(sox_spectrogram_command)

            # create a dictionary with the mediaconch results
            print("*Running MediaConch on Preservation and Access files*")
            mediaconchResults_dict = {
                "Preservation Format Policy": helpers.mediaconch_policy_check(
                    pm_file_abspath, p_wav_policy
                ),
                "Preservation BWF Policy": helpers.mediaconch_policy_check(
                    pm_file_abspath, bwf_policy
                ),
            }
            
            # Check access file if it exists
            if os.path.isfile(ac_file_abspath):
                mediaconchResults_dict.update({
                    "Access Format Policy": helpers.mediaconch_policy_check(
                        ac_file_abspath, a_wav_policy
                    ),
                    "Access BWF Policy": helpers.mediaconch_policy_check(
                        ac_file_abspath, bwf_policy
                    ),
                })
            
            # PASS/FAIL - check if any mediaconch results failed and append failed policies to results
            mediaconchResults = (
                helpers.parse_mediaconchResults(
                    mediaconchResults_dict
                )
            )

            # create a dictionary containing QC results
            qcResults = helpers.qc_results(
                inventory_check, mediaconchResults
            )

            if args.write_json:
                bwf_meta_dict = helpers.get_bwf_metadata(
                    pm_file_abspath
                )
                file_dict = {file: {}}
                file_dict[file].update(
                    {"Technical Metadata": input_metadata["file metadata"]}
                )
                file_dict[file].update({"BWF Metadata": bwf_meta_dict})
                file_dict[file].update(qcResults)
                output_metadata = loaded_metadata[inventory_filename][
                    "Inventory Metadata"
                ]
                if "Preservation Files" not in output_metadata:
                    output_metadata["Preservation Files"] = [file_dict]
                else:
                    output_metadata["Preservation Files"].append(file_dict)
                with open(json_file_abspath, "w", newline="\n") as outfile:
                    json.dump(output_metadata, outfile, indent=4)

            # get current date for logging when QC happened
            qcDate = str(datetime.datetime.today().strftime("%Y-%m-%d"))

            # create the list that will go in the qc log csv file
            csvWriteList = [
                file,
                qcResults["QC"]["inventory check"],
                qcDate,
                qcResults["QC"]["mediaconch results"],
                qcDate,
                None,
                None,
                None,
                helpers.convert_runtime(
                    input_metadata["file metadata"]["duration"]
                ),
            ]

            # Add QC results to QC log csv file
            helpers.write_output_csv(
                qc_csv_file, csvHeaderList, csvWriteList, qcResults
            )
            
            print(f"✓ Successfully processed {file}\n")

        print("\n" + "="*80)
        print("✅ PROCESSING COMPLETE")
        print("="*80)
        print(f"\nResults saved to: {qc_csv_file}")
        print("Check the QC log for any FAIL entries that need attention\n")

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


if __name__ == "__main__":
    main()