#!/usr/bin/env python3

import os
import sys
import re
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
    #TODO error out if multiple matches are found
    loaded_metadata = {}
    for item in source_inventory_dict:
        if item in file:
            loaded_metadata = {item : source_inventory_dict[item]}
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
    #'filename' : filename,
    'file size' : format_output.get('format')['size'],
    'duration' : format_output.get('format')['duration'],
    'streams' : format_output.get('format')['nb_streams'],
    'channels' : audio_channels,
    'audio streams' : audio_codec_name_list,
    'audio sample rate' : audio_sample_rate,
    'audio bitrate' : audio_bitrate
    }

    ffprobe_metadata = {'file metadata' : file_metadata}

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

def generate_system_log():
    #gather system info for json output
    osinfo = platform.platform()
    systemInfo = {
    'operating system': osinfo,
    }
    return systemInfo

def qc_results(inventoryCheck, mediaconchResults):
    QC_results = {}
    QC_results['QC'] = {
    'Inventory Check': inventoryCheck,
    'Mediaconch Results': mediaconchResults
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
                coding_history_dict['primary fields']['word length'] = "W=" + hardware_parser[1]
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
    skip_coding_history = False
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
                print("WARNING: Unable to find encoding chain fields in inventory")
                print("Continue without building Coding History? (y/n)")
                yes = {'yes','y', 'ye', ''}
                no = {'no','n'}
                choice = input().lower()
                if choice in yes:
                   skip_coding_history = True
                elif choice in no:
                   quit()
                else:
                   sys.stdout.write("Please respond with 'yes' or 'no'")
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
                if skip_coding_history is False:
                    coding_history = create_coding_history(row, encoding_chain_fields, [tapeBrand, type, speed, nr])
                else:
                    coding_history = None
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
                'Capture Notes' : row['Digitizer Notes']
                }
                csvDict.update({name : csvData})
    return csvDict

def get_bwf_metadata(pm_file_abspath):
    core_bwf_command = [args.metaedit_path, '--out-core', pm_file_abspath]
    tech_bwf_command = [args.metaedit_path, '--out-tech', pm_file_abspath]
    tech_bwf_csv = subprocess.check_output(tech_bwf_command).decode("ascii").rstrip().splitlines()
    core_bwf_csv = subprocess.check_output(core_bwf_command).decode("ascii").rstrip()
    print(core_bwf_csv)
    quit()

def parse_mediaconchResults(mediaconchResults_dict):
    if "FAIL" in mediaconchResults_dict.values():
        mediaconchResults = "FAIL"
        failed_policies = []
        for key in mediaconchResults_dict.keys():
            if "FAIL" in mediaconchResults_dict.get(key):
                failed_policies.append(key)
        mediaconchResults = mediaconchResults + ': ' + str(failed_policies).strip('[]')
    else:
        mediaconchResults = "PASS"
    return mediaconchResults

def convert_runtime(duration):
    runtime = time.strftime("%H:%M:%S", time.gmtime(float(duration)))
    return runtime

def write_output_csv(outdir, csvHeaderList, csvWriteList, qcResults):
    csv_file = os.path.join(outdir, "qc_log.csv")
    csvOutFileExists = os.path.isfile(csv_file)

    with open(csv_file, 'a') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        if not csvOutFileExists:
            writer.writerow(csvHeaderList)
        writer.writerow(csvWriteList)
