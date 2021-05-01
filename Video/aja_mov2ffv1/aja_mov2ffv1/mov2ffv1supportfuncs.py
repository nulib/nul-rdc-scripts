#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import json
import csv
import datetime
import time
from aja_mov2ffv1 import equipment_dict
from aja_mov2ffv1.mov2ffv1parameters import args

def create_transcode_output_folders(baseOutput, outputFolderList):
    if not os.path.isdir(baseOutput):
        try:
            os.mkdir(baseOutput)
        except:
            print ("unable to create output folder:", baseOutput)
            quit()
    else:
        print (baseOutput, "already exists")
        print ('Proceeding')
        
    for folder in outputFolderList:
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except:
                print ("unable to create output folder:", folder)
                quit()
        else:
            print ("using existing folder", folder, "as output")
    
def check_mixdown_arg():
    mixdown_list = ['copy', '4to3', '4to2']
    #TO DO add swap as an option to allow switching tracks 3&4 with tracks 1&2
    if not args.mixdown in mixdown_list:
        print("The selected audio mixdown is not a valid value")
        print ("please use one of: copy, swap, 4to3, 4to2")
        quit()  

def ffprobe_report(filename, input_file_abspath):
    '''
    returns nested dictionary with ffprobe metadata
    '''
    video_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=codec_name,avg_frame_rate,codec_time_base,width,height,pix_fmt,sample_aspect_ratio,display_aspect_ratio,color_range,color_space,color_transfer,color_primaries,chroma_location,field_order,codec_tag_string', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
    audio_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_long_name,bits_per_raw_sample,sample_rate,channels', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
    format_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-show_entries', 'format=duration,size,nb_streams', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
    data_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 'd', '-show_entries', 'stream=codec_tag_string', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
    attachment_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 't', '-show_entries', 'stream_tags=filename', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
    
    #cleaning up attachment output
    tags = [streams.get('tags') for streams in (attachment_output['streams'])]
    attachment_list = []
    for i in tags:
        attachmentFilename = [i.get('filename')]
        attachment_list.extend(attachmentFilename)
    
    #parse ffprobe metadata lists
    video_codec_name_list = [stream.get('codec_name') for stream in (video_output['streams'])]
    audio_codec_name_list = [stream.get('codec_long_name') for stream in (audio_output['streams'])]
    data_streams = [stream.get('codec_tag_string') for stream in (data_output['streams'])]
    width = [stream.get('width') for stream in (video_output['streams'])][0]
    height = [stream.get('height') for stream in (video_output['streams'])][0]
    pixel_format = [stream.get('pix_fmt') for stream in (video_output['streams'])][0]
    sar = [stream.get('sample_aspect_ratio') for stream in (video_output['streams'])][0]
    dar = [stream.get('display_aspect_ratio') for stream in (video_output['streams'])][0]
    framerate = [stream.get('avg_frame_rate') for stream in (video_output['streams'])][0]
    color_space = [stream.get('color_space') for stream in (video_output['streams'])][0]
    color_range = [stream.get('color_range') for stream in (video_output['streams'])][0]
    color_transfer = [stream.get('color_transfer') for stream in (video_output['streams'])][0]
    color_primaries = [stream.get('color_primaries') for stream in (video_output['streams'])][0]
    audio_bitrate = [stream.get('bits_per_raw_sample') for stream in (audio_output['streams'])]
    audio_sample_rate = [stream.get('sample_rate') for stream in (audio_output['streams'])]
    audio_channels = [stream.get('channels') for stream in (audio_output['streams'])]
    audio_stream_count = len(audio_codec_name_list)
    
    file_metadata = {
    'filename' : filename,
    'file size' : format_output.get('format')['size'],
    'duration' : format_output.get('format')['duration'],
    'streams' : format_output.get('format')['nb_streams'],
    'video streams' : video_codec_name_list,
    'audio streams' : audio_codec_name_list,
    'data streams' : data_streams,
    'attachments' : attachment_list
    }
    
    techMetaV = {
    'width' : width,
    'height' : height,
    'sample aspect ratio' : sar,
    'display aspect ratio' : dar,
    'pixel format' : pixel_format,
    'framerate' : framerate,
    'color space' : color_space,
    'color range' : color_range,
    'color primaries' : color_primaries,
    'color transfer' : color_transfer
    }
    
    techMetaA = {
    'audio stream count' : audio_stream_count,
    'audio bitrate' : audio_bitrate,
    'audio sample rate' : audio_sample_rate,
    'channels' : audio_channels
    }
    
    ffprobe_metadata = {'file metadata' : file_metadata, 'techMetaV' : techMetaV, 'techMetaA' : techMetaA}
    
    return ffprobe_metadata

