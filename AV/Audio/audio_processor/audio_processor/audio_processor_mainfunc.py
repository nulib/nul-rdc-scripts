#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import subprocess
import datetime
import json
from audio_processor.audio_processor_parameters import args
from audio_processor import audio_processor_supportfuncs
from audio_processor import corefuncs

def audio_processor_main():
    pm_identifier = 'p'
    ac_identifier = 'a'
    metadata_identifier = 'meta'
    preservation_extension = '.wav'
    access_extension = '.wav'
    inventoryName = 'transcode_inventory.csv'

    #assign mediaconch policies to use
    '''
    if not args.input_policy:
        movPolicy = os.path.join(os.path.dirname(__file__), 'data/mediaconch_policies/AJA_NTSC_VHS-2SAS-MOV.xml')
    else:
        movPolicy = args.input_policy
    if not args.output_policy:
        mkvPolicy = os.path.join(os.path.dirname(__file__), 'data/mediaconch_policies/AJA_NTSC_VHS-2SAS-MKV.xml')
    else:
        mkvPolicy = args.output_policy
    '''

    #assign input and output
    indir = corefuncs.input_check()
    if args.output_path:
        meadow_csv_file = args.output_path
    else:
        base_folder_name = os.path.basename(indir)
        qc_csv_file = os.path.join(indir, base_folder_name + '-QC_results.csv')
    corefuncs.output_check(qc_csv_file)

    #check that required programs are present
    corefuncs.mediaconch_check()
    corefuncs.ffprobe_check()
    ffvers = corefuncs.get_ffmpeg_version()
    metaedit_version = corefuncs.get_bwf_metaedit_version()
    sox_version = corefuncs.get_sox_version()

    inventory_reference_file = os.path.join(os.path.dirname(__file__), 'data/inventory_reference.csv')
    reference_inventory_dict = audio_processor_supportfuncs.load_inventory_reference(inventory_reference_file)
    #verify that mediaconch policies are present
    '''
    corefuncs.mediaconch_policy_exists(movPolicy)
    corefuncs.mediaconch_policy_exists(mkvPolicy)
    '''

    csvInventory = os.path.join(indir, inventoryName)
    #TO DO: separate out csv and json related functions that are currently in supportfuncs into dedicated csv or json related py files
    #csvDict = audio_processor_supportfuncs.import_csv(csvInventory)
    #create the list of csv headers that will go in the qc log csv file

    #importing inventories
    if args.source_inventory:
        source_inventories = args.source_inventory
        source_inventory_dictlist = audio_processor_supportfuncs.import_inventories(source_inventories, reference_inventory_dict)
    else:
        print('\n*** Checking input directory for CSV files ***')
        source_inventories = glob.glob(os.path.join(indir, "*.csv"))
        #skip auto-generated meadow ingest csv if it already exists
        source_inventories = [i for i in source_inventories if not '-QC_results.csv' in i]
        if not source_inventories:
            print("\n+++ WARNING: Unable to CSV inventory file +++")
            print("CONTINUE? (y/n)")
            yes = {'yes','y', 'ye', ''}
            no = {'no','n'}
            choice = input().lower()
            if choice in yes:
                source_inventory_dictlist = [{}]
            elif choice in no:
                quit()
            else:
                sys.stdout.write("Please respond with 'yes' or 'no'")
                quit()
            #rather than quitting - prompt user to choose whether or not to continue
        else:
            print("Inventories found\n")
            source_inventory_dictlist = audio_processor_supportfuncs.import_inventories(source_inventories, reference_inventory_dict)
    print(source_inventory)
    quit()
    csvHeaderList = [
    "Shot Sheet Check",
    "Date",
    "File Format & Metadata Verification",
    "Date",
    "File Inspection",
    "Date",
    "QC Notes"
    ]
    print ("***STARTING PROCESS***")

    object_list = audio_processor_supportfuncs.get_immediate_subdirectories(indir)

    #load bwf metadata into dictionary
    if args.write_bwf_metadata:
        #TODO check that bwf_metaedit is installed
        bwf_file = os.path.join(os.path.dirname(__file__), 'data/bwf_metadata.json')
        with open(bwf_file) as standard_metadata:
            bwf_dict = json.load(standard_metadata)

    for object in object_list:
        object_folder_abspath = os.path.join(indir, object)
        if os.path.isdir(os.path.join(object_folder_abspath, pm_identifier)):
            pm_folder_abspath = os.path.join(object_folder_abspath, pm_identifier)
            for file in glob.glob1(pm_folder_abspath, "*" + preservation_extension):
                pm_file_abspath = os.path.join(pm_folder_abspath, file)
                if not file.endswith(pm_identifier + preservation_extension):
                    print('WARNING: Error processing preservation files')
                    print('Your input files do not end with the expected identifier or have a different extension than was expected')
                    quit()
                else:
                    base_filename = file.replace(pm_identifier + preservation_extension, '')
                ac_folder_abspath = os.path.join(object_folder_abspath, ac_identifier)
                ac_file_abspath = os.path.join(ac_folder_abspath, base_filename + ac_identifier + access_extension)
                meta_folder_abspath = os.path.join(object_folder_abspath, metadata_identifier)
                json_file_abspath = os.path.join(meta_folder_abspath, base_filename + metadata_identifier + '.json')
                pm_md5_abspath = pm_file_abspath.replace(preservation_extension, '.md5')
                ac_md5_abspath = ac_file_abspath.replace(access_extension, '.md5')
                #TODO find matching file in inventory

                #generate ffprobe metadata from input
                input_metadata = audio_processor_supportfuncs.ffprobe_report(file, pm_file_abspath)

                #embed BWF metadata
                if args.write_bwf_metadata:
                    bwf_command = [args.metaedit_path, pm_file_abspath, '--MD5-Embed']
                    for key in bwf_dict:
                        if bwf_dict[key]['write']:
                            bwf_command += [bwf_dict[key]['command'] + bwf_dict[key]['write']]
                    print(bwf_command)

                #create folder for metadata if it doesn't already exist
                audio_processor_supportfuncs.create_output_folder(meta_folder_abspath)

                if args.transcode:
                    audio_processor_supportfuncs.create_output_folder(ac_folder_abspath)
                    ffmpeg_command = [args.ffmpeg_path, '-loglevel', 'error', '-i', pm_file_abspath]
                    ffmpeg_command += ['-af', 'aresample=resampler=soxr', '-ar', '44100', '-c:a', 'pcm_s16le', '-write_bext', '1', ac_file_abspath]
                    #sox_command = [args.sox_path, pm_file_abspath, '-b', '16', ac_file_abspath, 'rate', '44100']
                    subprocess.run(ffmpeg_command)
                    #generate md5 for access file
                    acHash = corefuncs.hashlib_md5(ac_file_abspath)
                    with open (os.path.join(ac_md5_abspath), 'w',  newline='\n') as f:
                        print(acHash, '*' + base_filename + ac_identifier + access_extension, file=f)
                '''
                #TODO only create md5 if one doesn't already exist?
                #create checksum sidecar file for preservation master
                print ("*creating checksum*")
                pm_hash = corefuncs.hashlib_md5(pm_file_abspath)
                with open (pm_md5_abspath, 'w',  newline='\n') as f:
                    print(pm_hash, '*' + file, file=f)
                '''

                #create spectrogram for pm audio channels
                if not args.skip_spectrogram:
                    print ("*generating QC spectrograms*")
                    sox_spectrogram_command = [args.sox_path, pm_file_abspath, '-n', 'spectrogram', '-Y', '1080', '-x', '1920', '-o', os.path.join(meta_folder_abspath, base_filename + 'spectrogram' + '.png')]
                    subprocess.run(sox_spectrogram_command)
                    #channel_layout = input_metadata['techMetaA']['channels']
                    #audio_processor_supportfuncs.generate_spectrogram(pm_file_abspath, channel_layout, meta_folder_abspath, base_filename)

                print(file)
                #TODO use ffmpeg with sox resampler? ffmpeg -i file -af aresample=resampler=soxr -ar 44100 -c:a pcm_s16le -write_bext 1 output
                #would need a to check ffmpeg configuration for '--enable-libsoxr'
                quit()
                '''
                print ("\n")
                #get information about item from csv inventory
                print("*checking inventory for", baseFilename + "*")
                item_csvDict = csvDict.get(baseFilename)
                #PASS/FAIL - was the file found in the inventory
                inventoryCheck = mov2ffv1passfail_checks.inventory_check(item_csvDict)
                '''
                '''
                audioStreamCounter = input_metadata['techMetaA']['audio stream count']
                '''

                '''
                #create a dictionary with the mediaconch results from the MOV and MKV files
                mediaconchResults_dict = {
                'MOV Mediaconch Policy': mov2ffv1supportfuncs.mediaconch_policy_check(inputAbsPath, movPolicy),
                'MKV Implementation':  mov2ffv1supportfuncs.mediaconch_implementation_check(outputAbsPath),
                'MKV Mediaconch Policy': mov2ffv1supportfuncs.mediaconch_policy_check(outputAbsPath, mkvPolicy),
                }
                #PASS/FAIL - check if any mediaconch results failed and append failed policies to results
                mediaconchResults = mov2ffv1passfail_checks.parse_mediaconchResults(mediaconchResults_dict)

                #create a dictionary containing QC results
                qcResults = mov2ffv1supportfuncs.qc_results(inventoryCheck, losslessCheck, mediaconchResults)

                #create json metadata file
                #TO DO: combine checksums into a single dictionary to reduce variables needed here
                mov2ffv1supportfuncs.create_json(jsonAbsPath, systemInfo, input_metadata, mov_stream_sum, mkvHash, mkv_stream_sum, baseFilename, output_metadata, item_csvDict, qcResults)
                '''

                #get current date for logging when QC happned
                qcDate = str(datetime.datetime.today().strftime('%Y-%m-%d'))

                #create the list that will go in the qc log csv file
                #should correspond to the csvHeaderList earlier in the script
                csvWriteList = [
                qcResults['QC']['Inventory Check'],
                qcDate,
                qcResults['QC']['Lossless Check'],
                qcDate,
                qcResults['QC']['Mediaconch Results'],
                qcDate,
                None,
                None,
                None,
                acFilename,
                mkvFilename,
                mov2ffv1supportfuncs.convert_runtime(output_metadata['file metadata']['duration'])
                ]

                #Add QC results to QC log csv file
                mov2ffv1supportfuncs.write_output_csv(outdir, csvHeaderList, csvWriteList, output_metadata, qcResults)


            else:
                print ('No file in output folder.  Skipping file processing')
