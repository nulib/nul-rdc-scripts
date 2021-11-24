#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import subprocess
import datetime
from aja_mov2ffv1.mov2ffv1parameters import args
from aja_mov2ffv1 import mov2ffv1supportfuncs
from aja_mov2ffv1 import corefuncs
from aja_mov2ffv1 import mov2ffv1passfail_checks

#TO DO: general cleanup

def aja_mov2ffv1_main():
    #the pm identifier is the name of the folder that the preservation file will be output to
    pm_identifier = 'p'
    #the ac identifier will be used as the folder name for the access file
    #it will also be appended to the end of the access copy filename
    ac_identifier = 'a'
    metadata_identifier = 'meta'
    #identifier appended to the end of the MKV preservation file
    #Replace with "None" to keep the name the same as the input
    if not args.keep_filename:
        pm_filename_identifier = '-p'
    else:
        pm_filename_identifier = None
    inventoryName = 'transcode_inventory.csv'
    #assign mediaconch policies to use
    if not args.input_policy:
        movPolicy = os.path.join(os.path.dirname(__file__), 'data/mediaconch_policies/AJA_NTSC_VHS-4AS-MOV.xml')
    else:
        movPolicy = args.input_policy
    if not args.output_policy:
        mkvPolicy = os.path.join(os.path.dirname(__file__), 'data/mediaconch_policies/AJA_NTSC_VHS-4AS-MKV-PCM.xml')
    else:
        mkvPolicy = args.output_policy
    
    #assign input directory and output directory
    indir = corefuncs.input_check()
    outdir = corefuncs.output_check()
    #check that mixdown argument is valid if provided
    mov2ffv1supportfuncs.check_mixdown_arg()
    #check that required programs are present
    if not args.skip_qcli:
        corefuncs.qcli_check()
    corefuncs.mediaconch_check()
    corefuncs.ffprobe_check()
    ffvers = corefuncs.get_ffmpeg_version()

    #verify that mediaconch policies are present
    corefuncs.mediaconch_policy_exists(movPolicy)
    corefuncs.mediaconch_policy_exists(mkvPolicy)

    csvInventory = os.path.join(indir, inventoryName)
    #TO DO: separate out csv and json related functions that are currently in supportfuncs into dedicated csv or json related py files
    csvDict = mov2ffv1supportfuncs.import_csv(csvInventory)
    
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

    for movFilename in glob.glob1(indir, "*.mov"):
        #create names that will be used in the script
        #TO DO: handle transcoding legacy files (either need a flag that avoids appending pm to the output filename or the ability to read the desired output filename from the CSV file
        inputAbsPath = os.path.join(indir, movFilename)
        baseFilename = movFilename.replace('.mov','')
        baseOutput = os.path.join(outdir, baseFilename)
        pmOutputFolder = os.path.join(baseOutput, pm_identifier)
        mkvBaseFilename = (baseFilename + pm_filename_identifier ) if pm_filename_identifier else (baseFilename)
        mkvFilename = mkvBaseFilename + '.mkv'
        outputAbsPath = os.path.join(pmOutputFolder, mkvFilename)
        tempMasterFile = os.path.join(pmOutputFolder, baseFilename + '-tmp.mkv')
        framemd5File = mkvBaseFilename + '.framemd5'
        framemd5AbsPath = os.path.join(pmOutputFolder, framemd5File)
        acOutputFolder = os.path.join(baseOutput, ac_identifier)
        acAbsPath = os.path.join(acOutputFolder, baseFilename + '-' + ac_identifier + '.mp4')
        metaOutputFolder = os.path.join(baseOutput, metadata_identifier)
        jsonAbsPath = os.path.join(metaOutputFolder, baseFilename + '-' + metadata_identifier + '.json')
        pmMD5AbsPath = os.path.join(pmOutputFolder, mkvBaseFilename + '.md5')
        
        #generate ffprobe metadata from input
        input_metadata = mov2ffv1supportfuncs.ffprobe_report(movFilename, inputAbsPath)  
        
        #create a list of needed output folders and make them
        if not args.skip_ac:
            outFolders = [pmOutputFolder, acOutputFolder, metaOutputFolder]
        else:
            outFolders = [pmOutputFolder, metaOutputFolder]
        mov2ffv1supportfuncs.create_transcode_output_folders(baseOutput, outFolders)
        
        print ("\n")
        #get information about item from csv inventory
        print("*checking inventory for", baseFilename + "*")
        item_csvDict = csvDict.get(baseFilename)
        #PASS/FAIL - was the file found in the inventory
        inventoryCheck = mov2ffv1passfail_checks.inventory_check(item_csvDict)
        
        print ("*losslessly transcoding", baseFilename + "*")
        
        #log transcode start time
        tstime = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        #losslessly transcode with ffmpeg
        transcode_nameDict = {
        'inputAbsPath' : inputAbsPath,
        'tempMasterFile' : tempMasterFile,
        'framemd5AbsPath' : framemd5AbsPath,
        'outputAbsPath' : outputAbsPath,
        'framemd5File' : framemd5File
        }
        audioStreamCounter = input_metadata['techMetaA']['audio stream count']
        mov2ffv1supportfuncs.ffv1_lossless_transcode(input_metadata, transcode_nameDict, audioStreamCounter)
        
        #log transcode finish time
        tftime = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        
        #If ffv1 file was succesfully created, do remaining verification and transcoding work
        if os.path.isfile(outputAbsPath):
            #create checksum sidecar file for preservation master
            print ("*creating checksum*")
            mkvHash = corefuncs.hashlib_md5(outputAbsPath)
            with open (pmMD5AbsPath, 'w',  newline='\n') as f:
                print(mkvHash, '*' + mkvFilename, file=f)
            
            #compare streamMD5s
            print ("*verifying losslessness*")
            mov_stream_sum = mov2ffv1supportfuncs.checksum_streams(inputAbsPath, audioStreamCounter)
            mkv_stream_sum = mov2ffv1supportfuncs.checksum_streams(outputAbsPath, audioStreamCounter)
            #PASS/FAIL - check if input stream md5s match output stream md5s
            streamMD5status = mov2ffv1passfail_checks.stream_md5_status(mov_stream_sum, mkv_stream_sum)
            
            #create a dictionary with the mediaconch results from the MOV and MKV files
            mediaconchResults_dict = {
            'MOV Mediaconch Policy': mov2ffv1supportfuncs.mediaconch_policy_check(inputAbsPath, movPolicy),
            'MKV Implementation':  mov2ffv1supportfuncs.mediaconch_implementation_check(outputAbsPath),
            'MKV Mediaconch Policy': mov2ffv1supportfuncs.mediaconch_policy_check(outputAbsPath, mkvPolicy),
            }
            #PASS/FAIL - check if any mediaconch results failed and append failed policies to results
            mediaconchResults = mov2ffv1passfail_checks.parse_mediaconchResults(mediaconchResults_dict)
            
            #run ffprobe on the output file
            output_metadata = mov2ffv1supportfuncs.ffprobe_report(mkvFilename, outputAbsPath)
            #log system info
            systemInfo = mov2ffv1supportfuncs.generate_system_log(ffvers, tstime, tftime)      
            
            #PASS/FAIL - are files lossless
            losslessCheck = mov2ffv1passfail_checks.lossless_check(input_metadata, output_metadata, streamMD5status)
            
            #create a dictionary containing QC results
            qcResults = mov2ffv1supportfuncs.qc_results(inventoryCheck, losslessCheck, mediaconchResults)
            
            #create json metadata file
            #TO DO: combine checksums into a single dictionary to reduce variables needed here
            mov2ffv1supportfuncs.create_json(jsonAbsPath, systemInfo, input_metadata, mov_stream_sum, mkvHash, mkv_stream_sum, baseFilename, output_metadata, item_csvDict, qcResults)
            
            if not args.skip_ac:
                #create access copy
                print ('*transcoding access copy*')
                mov2ffv1supportfuncs.two_pass_h264_encoding(audioStreamCounter, outputAbsPath, acAbsPath)
                
                #create checksum sidecar file for access copy
                acHash = corefuncs.hashlib_md5(acAbsPath)
                with open (os.path.join(acOutputFolder, baseFilename + '-' + ac_identifier + '.md5'), 'w',  newline='\n') as f:
                    print(acHash, '*' + baseFilename + '-' + ac_identifier + '.mp4', file=f)
                
            #log access copy filename if access copy was created
            #TO DO: verify that access copy runtime matches pm runtime?
            if os.path.isfile(acAbsPath):
                acFilename = baseFilename + '-' + ac_identifier + '.mp4'
            else:
                acFilename = "No access copy found"
                
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
            
            #create qctools report
            if not args.skip_qcli:
                print ("*creating qctools report*")
                mov2ffv1supportfuncs.generate_qctools(outputAbsPath)
            
        else:
            print ('No file in output folder.  Skipping file processing')

#TO DO: (low/not priority) add ability to automatically pull trim times from CSV (-ss 00:00:02 -t 02:13:52)?
#import time
#timeIn = [get csv time1]
#timeOut = [get csv time2]
#t1 = datetime.datetime.strptime(timeIn, "%H:%M:%S")
#t2 = datetime.datetime.strptime(timeOut, "%H:%M:%S")
#trimtime = time.strftime('%H:%M:%S', time.gmtime(((60 * ((60 * t2.hour) + t2.minute)) + t2.second) - ((60 * ((60 * t1.hour) + t1.minute)) + t1.second)))
