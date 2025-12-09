#!/usr/bin/env python3

"""
Functions that will be in multiple scripts
Handle things like: 
input, output, checksumming, checking that software exists, etc.
"""

import os
import hashlib
import sys
import subprocess
from nulrdcscripts.vproc.params import args


def input_check():
    """
    Checks if input was provided and if it is a directory that exists
    """
    if args.input_path:
        indir = args.input_path
    else:
        print("No input provided, using current directory as input")
        indir = os.getcwd()

    if not os.path.isdir(indir):
        print("input is not a directory")
        quit()
    return indir


def output_check(indir):
    """
    Checks if output was provided and if it is a directory that exists
    If no output is provided, output folder will default to input
    """
    if args.output_path:
        outdir = args.output_path
    else:
        print("Output not specified. Using input directory as Output directory")
        outdir = indir

    if not os.path.isdir(outdir):
        print("output is not a directory")
        quit()
    return outdir


def mediaconch_policy_exists(policy_path):
    """
    checks that the specified mediaconch policy exists
    """
    if not os.path.isfile(policy_path):
        print("unable to find mediaconch policy:", policy_path)
        print("Check if file exists before running")
        quit()


def ffprobe_check():
    """
    checks that ffprobe exists by running its -version command
    """
    try:
        subprocess.check_output([args.ffprobe_path, "-version"]).decode(
            "ascii"
        ).rstrip().splitlines()[0].split()[2]
    except:
        print("Error locating ffprobe")
        quit()


def mediaconch_check():
    """
    checks that mediaconch exists by running its -v command
    """
    try:
        subprocess.check_output([args.mediaconch_path, "-v"]).decode(
            "ascii"
        ).rstrip().splitlines()[0]
    except:
        print("Error locating mediaconch")
        quit()


def qcli_check():
    """
    checks that qcli exists by running its -version command
    """
    try:
        subprocess.check_output([args.qcli_path, "-version"]).decode(
            "ascii"
        ).rstrip().splitlines()[0]
    except:
        print("Error locating qcli")
        quit()


def get_ffmpeg_version():
    """
    Returns the version of ffmpeg
    """
    ffmpeg_version = "ffmpeg"
    try:
        ffmpeg_version = (
            subprocess.check_output([args.ffmpeg_path, "-version"])
            .decode("ascii")
            .rstrip()
            .splitlines()[0]
            .split()[2]
        )
    except:
        print("Error getting ffmpeg version")
        quit()
    return ffmpeg_version

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
    import glob
    
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
    Returns updated file paths.
    """
    import glob
    
    organized_files = []
    changes_made = []
    
    if detection_result['mode'] == 'single':
        # Single mode - create object folder if needed
        for file_path in detection_result['files']:
            filename = os.path.basename(file_path)
            file_base, ext = os.path.splitext(filename)
            
            # Check if already in organized structure
            if filename.endswith(f'_{pm_identifier}{ext}') and 'p' in os.path.dirname(file_path):
                organized_files.append(file_path)
                print(f"  ✓ {filename} - already organized")
                continue
            
            # Create p/ folder if needed
            p_folder = os.path.join(detection_result['base_dir'], pm_identifier)
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
                organized_files.append(new_path)
            else:
                organized_files.append(file_path)
    
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
                        organized_files.append(new_path)
                    else:
                        organized_files.append(file_path)
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
                    organized_files.append(new_path)
    
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