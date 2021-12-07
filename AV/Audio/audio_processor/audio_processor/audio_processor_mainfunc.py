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
    if not args.input_policy:
        p_wav_policy = os.path.join(os.path.dirname(__file__), 'data/mediaconch_policies/preservation_wav-96k24.xml')
    else:
        p_wav_policy = args.input_policy
    if not args.output_policy:
        a_wav_policy = os.path.join(os.path.dirname(__file__), 'data/mediaconch_policies/access_wav-44k16.xml')
    else:
        a_wav_policy = args.output_policy

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

    reference_inventory_file = os.path.join(os.path.dirname(__file__), 'data/inventory_reference.csv')
    reference_inventory_list = audio_processor_supportfuncs.load_reference_inventory(reference_inventory_file)
    #verify that mediaconch policies are present
    corefuncs.mediaconch_policy_exists(p_wav_policy)
    corefuncs.mediaconch_policy_exists(a_wav_policy)

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
        source_inventories = [i for i in source_inventories if not '-QC_results.csv' in i]
        if not source_inventories:
            print("\n+++ WARNING: Unable to CSV inventory file +++")
            print("CONTINUE? (y/n)")
            yes = {'yes','y', 'ye', ''}
            no = {'no','n'}
            choice = input().lower()
            if choice in yes:
                source_inventory_dict = {}
            elif choice in no:
                quit()
            else:
                sys.stdout.write("Please respond with 'yes' or 'no'")
                quit()
            #rather than quitting - prompt user to choose whether or not to continue
        else:
            print("Inventories found\n")
            source_inventory_dict = audio_processor_supportfuncs.import_inventories(source_inventories, reference_inventory_list)

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
                pm_md5_abspath = pm_file_abspath.replace(preservation_extension, '.md5')
                ac_md5_abspath = ac_file_abspath.replace(access_extension, '.md5')

                print("Processing " + file)

                #load inventory metadata related to the file
                loaded_metadata = audio_processor_supportfuncs.load_item_metadata(file, source_inventory_dict)
                #loading inventory metadata means the item was found in the inventory
                inventory_check = 'PASS'
                inventory_filename = []
                for key in loaded_metadata:
                    inventory_filename.append(key)
                inventory_filename = ''.join(inventory_filename)

                #json filename should use the filename found in the inventory
                json_file_abspath = os.path.join(meta_folder_abspath, inventory_filename + '-' + metadata_identifier + '.json')

                '''
                continue work here
                '''
                #TODO build out content appended to Files section of this dict with BWF metadata, technical metadata, and qc results
                loaded_metadata[inventory_filename]['Files'] = [file]
                if 'Files' not in loaded_metadata[inventory_filename]:
                    loaded_metadata[inventory_filename]['Files'] = [file]
                else:
                    loaded_metadata[inventory_filename]['Files'].append(file)
                #generate ffprobe metadata from input
                input_metadata = audio_processor_supportfuncs.ffprobe_report(file, pm_file_abspath)
                print(loaded_metadata)
                quit()
                #embed BWF metadata
                if args.write_bwf_metadata:
                    print("*embedding BWF metadata*")
                    source_format = loaded_metadata[inventory_filename]['Format'].lower()
                    bwf_dict['ISRF']['write'] = source_format
                    #TODO coding history needs to be updated accordingly
                    coding_history = loaded_metadata[inventory_filename]['Coding History']
                    if input_metadata['techMetaA']['channels'] == 1:
                        file_sound_mode = 'mono'
                    elif input_metadata['techMetaA']['channels'] == 2:
                        file_sound_mode = 'stereo'
                    else:
                        #TODO prompt user to enter a sound mode for the file manually?
                        pass
                    coding_history_update = 'A=PCM,F=' + input_metadata['techMetaA']['audio sample rate'] + ',W=' + input_metadata['techMetaA']['audio bitrate'] + ',M=' + file_sound_mode + ',T=BWFMetaEdit ' + metaedit_version
                    coding_history = coding_history + '\r\n' + coding_history_update
                    bwf_dict['CodingHistory']['write'] = coding_history
                    bwf_command = [args.metaedit_path, pm_file_abspath, '--MD5-Embed', '--BextVersion=1']
                    for key in bwf_dict:
                        if bwf_dict[key]['write']:
                            bwf_command += [bwf_dict[key]['command'] + bwf_dict[key]['write']]
                    if args.reset_timereference:
                        bwf_command += ['--Timereference=' + '0']
                    subprocess.run(bwf_command)
                    #print(bwf_command)

                    #create checksum sidecar file for preservation master
                    print ("*creating checksum for preservation file*")
                    pm_hash = corefuncs.hashlib_md5(pm_file_abspath)
                    with open (pm_md5_abspath, 'w',  newline='\n') as f:
                        print(pm_hash, '*' + file, file=f)

                #create folder for metadata if it doesn't already exist
                audio_processor_supportfuncs.create_output_folder(meta_folder_abspath)

                if args.transcode:
                    print("*transcoding access file*")
                    audio_processor_supportfuncs.create_output_folder(ac_folder_abspath)
                    ffmpeg_command = [args.ffmpeg_path, '-loglevel', 'error', '-i', pm_file_abspath]
                    ffmpeg_command += ['-af', 'aresample=resampler=soxr', '-ar', '44100', '-c:a', 'pcm_s16le', '-write_bext', '1', ac_file_abspath]
                    #sox_command = [args.sox_path, pm_file_abspath, '-b', '16', ac_file_abspath, 'rate', '44100']
                    subprocess.run(ffmpeg_command)
                    #generate md5 for access file
                    print("*creating checksum for access file*")
                    acHash = corefuncs.hashlib_md5(ac_file_abspath)
                    with open (os.path.join(ac_md5_abspath), 'w',  newline='\n') as f:
                        print(acHash, '*' + base_filename + ac_identifier + access_extension, file=f)

                #create spectrogram for pm audio channels
                if not args.skip_spectrogram:
                    #TODO handle cases where spectrogram files already exist
                    print ("*generating QC spectrograms*")
                    sox_spectrogram_command = [args.sox_path, pm_file_abspath, '-n', 'spectrogram', '-Y', '1080', '-x', '1920', '-o', os.path.join(meta_folder_abspath, base_filename + 'spectrogram' + '.png')]
                    subprocess.run(sox_spectrogram_command)
                    #channel_layout = input_metadata['techMetaA']['channels']
                    #audio_processor_supportfuncs.generate_spectrogram(pm_file_abspath, channel_layout, meta_folder_abspath, base_filename)

                #TODO make this able to handle cases where there is no access file
                #create a dictionary with the mediaconch results
                print("*Running MediaConch*")
                mediaconchResults_dict = {
                'Preservation Mediaconch Policy': audio_processor_supportfuncs.mediaconch_policy_check(pm_file_abspath, p_wav_policy),
                'Access Mediaconch Policy': audio_processor_supportfuncs.mediaconch_policy_check(ac_file_abspath, a_wav_policy)
                }
                #PASS/FAIL - check if any mediaconch results failed and append failed policies to results
                mediaconchResults = audio_processor_supportfuncs.parse_mediaconchResults(mediaconchResults_dict)

                #systemInfo = audio_processor_supportfuncs.generate_system_log()

                #create json metadata file
                audio_processor_supportfuncs.create_json(json_file_abspath, systemInfo, input_metadata, bwf_metadata, item_csvDict, qcResults)

                #get current date for logging when QC happned
                qcDate = str(datetime.datetime.today().strftime('%Y-%m-%d'))

                #create a dictionary containing QC results
                qcResults = mov2ffv1supportfuncs.qc_results(inventory_check, mediaconchResults)

                #create the list that will go in the qc log csv file
                #should correspond to the csvHeaderList earlier in the script
                csvWriteList = [
                qcResults['QC']['Inventory Check'],
                qcDate,
                qcResults['QC']['Mediaconch Results'],
                qcDate,
                None,
                None,
                None,
                audio_processor_supportfuncs.convert_runtime(output_metadata['file metadata']['duration'])
                ]

                #Add QC results to QC log csv file
                audio_processor_supportfuncs.write_output_csv(outdir, csvHeaderList, csvWriteList, output_metadata, qcResults)


            else:
                print ('No file in output folder.  Skipping file processing')
