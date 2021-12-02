#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import json
import csv
import datetime
import time
from audio_processor import audio_equipment_dict
from audio_processor.audio_processor_parameters import args

def get_immediate_subdirectories(folder):
    '''
    get list of immediate subdirectories of input
    '''
    return [name for name in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, name))]

def create_output_folder(folder):
    if not os.path.isdir(folder):
        try:
            os.mkdir(folder)
        except:
            print ("unable to create output folder:", folder)
            quit()
    else:
        print ("using existing folder", folder, "as output")

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

def ffprobe_report(filename, input_file_abspath):
    '''
    returns nested dictionary with ffprobe metadata
    '''
    audio_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_long_name,bits_per_raw_sample,sample_rate,channels', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())
    format_output = json.loads(subprocess.check_output([args.ffprobe_path, '-v', 'error', '-show_entries', 'format=duration,size,nb_streams', input_file_abspath, '-of', 'json']).decode("ascii").rstrip())

    audio_codec_name_list = [stream.get('codec_long_name') for stream in (audio_output['streams'])][0]
    audio_bitrate = [stream.get('bits_per_raw_sample') for stream in (audio_output['streams'])][0]
    audio_sample_rate = [stream.get('sample_rate') for stream in (audio_output['streams'])][0]
    audio_channels = [stream.get('channels') for stream in (audio_output['streams'])][0]

    file_metadata = {
    'filename' : filename,
    'file size' : format_output.get('format')['size'],
    'duration' : format_output.get('format')['duration'],
    'streams' : format_output.get('format')['nb_streams'],
    'audio streams' : audio_codec_name_list
    }

    techMetaA = {
    'audio bitrate' : audio_bitrate,
    'audio sample rate' : audio_sample_rate,
    'channels' : audio_channels
    }

    ffprobe_metadata = {'file metadata' : file_metadata, 'techMetaA' : techMetaA}

    return ffprobe_metadata

def generate_spectrogram(input, channel_layout, outputFolder, outputName):
    '''
    Creates a spectrogram for each audio track in the input
    '''
    spectrogram_resolution = "1928x1080"
    output = os.path.join(outputFolder, outputName + '_0a0' + '-spectrogram' + '.png')
    spectrogram_args = [args.ffmpeg_path]
    spectrogram_args += ['-loglevel', 'error', '-y']
    spectrogram_args += ['-i', input, '-lavfi']
    if channel_layout > 1:
        spectrogram_args += ['[0:a:%(a)s]showspectrumpic=mode=separate:s=%(b)s' % {"a" : '0', "b" : spectrogram_resolution}]
    else:
        spectrogram_args += ['[0:a:%(a)s]showspectrumpic=s=%(b)s' % {"a" : '0', "b" : spectrogram_resolution}]
    spectrogram_args += [output]
    subprocess.run(spectrogram_args)

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
