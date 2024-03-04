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
import progressbar

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
    global movPolicy
    if not args.input_policy:
        movPolicy = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/mediaconch_policies/AJA_NTSC_VHS-2SAS-MOV.xml",
        )
    else:
        movPolicy = args.input_policy
    global mkvPolicy
    if not args.output_policy:
        mkvPolicy = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/mediaconch_policies/AJA_NTSC_VHS-2SAS-MKV.xml",
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
    corefuncs.mediaconch_policy_exists(movPolicy)
    corefuncs.mediaconch_policy_exists(mkvPolicy)

    global csvInventory
    csvInventory = os.path.join(indir, inventoryName)
    # TO DO: separate out csv and json related functions that are currently in supportfuncs into dedicated csv or json related py files
    global csvDict
    csvDict = helpers.import_csv(csvInventory)

    # create the list of csv headers that will go in the qc log csv file
    global csvHeaderList
    csvHeaderList = [
        "shot sheet check",
        "date",
        "PM lossless transcoding",
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
    for movFilename in glob.glob1(input, "*.mov"):
        # create names that will be used in the script
        # TO DO: handle transcoding legacy files (either need a flag that avoids appending pm to the output filename or the ability to read the desired output filename from the CSV file
        inputAbsPath = os.path.join(input, movFilename)
        baseFilename = movFilename.replace(".mov", "")
        baseOutput = os.path.join(output, baseFilename)
        pmOutputFolder = os.path.join(baseOutput, pm_identifier)
        mkvBaseFilename = (
            (baseFilename + pm_filename_identifier)
            if pm_filename_identifier
            else (baseFilename)
        )
        mkvFilename = mkvBaseFilename + ".mkv"
        outputAbsPath = os.path.join(pmOutputFolder, mkvFilename)
        tempMasterFile = os.path.join(pmOutputFolder, baseFilename + "_tmp.mkv")
        framemd5File = mkvBaseFilename + ".framemd5"
        framemd5AbsPath = os.path.join(pmOutputFolder, framemd5File)
        acOutputFolder = os.path.join(baseOutput, ac_identifier)
        acAbsPath = os.path.join(
            acOutputFolder, baseFilename + "_" + ac_identifier + ".mp4"
        )
        metaOutputFolder = os.path.join(baseOutput, metadata_identifier)
        jsonAbsPath = os.path.join(metaOutputFolder, baseFilename + "_s" + ".json")
        pmMD5AbsPath = os.path.join(pmOutputFolder, mkvBaseFilename + ".md5")

        # generate ffprobe metadata from input
        input_metadata = helpers.ffprobe_report(movFilename, inputAbsPath)

        # create a list of needed output folders and make them
        if not args.skip_ac:
            outFolders = [pmOutputFolder, acOutputFolder, metaOutputFolder]
        else:
            outFolders = [pmOutputFolder, metaOutputFolder]
        helpers.create_transcode_output_folders(baseOutput, outFolders)

        # get information about item from csv inventory
        print("*checking inventory for", baseFilename + "*")
        item_csvDict = csvDict.get(baseFilename)
        # PASS/FAIL - was the file found in the inventory
        inventoryCheck = checks.inventory_check(item_csvDict)

        print("*losslessly transcoding", baseFilename + "*")
        with progressbar.ProgressBar(max_value=100) as ffv1progbar:

            tstime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            # losslessly transcode with ffmpeg
            for i in range(100):
                transcode_nameDict = {
                    "inputAbsPath": inputAbsPath,
                    "tempMasterFile": tempMasterFile,
                    "framemd5AbsPath": framemd5AbsPath,
                    "outputAbsPath": outputAbsPath,
                    "framemd5File": framemd5File,
                }
                audioStreamCounter = input_metadata["techMetaA"]["audio stream count"]
                ffv1progbar.update(i)
                helpers.ffv1_lossless_transcode(
                    input_metadata, transcode_nameDict, audioStreamCounter
                )

                # log transcode finish time
                tftime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        # If ffv1 file was succesfully created, do remaining verification and transcoding work
        if os.path.isfile(outputAbsPath):
            # create checksum sidecar file for preservation master
            print("*creating checksum*")
            with progressbar.ProgressBar(max_value=100) as checksumffv1progbar:
                for i in range(100):
                    mkvHash = corefuncs.hashlib_md5(outputAbsPath)
                    with open(pmMD5AbsPath, "w", newline="\n") as f:
                        print(mkvHash, "*" + mkvFilename, file=f)

            # compare streamMD5s
            print("*verifying losslessness*")
            with progressbar.ProgressBar(max_value=100) as ffv1losslessprogbar:
                for i in range(100):
                    mov_stream_sum = helpers.checksum_streams(
                        inputAbsPath, audioStreamCounter
                    )
                    mkv_stream_sum = helpers.checksum_streams(
                        outputAbsPath, audioStreamCounter
                    )
                    # PASS/FAIL - check if input stream md5s match output stream md5s
                    streamMD5status = checks.stream_md5_status(
                        mov_stream_sum, mkv_stream_sum
                    )

            print("*Checking against policies*")
            # create a dictionary with the mediaconch results from the MOV and MKV files
            with progressbar.ProgressBar(max_value=100) as policyprogbar:
                for i in range(100):
                    mediaconchResults_dict = {
                        "MOV Mediaconch Policy": helpers.mediaconch_policy_check(
                            inputAbsPath, movPolicy
                        ),
                        "MKV Implementation": helpers.mediaconch_implementation_check(
                            outputAbsPath
                        ),
                        "MKV Mediaconch Policy": helpers.mediaconch_policy_check(
                            outputAbsPath, mkvPolicy
                        ),
                    }
                    # PASS/FAIL - check if any mediaconch results failed and append failed policies to results
                    mediaconchResults = checks.parse_mediaconchResults(
                        mediaconchResults_dict
                    )

                    # run ffprobe on the output file
                    output_metadata = helpers.ffprobe_report(mkvFilename, outputAbsPath)
                    # log system info
                    systemInfo = helpers.generate_system_log(ffvers, tstime, tftime)

                    # PASS/FAIL - are files lossless
                    losslessCheck = checks.lossless_check(
                        input_metadata, output_metadata, streamMD5status
                    )

                    # create a dictionary containing QC results
                    qcResults = helpers.qc_results(
                        inventoryCheck, losslessCheck, mediaconchResults
                    )

            # create json metadata file
            # TO DO: combine checksums into a single dictionary to reduce variables needed here
            helpers.create_json(
                jsonAbsPath,
                systemInfo,
                input_metadata,
                mov_stream_sum,
                mkvHash,
                mkv_stream_sum,
                baseFilename,
                output_metadata,
                item_csvDict,
                qcResults,
            )

            if not args.skip_ac:
                # create access copy
                print("*transcoding access copy*")
                with progressbar.ProgressBar(max_value=100) as accesstranscodeprogbar:
                    for i in range(100):
                        helpers.two_pass_h264_encoding(
                            audioStreamCounter, outputAbsPath, acAbsPath
                        )
                        accesstranscodeprogbar.update(i)
                        # create checksum sidecar file for access copy
                        acHash = corefuncs.hashlib_md5(acAbsPath)
                        with open(
                            os.path.join(
                                acOutputFolder,
                                baseFilename + "_" + ac_identifier + ".md5",
                            ),
                            "w",
                            newline="\n",
                        ) as f:
                            print(
                                acHash,
                                "*" + baseFilename + "_" + ac_identifier + ".mp4",
                                file=f,
                            )

                        # log access copy filename if access copy was created
                        # TO DO: verify that access copy runtime matches pm runtime?
                        if os.path.isfile(acAbsPath):
                            acFilename = baseFilename + "_" + ac_identifier + ".mp4"
                        else:
                            acFilename = "No access copy found"

                        # get current date for logging when QC happned
                        qcDate = str(datetime.datetime.today().strftime("%Y-%m-%d"))

            # create the list that will go in the qc log csv file
            # should correspond to the csvHeaderList earlier in the script
            csvWriteList = [
                qcResults["QC"]["inventory check"],
                qcDate,
                qcResults["QC"]["lossless check"],
                qcDate,
                qcResults["QC"]["mediaconch results"],
                qcDate,
                None,
                None,
                None,
                acFilename,
                mkvFilename,
                helpers.convert_runtime(output_metadata["file metadata"]["duration"]),
            ]

            # Add QC results to QC log csv file
            helpers.write_output_csv(
                output, csvHeaderList, csvWriteList, output_metadata, qcResults
            )

            # create spectrogram for pm audio channels
            if audioStreamCounter > 0 and not args.skip_spectrogram:
                print("*generating QC spectrograms*")
                channel_layout_list = input_metadata["techMetaA"]["channels"]
                helpers.generate_spectrogram(
                    outputAbsPath, channel_layout_list, metaOutputFolder, baseFilename
                )

            # create qctools report
            if not args.skip_qcli:
                print("*creating qctools report*")
                helpers.generate_qctools(outputAbsPath)

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
