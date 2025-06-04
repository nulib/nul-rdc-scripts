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

# --- Move these globals here ---
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
# ...existing imports and globals...

indir = corefuncs.input_check()
outdir = corefuncs.output_check(indir)
helpers.check_mixdown_arg()
if not args.skip_qcli:
    corefuncs.qcli_check()
corefuncs.mediaconch_check()
corefuncs.ffprobe_check()
ffvers = corefuncs.get_ffmpeg_version()
corefuncs.mediaconch_policy_exists(mkvPolicy)
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
# --- End globals ---

# TO DO: general cleanup

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")


def main():
    # the pm identifier is the name of the folder that the preservation file will be output to
    global pm_identifier
    pm_identifier = "p"
    # the ac identifier will be used as the folder name for the access file
    # it will also be appended to the end of the access copy filename
    global ac_identifier
    ac_identifier = "a"
    global metadata_identifier
    metadata_identifier = "meta"
    # identifier appended to the end of the MKV preservation file
    # Replace with "None" to keep the name the same as the input
    global pm_filename_identifier
    if not args.keep_filename:
        pm_filename_identifier = "_p"
    else:
        pm_filename_identifier = None
    global inventoryName
    inventoryName = "transcode_inventory.csv"
    # assign mediaconch policies to use
    global mkvPolicy
    if not args.output_policy:
        mkvPolicy = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/mediaconch_policies/MKVFFV1_policy.xml",
        )
    else:
        mkvPolicy = args.output_policy
 

    print("***STARTING PROCESS***")

    if args.batch:
        batch_video(indir, outdir)
    else:
        single_video(indir, outdir)


def batch_video(input, output):
    items_to_process = []
    skipped_items = []

    for item in os.listdir(input):
        item_path = os.path.join(input, item)
        qc_log_path = os.path.join(item_path, "qc_log.csv")
        if not os.path.isdir(item_path):
            skipped_items.append((item, "not a directory"))
            continue
        if os.path.isfile(qc_log_path):
            skipped_items.append((item, "qc_log.csv exists"))
            continue

        # Check for valid .mkv files
        mkv_files = [f for f in glob.glob1(item_path, "*.mkv")]
        valid_mkv = False
        for mkv in mkv_files:
            mkv_path = os.path.join(item_path, mkv)
            baseFilename = mkv.replace("_p.mkv", "").replace(".mkv", "")
            if not os.path.isfile(mkv_path) or os.path.getsize(mkv_path) == 0:
                skipped_items.append((f"{item}/{mkv}", "malformed (missing or empty)"))
                continue
            if baseFilename not in csvDict:
                skipped_items.append((f"{item}/{mkv}", "not in CSV inventory"))
                continue
            valid_mkv = True
        if valid_mkv:
            items_to_process.append(item_path)
        elif not mkv_files:
            skipped_items.append((item, "no .mkv files found"))

    print("Folders to be transcoded:")
    for item in items_to_process:
        print(f"  {item}")

    if skipped_items:
        print("\nSkipped folders/files:")
        for item, reason in skipped_items:
            print(f"  {item}: {reason}")

    print(f"\nBatch processing {len(items_to_process)} video folders in parallel...")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(single_video, item, item)
            for item in items_to_process
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Batch item generated an exception: {exc}")


