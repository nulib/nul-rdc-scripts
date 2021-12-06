#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import json
import csv
import datetime
import time
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

def load_reference_inventory(reference_inventory_file):
    reference_inventory_fieldnames = []
    with open(reference_inventory_file, "r") as f:
        reader = csv.DictReader(f, delimiter=',')
        reference_inventory_fieldnames.extend(reader.fieldnames)
    return(reference_inventory_fieldnames)

def load_item_metadata(file, source_inventory_dict):
    loaded_metadata = None
    for item in source_inventory_dict:
        if item in file:
            loaded_metadata = source_inventory_dict[item]
    if not loaded_metadata:
        print("ERROR: Unable to find matching file for " + file)
        quit()
    return loaded_metadata

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

def verify_csv_exists(csv_file):
    '''
    TODO add doctest
    '''
    if csv_file.endswith('.csv'):
        if not os.path.isfile(csv_file):
            print("ERROR: Unable to locate " + csv_file)
            quit()
    else:
        print("ERROR: " + csv_file + " is not a CSV file")
        quit()

def group_lists(original_list):
    '''
    groups list items by the number found in them
    '''
    grouped_lists = []
    for value in original_list:
        numeric_string = "".join(filter(str.isdigit, value))
        if grouped_lists and "".join(filter(str.isdigit, grouped_lists[-1][0])) == numeric_string:
            grouped_lists[-1].append(value)
        else:
            grouped_lists.append([value])
    return grouped_lists

def create_coding_history(row, encoding_chain_fields, append_list):
    #separates out just the number from the encoding chain field
    #then compares that to the previous entry in the list so that same numbers are grouped
    grouped_field_list = group_lists(encoding_chain_fields)
    coding_history_dict = {}
    coding_history = []

    for encoding_chain in grouped_field_list:
        coding_history_dict = {
            'primary fields' : {
                'coding algorithm' : None,
                'sample rate' : None,
                'word length' : None,
                'sound mode' : None,
            },
            'freetext': {
                'device' : None,
                'id' : None,
                'append fields' : None,
                'ad type' : None
            }
        }
        for i in encoding_chain:
            if i.lower().endswith("hardware"):
                hardware_parser = row[i].split(';')
                hardware_parser = [i.lstrip() for i in hardware_parser]
                if len(hardware_parser) !=3:
                    print("ERROR: Encoding chain hardware does not follow expected formatting")
                coding_history_dict['primary fields']['coding algorithm'] = "A=" + hardware_parser[0]
                #TODO change how T= is added so it is instead just placed before the first entry of the freetext section
                coding_history_dict['freetext']['device'] = "T=" + hardware_parser[1]
                coding_history_dict['freetext']['id'] = hardware_parser[2]
            if i.lower().endswith("mode"):
                coding_history_dict['primary fields']['sound mode'] = "M=" + row[i]
            if i.lower().endswith("digital characteristics"):
                hardware_parser = row[i].split(';')
                hardware_parser = [i.lstrip() for i in hardware_parser]
                if len(hardware_parser) !=2:
                    print("ERROR: Encoding chain digital characteristics does not follow expected formatting")
                coding_history_dict['primary fields']['sample rate'] = "F=" + hardware_parser[0]
                coding_history_dict['primary fields']['word length'] = "W=" +hardware_parser[1]
            if i.lower().endswith("hardware type") and row[i].lower() == "playback deck":
                clean_list = []
                for field in append_list:
                    if field:
                        clean_list.append(field)
                if clean_list:
                    append_fields = '; '.join(clean_list)
                #convert append list to string
                coding_history_dict['freetext']['append fields'] = append_fields
            elif i.lower().endswith("hardware type"):
                coding_history_dict['freetext']['ad type'] = row[i]
        primary_fields = []
        freetext = []
        for key in coding_history_dict['primary fields']:
            if coding_history_dict['primary fields'][key]:
                primary_fields.append(coding_history_dict['primary fields'][key])
        for key in coding_history_dict['freetext']:
            if coding_history_dict['freetext'][key]:
                freetext.append(coding_history_dict['freetext'][key])
        if primary_fields and freetext:
            coding_history_p = ','.join(primary_fields)
            coding_history_t = '; '.join(freetext)
            coding_history_component = coding_history_p + ',' + coding_history_t
            coding_history.append(coding_history_component)
    coding_history = '\r\n'.join(coding_history)
    return(coding_history)

def import_inventories(source_inventories, reference_inventory_list):
    csvDict = {}
    for i in source_inventories:
        verify_csv_exists(i)
        with open(i, encoding='utf-8')as f:
            reader = csv.DictReader(f, delimiter=',')
            cleaned_fieldnames = [a for a in reader.fieldnames if not "encoding chain" in a.lower()]
            encoding_chain_fields = sorted([a for a in reader.fieldnames if "encoding chain" in a.lower()])
            missing_fieldnames = [i for i in reference_inventory_list if not i in cleaned_fieldnames]
            extra_fieldnames = [i for i in cleaned_fieldnames if not i in reference_inventory_list]
            if missing_fieldnames:
                print("WARNING: Your inventory seems to be missing the following columns")
                print(missing_fieldnames)
                quit()
            if extra_fieldnames:
                print("WARNING: Your inventory contains the following extra columns")
                print(extra_fieldnames)
                quit()
            if not encoding_chain_fields:
                print("ERROR: Unable to find encoding chain fields in inventory")
                quit()
            for row in reader:
                name = row['filename']
                record_date = row['Record Date/Time']
                container_markings = row['Housing/Container Markings']
                container_markings = container_markings.split('\n')
                format = row['Format'].lower()
                captureDate = row['Capture Date']
                #try to format date as yyyy-mm-dd if not formatted correctly
                if captureDate:
                    captureDate = str(guess_date(captureDate))
                tapeBrand = row['Tape Brand']
                sound = row['Sound']
                type = row['Tape Type (Cassette)']
                nr = row['Noise Reduction']
                speed = row['Speed IPS']
                coding_history = create_coding_history(row, encoding_chain_fields, [tapeBrand, type, speed, nr])
                #TODO make a more generic expandable coding history builder
                csvData = {
                'Work Accession Number' : row['work_accession_number'],
                'Box/Folder/Alma Number' : row['Box/Folder\nAlma number'],
                'Barcode' : row['Barcode'],
                'Inventory Title' : row['inventory_title'],
                'Record Date' : record_date,
                'Container Markings' : container_markings,
                'Condition Notes' : row['Condition Notes'],
                'Format' : format,
                'Digitization Operator' : row['Digitizer'],
                'Capture Date' : captureDate,
                'Coding History' : coding_history,
                'Sound Note' : sound,
                'Sides' : '',
                'Capture Notes' : row['Digitizer Notes']
                }
                csvDict.update({name : csvData})
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
