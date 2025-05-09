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
    # assign input and output
    indir = corefuncs.input_check()
    if args.output_path:
        qc_csv_file = args.output_path
    else:
        base_folder_name = os.path.basename(indir)
        qc_csv_file = os.path.join(indir, base_folder_name + "-qc_log.csv")
    corefuncs.output_check(qc_csv_file)
    # check that required programs are present
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

    csvInventory = os.path.join(indir, inventoryName)
    # TO DO: separate out csv and json related functions that are currently in supportfuncs into dedicated csv or json related py files
    # csvDict = helpers.import_csv(csvInventory)
    # create the list of csv headers that will go in the qc log csv file

    # importing inventories
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
            print("\n+++ WARNING: Unable to CSV inventory file +++")
            print("CONTINUE? (y/n)")
            yes = {"yes", "y", "ye", ""}
            no = {"no", "n"}
            choice = input().lower()
            if choice in yes:
                source_inventory_dict = {}
            elif choice in no:
                quit()
            else:
                sys.stdout.write("Please respond with 'yes' or 'no'")
                quit()
            # rather than quitting - prompt user to choose whether or not to continue
        else:
            print("Inventories found\n")
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
    print("***STARTING PROCESS***")

    object_list = helpers.get_immediate_subdirectories(indir)

    # load bwf metadata into dictionary
    if args.write_bwf_metadata:
        # TODO check that bwf_metaedit is installed
        bwf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bwf_metadata.json")
        with open(bwf_file) as standard_metadata:
            bwf_dict = json.load(standard_metadata)

    # TODO add earlier failure to end process if all files do not have corresponding inventory entries

    for object in object_list:
        object_folder_abspath = os.path.join(indir, object)
        if os.path.isdir(os.path.join(object_folder_abspath, pm_identifier)):
            pm_folder_abspath = os.path.join(object_folder_abspath, pm_identifier)
            for file in glob.glob1(pm_folder_abspath, "*" + preservation_extension):
                pm_file_abspath = os.path.join(pm_folder_abspath, file)
                if not file.endswith(pm_identifier + preservation_extension):
                    print("WARNING: Error processing preservation files")
                    print(
                        "Your input files do not end with the expected identifier or have a different extension than was expected"
                    )
                    quit()
                else:
                    base_filename = file.replace(
                        pm_identifier + preservation_extension, ""
                    )
                ac_folder_abspath = os.path.join(object_folder_abspath, ac_identifier)
                ac_file_abspath = os.path.join(
                    ac_folder_abspath, base_filename + ac_identifier + access_extension
                )
                meta_folder_abspath = os.path.join(
                    object_folder_abspath, metadata_identifier
                )
                pm_md5_abspath = pm_file_abspath.replace(preservation_extension, ".md5")
                ac_md5_abspath = ac_file_abspath.replace(access_extension, ".md5")

                print("Processing " + file)

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
                    # TODO coding history needs to be updated accordingly
                    coding_history = inventory_bwf_metadata["coding history"]
                    if input_metadata["file metadata"]["channels"] == 1:
                        file_sound_mode = "mono"
                    elif input_metadata["file metadata"]["channels"] == 2:
                        file_sound_mode = "stereo"
                    else:
                        # TODO prompt user to enter a sound mode for the file manually?
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
                    # if args.reset_timereference:
                    #    bwf_command += ['--Timereference=' + '0']
                    subprocess.run(bwf_command)
                    # print(bwf_command)

                    # create checksum sidecar file for preservation master
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
                    # sox_command = [args.sox_path, pm_file_abspath, '-b', '16', ac_file_abspath, 'rate', '44100']
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
                # embed BWF metadata for a file
                if args.write_bwf_metadata:
                    print("*embedding BWF metadata*")
                    inventory_bwf_metadata = loaded_metadata[inventory_filename][
                        "BWF Metadata"
                    ]
                    source_format = inventory_bwf_metadata["format"].lower()
                    bwf_dict["ISRF"]["write"] = source_format
                    # TODO coding history needs to be updated accordingly
                    coding_history = inventory_bwf_metadata["coding history"]
                    if input_metadata["file metadata"]["channels"] == 1:
                        file_sound_mode = "mono"
                    elif input_metadata["file metadata"]["channels"] == 2:
                        file_sound_mode = "stereo"
                    else:
                        # TODO prompt user to enter a sound mode for the file manually?
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
                        ac_file_abspath,
                        "--MD5-Embed",
                        "--BextVersion=1",
                    ]
                    for key in bwf_dict:
                        if bwf_dict[key]["write"]:
                            bwf_command += [
                                bwf_dict[key]["command"] + bwf_dict[key]["write"]
                            ]
                    # if args.reset_timereference:
                    #    bwf_command += ['--Timereference=' + '0']
                    subprocess.run(bwf_command)
                    # print(bwf_command)

                # create folder for metadata if needed
                if args.spectrogram or args.write_json:
                    helpers.create_output_folder(
                        meta_folder_abspath
                    )

                # create spectrogram for pm audio channels
                if args.spectrogram:
                    # TODO handle cases where spectrogram files already exist
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
                    # channel_layout = input_metadata['file metadata']['channels']
                    # helpers.generate_spectrogram(pm_file_abspath, channel_layout, meta_folder_abspath, base_filename)

                # TODO make this able to handle cases where there is no access file
                # TODO split BWF metadata checks into separate policies?
                # create a dictionary with the mediaconch results
                print("*Running MediaConch on Preservation and Access files*")
                mediaconchResults_dict = {
                    "Preservation Format Policy": helpers.mediaconch_policy_check(
                        pm_file_abspath, p_wav_policy
                    ),
                    "Preservation BWF Policy": helpers.mediaconch_policy_check(
                        pm_file_abspath, bwf_policy
                    ),
                    "Access Format Policy": helpers.mediaconch_policy_check(
                        ac_file_abspath, a_wav_policy
                    ),
                    "Access BWF Policy": helpers.mediaconch_policy_check(
                        ac_file_abspath, bwf_policy
                    ),
                }
                # PASS/FAIL - check if any mediaconch results failed and append failed policies to results
                mediaconchResults = (
                    helpers.parse_mediaconchResults(
                        mediaconchResults_dict
                    )
                )

                # systemInfo = helpers.generate_system_log()

                # create a dictionary containing QC results
                qcResults = helpers.qc_results(
                    inventory_check, mediaconchResults
                )

                # TODO use bwfmetaedit --out-core and --out-tech to grab the BWF metadata, then translate csv data to dict
                if args.write_json:
                    # TODO consider using --out-tech to get technical metadata instead of ffmpeg?
                    bwf_meta_dict = helpers.get_bwf_metadata(
                        pm_file_abspath
                    )
                    # input_metadata['file_metadata'].pop('Format')
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

                # get current date for logging when QC happned
                qcDate = str(datetime.datetime.today().strftime("%Y-%m-%d"))

                # TODO multi-part/side files need cumulative runtime
                # create the list that will go in the qc log csv file
                # should correspond to the csvHeaderList earlier in the script
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

if __name__ == "__main__":
	main()