def single_video(input, output):
    for preservationFilename in glob.glob1(input, "*.mkv"):
        # Skip files with "qctools" in the filename
        if "qctools" in preservationFilename.lower():
            print(f"Skipping {preservationFilename} (contains 'qctools' in filename)")
            continue

        preservationAbsPath = os.path.join(input, preservationFilename)
        if not os.path.isfile(preservationAbsPath) or os.path.getsize(preservationAbsPath) == 0:
            print(f"ERROR: {preservationAbsPath} is missing or empty. Skipping.")
            continue

        baseFilename = preservationFilename.replace("_p.mkv", "").replace(".mkv", "")
        baseOutput = os.path.join(output, baseFilename)
        preservationOutputFolder = os.path.join(baseOutput, pm_identifier)
        # Ensure the preservation folder exists
        if not os.path.isdir(preservationOutputFolder):
            os.makedirs(preservationOutputFolder, exist_ok=True)

        # Determine the correct destination path for the _p.mkv file
        preservationDestPath = os.path.join(preservationOutputFolder, baseFilename + "_p.mkv")

        # If the file is not already in the correct location/name, move/rename it
        if preservationAbsPath != preservationDestPath:
            # If the file does not already have the _p.mkv suffix, rename it
            if not preservationFilename.endswith("_p.mkv"):
                newPresAbsPath = preservationAbsPath.replace(".mkv", "_p.mkv")
                os.rename(preservationAbsPath, newPresAbsPath)
                preservationAbsPath = newPresAbsPath
            # Move to the preservation folder if not already there
            if os.path.abspath(preservationAbsPath) != os.path.abspath(preservationDestPath):
                os.rename(preservationAbsPath, preservationDestPath)
                preservationAbsPath = preservationDestPath

        # Now, preservationAbsPath points to the correct file in the p folder
        baseFilename = preservationFilename.replace("_p.mkv", "")
        baseOutput = os.path.join(output, baseFilename)
        preservationOutputFolder = os.path.join(baseOutput, pm_identifier)
        accessOutputFolder = os.path.join(baseOutput, ac_identifier)
        accessAbsPath = os.path.join(
            accessOutputFolder, baseFilename + "_" + ac_identifier + ".mp4"
        )
        accessFilename = baseFilename + "_" + ac_identifier + ".mp4"
        metaOutputFolder = os.path.join(baseOutput, metadata_identifier)
        jsonAbsPath = os.path.join(metaOutputFolder, baseFilename + "_s" + ".json")

        # generate ffprobe metadata from input
        preservation_metadata = helpers.ffprobe_report(
            preservationFilename, preservationAbsPath
        )

        # create a list of needed output folders and make them
        if not args.skip_ac:
            outFolders = [
                preservationOutputFolder,
                accessOutputFolder,
                metaOutputFolder,
            ]
        else:
            outFolders = [preservationOutputFolder, metaOutputFolder]
        helpers.create_transcode_output_folders(baseOutput, outFolders)

        # get information about item from csv inventory
        print("*checking inventory for", baseFilename + "*")
        item_csvDict = csvDict.get(baseFilename)
        # PASS/FAIL - was the file found in the inventory
        inventoryCheck = checks.inventory_check(item_csvDict)

        # log transcode start time
        tstime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        # losslessly transcode with ffmpeg
        transcode_nameDict = {
            "inputAbsPath": preservationAbsPath,
            "outputAbsPath": accessAbsPath,
        }
        audioStreamCounter = preservation_metadata["techMetaA"]["audio stream count"]
        # log transcode finish time
        tftime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        if not args.skip_ac:
            # create access copy
            print("*transcoding access copy*")
            logfile = accessAbsPath + ".log"
            helpers.two_pass_h264_encoding(
                audioStreamCounter, preservationAbsPath, accessAbsPath, logfile=accessAbsPath + ".log"
            )
            print("*successfully transcoded access copy*")

        # log access copy filename if access copy was created
        # TO DO: verify that access copy runtime matches pm runtime?
        if os.path.isfile(accessAbsPath):
            acFilename = baseFilename + "_" + ac_identifier + ".mp4"
        else:
            acFilename = "No access copy found"

        # If access file was succesfully created, do remaining verification and transcoding work
        if os.path.isfile(accessAbsPath):
            mediaconchResults_dict = {
                "MKV Implementation": helpers.mediaconch_implementation_check(
                    preservationAbsPath
                ),
                "MKV Mediaconch Policy": helpers.mediaconch_policy_check(
                    preservationAbsPath, mkvPolicy
                ),
            }
            # TEMP DEBUG: Print MKV policy check result
            mediaconch_policy_output = helpers.mediaconch_policy_check(preservationAbsPath, mkvPolicy, debug=True)
            print(f"DEBUG: MKV Mediaconch Policy check output for {preservationAbsPath}:\n{mediaconch_policy_output}")
            # PASS/FAIL - check if any mediaconch results failed and append failed policies to results
            mediaconchResults = checks.parse_mediaconchResults(mediaconchResults_dict)

            # run ffprobe on the output file
            access_metadata = helpers.ffprobe_report(accessFilename, accessAbsPath)
            # log system info
            systemInfo = helpers.generate_system_log(ffvers, tstime, tftime)
            # create a dictionary containing QC results
            qcResults = helpers.qc_results(inventoryCheck, mediaconchResults)

            encoding_chain = helpers.generate_coding_history(csvDict, baseFilename)
            # create json metadata file
            # TO DO: combine checksums into a single dictionary to reduce variables needed here
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
            # should correspond to the csvHeaderList earlier in the script
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
                helpers.convert_runtime(
                    preservation_metadata["file metadata"]["duration"]
                ),
            ]

            # Add QC results to QC log csv file
            csvfunctions.write_output_csv(
                output, csvHeaderList, csvWriteList, preservation_metadata, qcResults
            )

            # create spectrogram for pm audio channels
            if audioStreamCounter > 0 and not args.skip_spectrogram:
                print("*generating QC spectrograms*")
                channel_layout_list = preservation_metadata["techMetaA"]["channels"]
                helpers.generate_spectrogram(
                    preservationAbsPath,
                    channel_layout_list,
                    metaOutputFolder,
                    baseFilename,
                )

        else:
            print("No file in output folder.  Skipping file processing")


# TO DO: (low/not priority) add ability to automatically pull trim times from CSV (-ss 00:00:02 -t 02:13:52)?
# import time
# timeIn = [get csv time1]
# timeOut = [get csv time2]
# t1 = datetime.datetime.strptime(timeIn, "%H:%M:%S")
# t2 = datetime.datetime.strptime(timeOut, "%H:%M:%S")
# trimtime = time.strftime('%H:%M:%S', time.gmtime(((60 * ((60 * t2.hour) + t2.minute)) + t2.second) - ((60 * ((60 * t1.hour) + t1.minute)) + t1.second)))

if __name__ == "__main__":
    main()