def ffv1_lossless_transcode(input_metadata, transcode_nameDict, audioStreamCounter):
    #get relevant names from nameDict
    inputAbsPath = transcode_nameDict.get('inputAbsPath')
    tempMasterFile = transcode_nameDict.get('tempMasterFile')
    framemd5AbsPath = transcode_nameDict.get('framemd5AbsPath')
    outputAbsPath = transcode_nameDict.get('outputAbsPath')
    framemd5File = transcode_nameDict.get('framemd5File')
    
    #create ffmpeg command
    ffmpeg_command = [args.ffmpeg_path]
    if not args.verbose:
        ffmpeg_command.extend(('-loglevel', 'error'))
    ffmpeg_command.extend(['-i', inputAbsPath, '-map', '0', '-dn', '-c:v', 'ffv1', '-level', '3', '-g', '1', '-slices', str(args.ffv1_slice_count), '-slicecrc', '1'])
    #TO DO: consider putting color data in a list or dict to replace the following if statements with a single if statement in a for loop
    if input_metadata['techMetaV']['color primaries']:
        ffmpeg_command.extend(('-color_primaries', input_metadata['techMetaV']['color primaries']))
    if input_metadata['techMetaV']['color transfer']:
        ffmpeg_command.extend(('-color_trc', input_metadata['techMetaV']['color transfer']))
    if input_metadata['techMetaV']['color space']:
        ffmpeg_command.extend(('-colorspace', input_metadata['techMetaV']['color space']))
    if audioStreamCounter > 0:
        ffmpeg_command.extend(('-c:a', 'copy'))
    ffmpeg_command.extend((tempMasterFile if args.embed_framemd5 else outputAbsPath, '-f', 'framemd5', '-an', framemd5AbsPath))

    #execute ffmpeg command
    subprocess.run(ffmpeg_command)

    #remux to attach framemd5
    if args.embed_framemd5:
        add_attachment = [args.ffmpeg_path, '-loglevel', 'error', '-i', tempMasterFile, '-c', 'copy', '-map', '0', '-attach', framemd5AbsPath, '-metadata:s:t:0', 'mimetype=application/octet-stream', '-metadata:s:t:0', 'filename=' + framemd5File, outputAbsPath]    
        if os.path.isfile(tempMasterFile):
            subprocess.call(add_attachment)
            filesToDelete = [tempMasterFile, framemd5AbsPath]
            delete_files(filesToDelete)
        else:
            print ("There was an issue finding the file", tempMasterFile)

def delete_files(list):
    '''
    Loops through a list of files and tries to delete them
    '''
    for i in list:
        try:
            os.remove(i)
        except FileNotFoundError:
            print ("unable to delete " + i)
            print ("File not found")

def checksum_streams(input, audioStreamCounter):
    '''
    Gets the stream md5 of a file
    Uses both video and all audio streams if audio is present
    '''
    stream_sum=[]
    stream_sum_command = [args.ffmpeg_path, '-loglevel', 'error', '-i', input, '-map', '0:v', '-an']
    
    stream_sum_command.extend(('-f', 'md5', '-'))
    video_stream_sum = subprocess.check_output(stream_sum_command).decode("ascii").rstrip()
    stream_sum.append(video_stream_sum.replace('MD5=', ''))
    for i in range(audioStreamCounter):
        audio_sum_command = [args.ffmpeg_path]
        audio_sum_command += ['-loglevel', 'error', '-y', '-i', input]
        audio_sum_command += ['-vn', '-map', '0:a:%(a)s' % {"a" : i}]
        audio_sum_command += ['-c:a', 'pcm_s24le', '-f', 'md5', '-']
        audio_stream_sum = subprocess.check_output(audio_sum_command).decode("ascii").rstrip()
        stream_sum.append(audio_stream_sum.replace('MD5=', ''))
    return stream_sum

