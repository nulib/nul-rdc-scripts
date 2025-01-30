#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import subprocess
import datetime
from nulrdcscripts.vproc.params import args
import nulrdcscripts.vproc.helpers as helpers
import nulrdcscripts.vproc.corefuncs as corefuncs
import nulrdcscripts.vproc.checks as checks
import nulrdcscripts.vproc.metadata as metadata
import nulrdcscripts.vproc.csvfunctions as csvfunctions

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

    # assign input directory and output directory
    indir = corefuncs.input_check()
    outdir = corefuncs.output_check(indir)
    # check that mixdown argument is valid if provided
    helpers.check_mixdown_arg()
    # check that required programs are present
    if not args.skip_qcli:
        corefuncs.qcli_check()
    corefuncs.mediaconch_check()
    corefuncs.ffprobe_check()
    global ffvers
    ffvers = corefuncs.get_ffmpeg_version()

    # verify that mediaconch policies are present
    corefuncs.mediaconch_policy_exists(mkvPolicy)

    global csvInventory
    csvInventory = os.path.join(indir, inventoryName)
    # TO DO: separate out csv and json related functions that are currently in supportfuncs into dedicated csv or json related py files
    global csvDict
    csvDict = csvfunctions.import_csv(csvInventory)

    # create the list of csv headers that will go in the qc log csv file
    global csvHeaderList
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

    print("***STARTING PROCESS***")

    if args.batch:
        batch_video(indir, outdir)
    else:
        single_video(indir, outdir)


def batch_video(input, output):
    for item in os.listdir(input):
        # changes item's path to absolute
        item = os.path.join(input, item)
        # performs single_video on item if its a folder and hasn't been transcoded yet
        if os.path.isdir(item):
            if not os.path.isfile(os.path.join(item, "qc_log.csv")):
                single_video(item, item)


def single_video(input, output):
    for preservationFilename in glob.glob1(input, "*.mkv"):
        # create names that will be used in the script
        # TO DO: handle transcoding legacy files (either need a flag that avoids appending pm to the output filename or the ability to read the desired output filename from the CSV file
        preservationAbsPath = os.path.join(input, preservationFilename)
        # Check that the filename is correct for the mkv file. If not rename it
        if preservationAbsPath.endswith("_p.mkv"):
            pass
        else:
            newPresAbsPath = preservationAbsPath.replace(".mkv", "_p.mkv")
            preservationAbsPath = os.rename(preservationAbsPath, newPresAbsPath)

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
            helpers.two_pass_h264_encoding(
                audioStreamCounter, preservationAbsPath, accessAbsPath
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

            # create qctools report
            if args.runqcli:
                print("*Creating QCTools Report*")
                helpers.generate_qctools(preservationAbsPath)
                print("*Generated QCTools Report")
            else:
                pass

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
