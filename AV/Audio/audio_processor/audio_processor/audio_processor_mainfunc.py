#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import subprocess
import datetime
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
    #assign input directory and output directory
    indir = corefuncs.input_check()
    #check that required programs are present
    corefuncs.mediaconch_check()
    #use sox for spectrograms and getting metadata?
    '''
    corefuncs.ffprobe_check()
    ffvers = corefuncs.get_ffmpeg_version()
    '''
    #verify that mediaconch policies are present
    '''
    corefuncs.mediaconch_policy_exists(movPolicy)
    corefuncs.mediaconch_policy_exists(mkvPolicy)
    '''
    #csvInventory = os.path.join(indir, inventoryName)
    #TO DO: separate out csv and json related functions that are currently in supportfuncs into dedicated csv or json related py files
    #csvDict = audio_processor_supportfuncs.import_csv(csvInventory)
    #create the list of csv headers that will go in the qc log csv file
    csvHeaderList = [
    "Shot Sheet Check",
    "Date",
    "PM Lossless Transcoding",
    "Date",
    "File Format & Metadata Verification",
    "Date",
    "File Inspection",
    "Date",
    "QC Notes",
    "AC Filename",
    "PM Filename",
    "Runtime"
    ]
    print ("***STARTING PROCESS***")

    object_list = audio_processor_supportfuncs.get_immediate_subdirectories(indir)

    for object in object_list:
        object_folder_abspath = os.path.join(indir, object)
        if os.path.isdir(os.path.join(object_folder_abspath, pm_identifier)):
            pm_folder_abspath = os.path.join(object_folder_abspath, pm_identifier)
            for file in glob.glob1(pm_folder_abspath, "*" + preservation_extension):
                pm_file_abspath = os.path.join(pm_folder_abspath, file)
                base_filename = file.replace(pm_identifier + preservation_extension, '')
                ac_folder_abspath = os.path.join(object_folder_abspath, ac_identifier)
                ac_file_abspath = os.path.join(ac_folder_abspath, base_filename + ac_identifier + access_extension)
                meta_folder_abspath = os.path.join(object_folder_abspath, metadata_identifier)
                json_file_abspath = os.path.join(meta_folder_abspath, base_filename + metadata_identifier + '.json')
                pm_md5_abspath = pm_file_abspath.replace(preservation_extension, '.md5')
                ac_md5_abspath = ac_file_abspath.replace(access_extension, '.md5')
                #TODO find matching file in inventory
                #TODO create a set of filenames from inventory, check if input matches anything in the set and then remove item from set at end of for loop?
                #generate ffprobe metadata from input
                #input_metadata = mov2ffv1supportfuncs.ffprobe_report(movFilename, inputAbsPath)

                #TODO have defualt processing path just be QC?
                #create a list of needed output folders and make them
                if args.qc:
                    outFolders = [meta_folder_abspath]
                else:
                    outFolders = [ac_folder_abspath, meta_folder_abspath]
                audio_processor_supportfuncs.create_output_folders(outFolders)

                print(file)
                #TODO use ffmpeg with sox resampler? ffmpeg -i file -af aresample=resampler=soxr -ar 44100 -c:a pcm_s16le output
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
                #losslessly transcode with ffmpeg
                transcode_nameDict = {
                'inputAbsPath' : inputAbsPath,
                'tempMasterFile' : tempMasterFile,
                'framemd5AbsPath' : framemd5AbsPath,
                'outputAbsPath' : outputAbsPath,
                'framemd5File' : framemd5File
                }
                audioStreamCounter = input_metadata['techMetaA']['audio stream count']
                '''
                #TODO only create md5 if one doesn't already exist?
                #create checksum sidecar file for preservation master
                print ("*creating checksum*")
                pm_hash = corefuncs.hashlib_md5(pm_file_abspath)
                with open (pm_md5_abspath, 'w',  newline='\n') as f:
                    print(pm_hash, '*' + file, file=f)
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
                if not args.skip_ac:
                    #create access copy
                    print ('*transcoding access copy*')
                    mov2ffv1supportfuncs.two_pass_h264_encoding(audioStreamCounter, outputAbsPath, acAbsPath)

                    #create checksum sidecar file for access copy
                    acHash = corefuncs.hashlib_md5(acAbsPath)
                    with open (os.path.join(acOutputFolder, baseFilename + '-' + ac_identifier + '.md5'), 'w',  newline='\n') as f:
                        print(acHash, '*' + baseFilename + '-' + ac_identifier + '.mp4', file=f)

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

                #create spectrogram for pm audio channels
                if audioStreamCounter > 0 and not args.skip_spectrogram:
                    print ("*generating QC spectrograms*")
                    channel_layout_list = input_metadata['techMetaA']['channels']
                    mov2ffv1supportfuncs.generate_spectrogram(outputAbsPath, channel_layout_list, metaOutputFolder, baseFilename)

            else:
                print ('No file in output folder.  Skipping file processing')