def two_pass_h264_encoding(audioStreamCounter, outputAbsPath, acAbsPath):
    if os.name == 'nt':
        nullOut = 'NUL'
    else:
        nullOut = '/dev/null'
    pass1 = [args.ffmpeg_path]
    if not args.verbose:
        pass1 += ['-loglevel', 'error']
    pass1 += ['-y', '-i', outputAbsPath, '-c:v', 'libx264', '-preset', 'medium', '-b:v', '8000k', '-pix_fmt', 'yuv420p', '-pass', '1']
    if audioStreamCounter > 0:
        if args.mixdown == 'copy':    
            pass1 += ['-c:a', 'aac', '-b:a', '128k']
        if args.mixdown == '4to3' and audioStreamCounter == 4:
            pass1 += ['-filter_complex', '[0:a:0][0:a:1]amerge=inputs=2[a]', '-map', '0:v', '-map', '[a]', '-map', '0:a:2', '-map', '0:a:3']
        if args.mixdown == '4to2' and audioStreamCounter == 4:
            pass1 += ['-filter_complex', '[0:a:0][0:a:1]amerge=inputs=2[a];[0:a:2][0:a:3]amerge=inputs=2[b]', '-map', '0:v', '-map', '[a]', '-map', '[b]']
    pass1 += ['-f', 'mp4', nullOut]
    pass2 = [args.ffmpeg_path]
    if not args.verbose:
        pass2 += ['-loglevel', 'error']
    pass2 += ['-y', '-i', outputAbsPath, '-c:v', 'libx264', '-preset', 'medium', '-b:v', '8000k', '-pix_fmt', 'yuv420p', '-pass', '2']
    if audioStreamCounter > 0:
        if args.mixdown == 'copy':
            pass2 += ['-c:a', 'aac', '-b:a', '128k']
        if args.mixdown == '4to3' and audioStreamCounter == 4:
            pass2 += ['-filter_complex', '[0:a:0][0:a:1]amerge=inputs=2[a]', '-map', '0:v', '-map', '[a]', '-map', '0:a:2', '-map', '0:a:3']
        if args.mixdown == '4to2' and audioStreamCounter == 4:
            pass2 += ['-filter_complex', '[0:a:0][0:a:1]amerge=inputs=2[a];[0:a:2][0:a:3]amerge=inputs=2[b]', '-map', '0:v', '-map', '[a]', '-map', '[b]']
    pass2 += [acAbsPath]
    subprocess.run(pass1)
    subprocess.run(pass2)

def generate_spectrogram(input, channel_layout_list, outputFolder, outputName):
    '''
    Creates a spectrogram for each audio track in the input
    '''
    spectrogram_resolution = "1928x1080"
    for index, item in enumerate(channel_layout_list):
        output = os.path.join(outputFolder, outputName + '_0a' + str(index) + '.png')
        spectrogram_args = [args.ffmpeg_path]
        spectrogram_args += ['-loglevel', 'error', '-y']
        spectrogram_args += ['-i', input, '-lavfi']
        if item > 1:
            spectrogram_args += ['[0:a:%(a)s]showspectrumpic=mode=separate:s=%(b)s' % {"a" : index, "b" : spectrogram_resolution}]
        else:
            spectrogram_args += ['[0:a:%(a)s]showspectrumpic=s=%(b)s' % {"a" : index, "b" : spectrogram_resolution}]
        spectrogram_args += [output]
        subprocess.run(spectrogram_args)

def generate_qctools(input):
    '''
    uses qcli to generate a QCTools report
    '''
    qctools_args = [args.qcli_path, '-i', input]
    subprocess.run(qctools_args)

def mediaconch_policy_check(input, policy):
    mediaconchResults = subprocess.check_output([args.mediaconch_path, '--policy=' + policy, input]).decode("ascii").rstrip().split()[0]
    if mediaconchResults == "pass!":
        mediaconchResults = "PASS"
    else:
        mediaconchResults = "FAIL"
    return mediaconchResults

def mediaconch_implementation_check(input):
    mediaconchResults = subprocess.check_output([args.mediaconch_path, input]).decode("ascii").rstrip().split()[0]
    if mediaconchResults == "pass!":
        mediaconchResults = "PASS"
    else:
        mediaconchResults = "FAIL"
    return mediaconchResults

