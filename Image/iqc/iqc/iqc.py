#!/usr/bin/env python3

#TO DO - Organize functions better
#TO DO - add a way to handle checksum files with path information in them

import json
from pathlib import Path
from datetime import datetime
import sys
import os
import glob
import pandas as pd
from functools import reduce
import hashlib
import subprocess
from PIL import Image
from iqc.iqcparameters import args

def input_check():
    '''Checks if input was provided and if it is a directory that exists'''
    if args.input_path:
        indir = args.input_path
    else:
        print ("No input provided")
        quit()

    if not os.path.isdir(indir):
        print('input is not a directory')
        quit()
    return indir

def generate_checksums(filename, file, checksum_type):
    '''Uses hashlib to return an MD5 checksum of an input filename'''
    read_size = 0
    last_percent_done = 0
    method_to_call = getattr(hashlib, checksum_type)
    chksm = method_to_call()
    total_size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        while True:
            #2**20 is for reading the file in 1 MiB chunks
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            chksm.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write(checksum_type + ' ' + file + ': ' + '[%d%%]\r' % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
        print()
    checksum_output = chksm.hexdigest()
    return checksum_output

def interpret_checksum_command():
    '''checks if argument used with verify_checksums is valid'''
    checksum_list = ['md5', 'sha1']
    for i in args.verify_checksums:
        if not i in checksum_list:
            print('\n---ERROR: ' + i + ' is not a valid checksum input ---\n')
            quit()

def output_check():
    '''Checks that output is valid'''
    output = args.output_path
    if not output.endswith('.json'):
        print("\n--- ERROR: Output must be a JSON file ---\n")
        quit()
    #print("Checking output path")
    try:
        with open(output, 'w', newline='\n') as outfile:
            outfile.close
    except OSError:
        print("\n--- ERROR: Unable to create output file", output + ' ---\n')
        quit()


def image_handler(file, subdir, cleanSubdir, parameter_dict, inventorydf, column_to_match):
    '''create dictionary that forms the basis for dataframes for found images'''
    filepath = os.path.join(subdir, file)
    for i in parameter_dict['Images']['extension']:
        if file.endswith(i):
            parameter_dict['Images']['row_counter'] += 1
            rowNumber = "row_" + str(parameter_dict['Images']['row_counter'])
            name = Path(file).stem
            attribute_list = [file, name, cleanSubdir, i]
            if args.verify_checksums:
                for a in args.verify_checksums:
                    sumtype = a + 'sum'
                    sumtype = [generate_checksums(filepath, file, a)]
                    attribute_list += sumtype
            if args.techdata:
                print("checking technical metadata for " + file)
                techresults = []
                isgrayscale = is_grayscale(filepath)
                profile = load_profile(file, inventorydf, column_to_match, isgrayscale)
                techmetadata = get_tech_metadata(filepath)
                if not str(techmetadata.get('BitsPerSample')) == profile.get('Bit Depth'):
                    bit_depth_check = 'FAIL'
                else:
                    bit_depth_check = 'PASS'
                if not techmetadata.get('ProfileDescription') in profile.get('Profile Description'):
                    profile_check = 'FAIL'
                else:
                    profile_check = 'PASS'
                attribute_list += [bit_depth_check, profile_check]
            fileAttributes = {rowNumber: attribute_list}
            parameter_dict['Images']['dictionary'].update(fileAttributes)

def checksum_handler(file, subdir, cleanSubdir, parameter_dict):
    '''pull information out of checksum files'''
    for i in parameter_dict.keys():
        if file.endswith(parameter_dict[i]['extension']):
            parameter_dict[i]['row_counter'] += 1
            rowNumber = "row_" + str(parameter_dict[i]['row_counter'])
            name = Path(file).stem
            '''remove double stem if present (i.e. .tif.md5)'''
            if '.' in name:
                name = Path(name).stem
            with open(os.path.join(subdir, file)) as f:
                content = f.readlines()
                content = [line.rstrip('\n') for line in content]
            for value in content:
                if '*' in value:
                    checksum_filename = value.split('*')[1]
                elif ' = ' in value:
                    checksum_filename = value.split(' = ')[0]
                else:
                    checksum_filename = value.split('  ')[1]
                if '  ' in value or '*' in value:
                    checksum_value = value.split(' ')[0]
                elif ' = ' in value:
                    checksum_value = value.split(' = ')[1]
                else:
                    print ('having trouble parsing checksums')
                    print ('are they formatted correctly?')
                    quit()
            cleanup_characters = ['./', 'MD5 ', 'SHA1 ', '(', ')']
            for chars in cleanup_characters:
                if chars in checksum_filename:
                    checksum_filename = checksum_filename.replace(chars, '')
            fileAttributes = {rowNumber: [name, file, cleanSubdir, checksum_filename, checksum_value]}
            parameter_dict[i]['dictionary'].update(fileAttributes)

def exiftool_check():
    '''checks that exiftool exists by running its -ver command'''
    try:
        subprocess.check_output([args.exiftool_path, '-ver']).decode("ascii").rstrip()
    except:
        print("Error locating exiftool")
        quit()

def get_iptc_metadata(filename, filepath, column_to_match, exifmetalist):
    '''Run exiftool to get IPTC metadata'''
    #TO DO - Feed this a list of exiftool fields to check rather than hard coding them in the command?
    exiftool_command = [args.exiftool_path, '-headline', '-by-line', '-source', '-copyrightnotice', '-j', filepath]
    exifdata = subprocess.check_output(exiftool_command)
    exifdata = json.loads(exifdata)
    exifdata[0][column_to_match] = filename
    exifmetalist += (exifdata)

def get_directory_size(directory):
    #credit: How to Get the Size of Directories in Python, Abdou Rockikz
    '''Returns the `directory` size in bytes'''
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total

def get_size_format(b, factor=1024, suffix="B"):
    #credit: How to Get the Size of Directories in Python, Abdou Rockikz
    '''
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    '''
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def is_grayscale(img_path):
    '''check if image is grayscale. Return true/false'''
    #TO DO - set max_image_pixels to a reasonable limit?
    Image.MAX_IMAGE_PIXELS = None
    img = Image.open(img_path).convert('RGB')
    MAX_SIZE = (500, 500)
    img.thumbnail(MAX_SIZE)
    w, h = img.size
    for i in range(w):
        for j in range(h):
            r, g, b = img.getpixel((i,j))
            if r != g != b:
                return False
    return True

def load_profile(filename, inventorydf, column_to_match, isgrayscale):
    #probably better to store these in an external json file in a data folder so they'll be easier to edit
    p_techmetadata = {"Bit Depth": "16 16 16", "Profile Description": ["ProPhoto"]}
    a_techmetadata = {"Color": {"Bit Depth": "8 8 8", "Profile Description": ["Adobe RGB (1998)"]}, "Grayscale": {"Bit Depth": "8", "Profile Description": ["Gray Gamma 2.2"]}}
    empty_techmetadata = {"Bit Depth": "", "Profile Description": ""}
    role = ''.join(inventorydf.loc[inventorydf[column_to_match] == filename]['role'].values)
    if not role:
        profile = empty_techmetadata
    elif role == 'P':
        profile = p_techmetadata
    elif role == 'A' and isgrayscale == False:
        profile = a_techmetadata.get('Color')
    elif role == 'A' and isgrayscale == True:
        profile = a_techmetadata.get('Grayscale')
    else:
        profile = empty_techmetadata
    return profile

def get_tech_metadata(filepath):
    exif_command = [args.exiftool_path, '-profiledescription', '-bitspersample', '-a', '-j', filepath]
    exifdata = subprocess.check_output(exif_command)
    exifdata = json.loads(exifdata)
    exifdata = exifdata[0]
    return exifdata

def iqc_main():
    column_to_match = 'filename'
    indir = args.input_path
    input_check()
    base_folder_name = os.path.basename(indir)
    #script will default to writing json report in input file if using --all and not specifying an output
    if args.all and not args.output_path:
        args.output_path = os.path.join(indir, base_folder_name + '_report.json')
    if args.output_path:
        output_check()
    if args.verify_metadata:
        exiftool_check()
        exifmetalist = []

    if args.verify_checksums:
        interpret_checksum_command()
    #get the input folder size
    input_folder_size = get_size_format(get_directory_size(indir))

    #import inventories as dataframe
    if not args.inventory_path:
        inventoryPath = indir
        if os.path.isdir(inventoryPath):
            inventories = glob.glob(os.path.join(inventoryPath, "*.csv"))
            if not inventories:
                print("\n--- ERROR: No inventory found. Either specify your inventories or place them in the base folder of your input directory ---\n")
                quit()
            inventorydf = pd.concat([pd.read_csv(inv, skiprows=0, header=0) for inv in inventories])
        else:
            print('\n--- ERROR: Inventory path is not valid ---\n')
            quit()
    else:
        inventoryPath = args.inventory_path
        if inventoryPath.endswith('.csv'):
            if os.path.isfile(inventoryPath):
                inventorydf =  pd.read_csv(inventoryPath, skiprows=0, header=0)
            else:
                print('\n--- ERROR: Supplied inventory path is not valid ---\n')
                quit()
        else:
            if os.path.isdir(inventoryPath):
                inventories = glob.glob(os.path.join(inventoryPath, "*.csv"))
                if not inventories:
                    print("\n--- ERROR: The specified inventory folder does not contain any CSV files ---\n")
                    quit()
                #Note - header=1 is used to grab the second row of the spreadsheet as the header row
                #use header=0 for csv files where the first row is the header row
                inventorydf = pd.concat([pd.read_csv(inv, skiprows=0, header=0) for inv in inventories])
            else:
                print('\n--- ERROR: Supplied inventory path is not valid ---\n')
                quit()

    #create dictionaries containing the formats we want to process
    image_dictionary = {'Images' : { 'extension' : ['.tif'], 'row_counter' : 0, 'dictionary' : {}}}
    #TO DO - review/update checksum implementation now that script has been changed to only check one type at a time
    checksum_sidecar_dictionary = {'MD5' : { 'extension' : '.md5', 'row_counter' : 0, 'dictionary' : {}}, 'SHA1' : { 'extension' : '.sha1', 'row_counter' : 0, 'dictionary' : {}}}

    #search input and process specified files
    for subdir, dirs, files in os.walk(indir):
        cleanSubdir = (subdir.replace(indir, ''))
        #skip hidden files and folders
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            #TO DO - reduce the number of variables getting passed around
            image_handler(file, subdir, cleanSubdir, image_dictionary, inventorydf, column_to_match)
            checksum_handler(file, subdir, cleanSubdir, checksum_sidecar_dictionary)
            if args.verify_metadata:
                for i in image_dictionary['Images']['extension']:
                    #TO DO - This most likely is not the most efficient way to do this
                    #try merging with related image handler steps instead
                    if file.endswith(i):
                        print("checking IPTC metadata for " + file)
                        get_iptc_metadata(file, os.path.join(subdir, file), column_to_match, exifmetalist)

    #test if these can be grabbed using something like exiftool -By-line -a image?
    if args.verify_metadata:
        exifdf = pd.DataFrame.from_records(exifmetalist)
        exifdf = exifdf[[column_to_match, 'By-line', 'Headline', 'Source', 'CopyrightNotice']]

    '''determine column headers for image dataframe based on arguments used'''
    image_columns = [column_to_match, 'base filename', 'file path', 'extension']
    if args.verify_checksums:
        for i in args.verify_checksums:
            column_name = 'calculated ' + i + ' checksum'
            image_columns += [column_name]
    if args.techdata:
        image_columns += ["Bit Depth Check", "Color Profile Check"]

    imagedf = pd.DataFrame.from_dict(image_dictionary['Images']['dictionary'], orient='index', columns=image_columns)
    md5df = pd.DataFrame.from_dict(checksum_sidecar_dictionary['MD5']['dictionary'], orient='index', columns=['base filename', 'md5 filename', 'md5 path', 'filename in md5 checksum', 'md5 checksum value'])
    sha1df = pd.DataFrame.from_dict(checksum_sidecar_dictionary['SHA1']['dictionary'], orient='index', columns=['base filename', 'sha1 filename', 'sha1 path', 'filename in sha1 checksum', 'sha1 checksum value'])

    #count the number of items in inventory
    inventory_count = len(inventorydf.index)
    #count the number of images
    image_count = len(imagedf.index)

    #returns a df of just the target files
    targetdf = imagedf[imagedf[column_to_match].str.contains("_target.tif", na=False)]
    #count the number of target files found
    target_count = len(targetdf.index)

    #filter out targets from imagedf using the inverse of the target filter
    imagedf = imagedf[~imagedf[column_to_match].str.contains("_target.tif", na=False)]
    #returns df of images not found in inventory
    df3 = imagedf.merge(inventorydf, how='left', on=column_to_match, indicator="Status").query('Status == "left_only"')
    #returns df of inventory entries with no tif file
    df4 = imagedf.merge(inventorydf, how='right', on=column_to_match, indicator="Status").query('Status == "right_only"')
    #creates DF of combined inventory and file DFs
    df_merged = inventorydf.merge(imagedf, how='left', on=column_to_match)

    if args.verify_metadata:
        df_merged = df_merged.merge(exifdf, how='left', on=column_to_match)
        #remove target files and instances where there is no file/inventory entry to match
        clean_exifdf = pd.merge(exifdf, df3[column_to_match], on=column_to_match, how='outer', indicator='exifdfmatch').query("exifdfmatch == 'left_only'")
        clean_exifdf = clean_exifdf[~clean_exifdf[column_to_match].str.contains("_target.tif", na=False)]
        if args.strict:
            metadf_failures = pd.merge(clean_exifdf, inventorydf, left_on=[column_to_match, 'By-line', 'Headline', 'Source', 'CopyrightNotice'], right_on=[column_to_match, 'Creator', 'Headline', 'Source', 'Copyright Notice'], how='outer', indicator='metamatch').query("metamatch == 'left_only'")
        else:
            copyright_pattern = '|'.join(r"{}".format(x) for x in exifdf['CopyrightNotice'])
            inventorydf['copyright_pattern_match'] = inventorydf['Copyright Notice'].str.extract('('+ copyright_pattern +')', expand=False)
            copyright_partial_match = pd.merge(clean_exifdf, inventorydf, left_on=[column_to_match, 'CopyrightNotice'], right_on=[column_to_match, 'copyright_pattern_match'], how='outer', indicator="copyright_metadata_status").query("copyright_metadata_status == 'left_only'")

            headline_pattern = '|'.join(r"{}".format(x) for x in exifdf['Headline'])
            inventorydf['headline_pattern_match'] = inventorydf['Headline'].str.extract('('+ headline_pattern +')', expand=False)
            headline_partial_match = pd.merge(clean_exifdf, inventorydf, left_on=[column_to_match, 'Headline'], right_on=[column_to_match, 'headline_pattern_match'], how='outer', indicator="headline_metadata_status").query("headline_metadata_status == 'left_only'")

            byline_pattern = '|'.join(r"{}".format(x) for x in exifdf['By-line'])
            inventorydf['byline_pattern_match'] = inventorydf['Creator'].str.extract('('+ byline_pattern +')', expand=False)
            byline_partial_match = pd.merge(clean_exifdf, inventorydf, left_on=[column_to_match, 'By-line'], right_on=[column_to_match, 'byline_pattern_match'], how='outer', indicator="byline_metadata_status").query("byline_metadata_status == 'left_only'")

            source_pattern = '|'.join(r"{}".format(x) for x in exifdf['Source'])
            inventorydf['source_pattern_match'] = inventorydf['Source'].str.extract('('+ source_pattern +')', expand=False)
            source_partial_match = pd.merge(clean_exifdf, inventorydf, left_on=[column_to_match, 'Source'], right_on=[column_to_match, 'source_pattern_match'], how='outer', indicator="source_metadata_status").query("source_metadata_status == 'left_only'")
            metadf_list = [copyright_partial_match, headline_partial_match, byline_partial_match, source_partial_match]
            #merge all metadata dataframes
            metadf_failures = reduce(lambda left,right: pd.merge(left,right,on=[column_to_match], how='outer'), metadf_list)

    if args.verify_checksums:
        #TO DO - Make this more generic (autofill md5/sha1 based on command)
        if 'md5' in args.verify_checksums and not md5df.empty:
            #TO DO should be a check if the filename in the checksum file matches the checksum base name
            df_merged = df_merged.merge(md5df, how='left', left_on=column_to_match, right_on='filename in md5 checksum')
            missing_md5_df = df_merged[df_merged['md5 checksum value'].isnull()]
            df_merged['checksum_match'] = df_merged['md5 checksum value'].eq(df_merged['calculated md5 checksum'])
            failed_md5_df = df_merged[df_merged['md5 checksum value'].notnull()]
            failed_md5_df = failed_md5_df.loc[failed_md5_df['checksum_match'] == False]
        if 'sha1' in args.verify_checksums and not sha1df.empty:
            df_merged = df_merged.merge(sha1df, how='left', left_on=column_to_match, right_on='filename in sha1 checksum')
            missing_sha1_df = df_merged[df_merged['sha1 checksum value'].isnull()]
            df_merged['checksum_match'] = df_merged['sha1 checksum value'].eq(df_merged['calculated sha1 checksum'])
            failed_sha1_df = df_merged[df_merged['sha1 checksum value'].notnull()]
            failed_sha1_df = failed_sha1_df.loc[failed_sha1_df['checksum_match'] == False]

    if args.techdata:
        cleandf = pd.merge(imagedf, df3[column_to_match], on=column_to_match, how='outer', indicator='present').query("present == 'left_only'")
        bitdepthdf = cleandf.loc[cleandf['Bit Depth Check'] == "FAIL"]
        profiledf = cleandf.loc[cleandf['Color Profile Check'] == "FAIL"]

    #presentation related stuff for reporting
    #TO DO organize this better to reduce repeated and dispersed info - create json dict first, then just pull from it or update values
    #Consider only printing a report in terminal if an output file is NOT specified?
    output_report = {}
    output_report[base_folder_name] = []
    checksum_results = "Not Checked"
    metadata_results = "Not Checked"
    bit_depth_results = "Not Checked"
    profile_results = "Not Checked"
    print("\n--------------- RESULTS ---------------\n")
    report_date = datetime.now().strftime("%m/%d/%Y %I:%M%p")
    print("REPORT DATE:", report_date)
    print("INPUT FOLDER SIZE:", input_folder_size + "\n")
    print("Number of items in inventory: " + str(inventory_count))
    print("Number of TIFF images in input: " + str(image_count))
    print("Number of target files in input: " + str(target_count))
    print("\n**TARGET FILES FOUND IN INPUT: " + str(targetdf[column_to_match].tolist()))
    print("\n**TIFF FILES NOT FOUND IN INVENTORY: " + str(df3[column_to_match].tolist()))
    print("\n**INVENTORY ENTRIES WITH NO MATCHING TIFF FILE: " + str(df4[column_to_match].tolist()) + "\n")
    if args.verify_checksums:
        #more elegant way to format this?
        if md5df.empty and 'md5' in args.verify_checksums:
            print ('+++ WARNING: Unable to verify ' + i + ' checksums. No ' + i + ' checksums were found +++')
            print()
            checksum_results = "Unable to verify md5 checksums. No md5 checksums were found."
        elif 'md5' in args.verify_checksums:
            md5_failures = failed_md5_df[column_to_match].tolist()
            md5_missing = missing_md5_df[column_to_match].tolist()
            print("**MD5 CHECKSUM FAILURES: " + str(md5_failures))
            print("\n**INVENTORY ENTRIES WITH NO MATCHING MD5 FILE: " + str(md5_missing) + "\n")
            if md5_failures or md5_missing:
                checksum_results = [{"MD5 Checksum Failures" : md5_failures, "Inventory Entries with No Matching MD5 File" : md5_missing}]
            else:
                checksum_results = "PASS"
        if sha1df.empty and 'sha1' in args.verify_checksums:
            print ("+++ WARNING: Unable to verify sha1 checksums. No sha1 checksums were found +++\n")
            checksum_results = "Unable to verify sha1 checksums. No sha1 checksums were found."
        elif 'sha1' in args.verify_checksums:
            sha1_failures =failed_sha1_df[column_to_match].tolist()
            sha1_missing = missing_sha1_df[column_to_match].tolist()
            print("**SHA1 CHECKSUM FAILURES: " + str(sha1_failures))
            print("\n**INVENTORY ENTRIES WITH NO MATCHING SHA1 FILE: " + str(sha1_missing) + "\n")
            if sha1_failures or sha1_missing:
                checksum_results = [{"SHA1 Checksum Failures" : sha1_failures, "Inventory Entries with No Matching SHA1 File" : sha1_missing}]
            else:
                checksum_results = "PASS"
    if args.verify_metadata:
        metadata_failures = metadf_failures[column_to_match].tolist()
        print("**IPTC METADATA FAILURES: " + str(metadata_failures) + "\n")
        if metadata_failures:
            metadata_results = metadata_failures
        else:
            metadata_results = "PASS"
    if args.techdata:
        bit_depth_failures = bitdepthdf[column_to_match].tolist()
        profile_failures = profiledf[column_to_match].tolist()
        print("**BIT DEPTH FAILURES: " + str(bit_depth_failures))
        print("\n**COLOR PROFILE FAILURES: " + str(profile_failures) + "\n")
        if bit_depth_failures:
            bit_depth_results = bit_depth_failures
        else:
            bit_depth_results = "PASS"
        if profile_failures:
            profile_results = profile_failures
        else:
            profile_results = "PASS"

    report_data = {
    "Report Date" : report_date,
    "Input Folder Size" : input_folder_size,
    "Inventory Item Count" : inventory_count,
    "TIFF File Count" : image_count,
    "Target File Count" : target_count,
    "Target Files" : targetdf[column_to_match].tolist(),
    "TIFF Files Not Found in Inventory" : df3[column_to_match].tolist(),
    "Inventory Files Not Found in TIFF Files" : df4[column_to_match].tolist(),
    "Checksum Verification" : checksum_results,
    "IPTC Metadata Verification" : metadata_results,
    "Color Profile Check" : bit_depth_results,
    "Bit Depth Check" : profile_results
    }
    output_report[base_folder_name].append(report_data)
    #Write report data to output file
    if args.output_path:
        print ("Writing report to:" + args.output_path)
        with open(args.output_path, 'w', newline='\n') as outfile:
            json.dump(output_report, outfile, indent=4)
        #df_merged.to_csv(args.output_path, sep=',', encoding='utf-8')
    else:
        print('No output specified. Ending process')
        quit()