def generate_system_log(ffvers, tstime, tftime):
    #gather system info for json output
    osinfo = platform.platform()
    systemInfo = {
    'operating system': osinfo,
    'ffmpeg version': ffvers,
    'transcode start time': tstime,
    'transcode end time': tftime
    #TO DO: add capture software/version maybe -- would have to pull from csv
    }
    return systemInfo

def qc_results(inventoryCheck, losslessCheck, mediaconchResults):
    QC_results = {}
    QC_results['QC'] = {
    'Inventory Check': inventoryCheck,
    'Lossless Check': losslessCheck,
    'Mediaconch Results': mediaconchResults,
    }
    return QC_results

def guess_date(string):
    for fmt in ["%m/%d/%Y", "%d-%m-%Y", "%m/%d/%y", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            continue
    raise ValueError(string)

def generate_coding_history(coding_history, hardware, append_list):
    '''
    Formats hardware into BWF style coding history. Takes a piece of hardware (formatted: 'model; serial No.'), splits it at ';' and then searches the equipment dictionary for that piece of hardware. Then iterates through a list of other fields to append in the free text section. If the hardware is not found in the equipment dictionary this will just pull the info from the csv file and leave out some of the BWF formatting.
    '''
    equipmentDict = equipment_dict.equipment_dict()
    if hardware.split(';')[0] in equipmentDict.keys():
        hardware_history = equipmentDict[hardware.split(';')[0]]['Coding Algorithm'] + ',' + 'T=' + hardware
        for i in append_list:
            if i:
                hardware_history += '; '
                hardware_history += i
        if 'Hardware Type' in equipmentDict.get(hardware.split(';')[0]):
            hardware_history += '; '
            hardware_history += equipmentDict[hardware.split(';')[0]]['Hardware Type']
        coding_history.append(hardware_history)
    #handle case where equipment is not in the equipmentDict using a more general format
    elif hardware and not hardware.split(';')[0] in equipmentDict.keys():
        hardware_history = hardware
        for i in append_list:
            if i:
                hardware_history += '; '
                hardware_history += i
        coding_history.append(hardware_history)
    else:
        pass
    return coding_history
    
def import_csv(csvInventory):
    csvDict = {}
    try:
        with open(csvInventory, encoding='utf-8')as f:
            reader = csv.DictReader(f, delimiter=',')
            video_fieldnames_list = ['File name', 'Accession number/Call number', 'ALMA number/Finding Aid', 'Barcode', 'Title', 'Record Date/Time', 'Housing/Container/Cassette Markings', 'Description', 'Condition', 'Format', 'Capture Date', 'Digitization Operator', 'VTR', 'VTR Output Used', 'Tape Brand', 'Tape Record Mode', 'TBC', 'TBC Output Used', 'ADC', 'Capture Card', 'Sound', 'Region', 'Capture notes']
            missing_fieldnames = [i for i in video_fieldnames_list if not i in reader.fieldnames]
            if not missing_fieldnames:
                for row in reader:
                    name = row['File name']
                    id1 = row['Accession number/Call number']
                    id2 = row['ALMA number/Finding Aid']
                    id3 = row['Barcode']
                    title = row['Title']
                    record_date = row['Record Date/Time']
                    container_markings = row['Housing/Container/Cassette Markings']
                    container_markings = container_markings.split('\n')
                    description = row['Description']
                    condition_notes = row['Condition']
                    format = row['Format']
                    captureDate = row['Capture Date']
                    #try to format date as yyyy-mm-dd if not formatted correctly
                    if captureDate:
                        captureDate = str(guess_date(captureDate))
                    digitizationOperator = row['Digitization Operator']
                    vtr = row['VTR']
                    vtrOut = row['VTR Output Used']
                    tapeBrand = row['Tape Brand']
                    recordMode = row['Tape Record Mode']
                    tbc = row['TBC']
                    tbcOut = row['TBC Output Used']
                    adc = row['ADC']
                    dio = row['Capture Card']
                    sound = row['Sound']
                    sound = sound.split('\n')
                    region = row['Region']
                    capture_notes = row['Capture notes']
                    coding_history = []
                    coding_history = generate_coding_history(coding_history, vtr, [tapeBrand, recordMode, region, vtrOut])
                    coding_history = generate_coding_history(coding_history, tbc, [tbcOut])
                    coding_history = generate_coding_history(coding_history, adc, [None])
                    coding_history = generate_coding_history(coding_history, dio, [None])
                    csvData = {
                    'Accession number/Call number' : id1,
                    'ALMA number/Finding Aid' : id2,
                    'Barcode' : id3,
                    'Title' : title,
                    'Record Date' : record_date,
                    'Container Markings' : container_markings,
                    'Description' : description,
                    'Condition Notes' : condition_notes,
                    'Format' : format,
                    'Digitization Operator' : digitizationOperator,
                    'Capture Date' : captureDate,
                    'Coding History' : coding_history,
                    'Sound Note' : sound,
                    'Capture Notes' : capture_notes
                    }
                    csvDict.update({name : csvData})
            elif not 'File name' in missing_fieldnames:
                print("WARNING: Unable to find all column names in csv file")
                print("File name column found. Interpreting csv file as file list")
                print("CONTINUE? (y/n)")
                yes = {'yes','y', 'ye', ''}
                no = {'no','n'}
                choice = input().lower()
                if choice in yes:
                   for row in reader:
                        name = row['File name']
                        csvData = {}
                        csvDict.update({name : csvData})
                elif choice in no:
                   quit()
                else:
                   sys.stdout.write("Please respond with 'yes' or 'no'")
                   quit()
            else:
                print("No matching column names found in csv file")
            #print(csvDict)
    except FileNotFoundError:
        print("Issue importing csv file")
    return csvDict

def convert_runtime(duration):
    runtime = time.strftime("%H:%M:%S", time.gmtime(float(duration)))
    return runtime

def write_output_csv(outdir, csvHeaderList, csvWriteList, output_metadata, qcResults):
    csv_file = os.path.join(outdir, "qc_log.csv")
    csvOutFileExists = os.path.isfile(csv_file)

    with open(csv_file, 'a') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        if not csvOutFileExists:
            writer.writerow(csvHeaderList)
        writer.writerow(csvWriteList)

def create_json(jsonAbsPath, systemInfo, input_metadata, mov_stream_sum, mkvHash, mkv_stream_sum, baseFilename, output_metadata, item_csvDict, qcResults):
    input_techMetaV = input_metadata.get('techMetaV')
    input_techMetaA = input_metadata.get('techMetaA')
    input_file_metadata = input_metadata.get('file metadata')
    output_techMetaV = output_metadata.get('techMetaV')
    output_techMetaA = output_metadata.get('techMetaA')
    output_file_metadata = output_metadata.get('file metadata')
     
    #create dictionary for json output
    data = {}
    data[baseFilename] = []

    #gather pre and post transcode file metadata for json output
    mov_file_meta = {}
    ffv1_file_meta = {}
    #add stream checksums to metadata
    mov_md5_dict = {'a/v streamMD5s': mov_stream_sum}
    ffv1_md5_dict = {'md5 checksum': mkvHash, 'a/v streamMD5s': mkv_stream_sum}
    input_file_metadata = {**input_file_metadata, **mov_md5_dict}
    output_file_metadata = {**output_file_metadata, **ffv1_md5_dict}
    ffv1_file_meta = {'post-transcode metadata' : output_file_metadata}
    mov_file_meta = {'pre-transcode metadata' : input_file_metadata}
    
    #gather technical metadata for json output
    techdata = {}
    video_techdata = {}
    audio_techdata = {}
    techdata['technical metadata'] = []
    video_techdata = {'video' : input_techMetaV}
    audio_techdata = {'audio' : input_techMetaA}
    techdata['technical metadata'].append(video_techdata)
    techdata['technical metadata'].append(audio_techdata)
    
    #gather metadata from csv dictionary as capture metadata
    csv_metadata = {'inventory metadata' : item_csvDict}
    
    system_info = {'system information' : systemInfo}
    
    data[baseFilename].append(csv_metadata)
    data[baseFilename].append(system_info)
    data[baseFilename].append(ffv1_file_meta)
    data[baseFilename].append(mov_file_meta)        
    data[baseFilename].append(techdata)
    data[baseFilename].append(qcResults)
    with open(jsonAbsPath, 'w', newline='\n') as outfile:
        json.dump(data, outfile, indent=4)
