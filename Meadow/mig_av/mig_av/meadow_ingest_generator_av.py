#!/usr/bin/env python3

import os
import argparse
import csv
import glob
import meadow_parser_funcs

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', action='store', dest='input_path', type=str, help='full path to input folder')
parser.add_argument('--output', '-o', action='store', dest='output_path', type=str, help='full path to output csv file')
parser.add_argument('--load_inventory', '-l', required=False, nargs='*', action='store', dest='source_inventory', help='Use to specify an object inventory. If not specified the script will look in the base folder of the input for object inventories. If no inventories are found the script will leave some fields blank.')
parser.add_argument('--skip', '-s', required=False, nargs='*', action='store', dest='skip', help='Use to specify patterns to skip. Can take multiple inputs. For example, "_ac." "_am." could be used to skip legacy ac and am files.')
parser.add_argument('--description', '-d', required=False, nargs='*', action='store', dest='desc', help='Use to specify column names to populate Meadow description field with. Can take multiple inputs. Information from each column will be separated by a ";". Example usage: -d "Date/Time" "Barcode". If not specified, script will default to looking for the column "inventory_title"')
#parser.add_argument('--newline_limit', '-n', required=False, nargs=1, action='store', dest='output_path', type=int, help='Limit fields imported into the description field to a certain number of newlines.')
parser.add_argument('--auxiliary', '-x', required=False, nargs=1, action='store', dest='aux_parse', help='Sets how to parse auxiliary files. Options include: extension (by extension), parse (by word), none (no aux files). Default is none.')

args = parser.parse_args()

def input_check(indir):
    '''Checks if input was provided and if it is a directory that exists'''
    if not indir:
        print ("No input provided")
        quit()

    if not os.path.isdir(indir):
        print('input is not a directory')
        quit()

def output_check(output):
    '''Checks that output is valid'''
    if not output.endswith('.csv'):
        print("\n--- ERROR: Output must be a CSV file ---\n")
        quit()

def interpret_aux_command():
    '''checks if argument passed to aux_parse is valid'''
    aux_parse_list = ['extension', 'parse']
    for i in args.aux_parse:
        if not i in aux_parse_list:
            print('\n---ERROR: ' + i + ' is not a valid input to the auxiliary command ---\n')
            quit()

def update_fieldname_list(original_fieldname_list, missing_fieldname_list):
    fieldname_list = [header for header in original_fieldname_list if header not in missing_fieldname_list]
    return fieldname_list

def missing_description_field_handler(missing_descriptive_fieldnames):
    print("+++ WARNING: Your inventory is missing the following columns +++")
    print(missing_descriptive_fieldnames)
    print("SKIP COLUMNS AND CONTINUE? (y/n)")
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}
    choice = input().lower()
    if choice in yes:
        pass
    elif choice in no:
        quit()

#TODO add early warning if spreadsheet is missing important columns like work_accession_number
def import_inventories(source_inventories):
    '''
    import CSV inventories and parse each row into a dictionary that is added to a list
    We use lists of dicts initially to catch duplicate filenames later on
    TODO Cell wrangling stems from here (description and label)
    '''
    missing_fieldnames = False
    source_inventory_dictlist = []
    for i in source_inventories:
        if i.endswith('.csv'):
            if os.path.isfile(i):
                csvDict = []
                with open(i, encoding='utf-8')as f:
                    reader = csv.DictReader(f, delimiter=',')
                    for row in reader:
                        #work type is assumed by the presence of format-specific column headers
                        if 'Width (cm.)' in reader.fieldnames:
                            work_type = 'IMAGE'
                        elif 'Speed IPS' in reader.fieldnames:
                            work_type = 'AUDIO'
                        elif 'Region' or 'Stock' in reader.fieldnames:
                            work_type = 'VIDEO'
                        name = row['filename']
                        if work_type == 'AUDIO' or work_type == 'VIDEO':
                            if not args.desc:
                                description_fields = ['inventory_title']
                            else:
                                description_fields = args.desc
                            missing_descriptive_fieldnames = [a for a in description_fields if not a in reader.fieldnames]
                            if missing_descriptive_fieldnames:
                                missing_fieldnames = True
                                description_fields = update_fieldname_list(description_fields, missing_descriptive_fieldnames)
                            description_list = []
                            for header in description_fields:
                                #TODO make this its own function since it's probably going to get repeated
                                description_list.append(row[header])
                            description = "; ".join(i for i in description_list if i)
                                #description.update({'descriptive': row[header]})
                            if not 'label' in reader.fieldnames:
                                inventory_label = None
                            else:
                                inventory_label = row['label']
                            #if work_type == "VIDEO" and 'Region' in reader.fieldnames:
                            csvData = {
                            'filename' : row['filename'],
                            'work_type' : work_type,
                            'work_accession_number' : row['work_accession_number'],
                            'description' : description,
                            'label' : inventory_label
                            }
                        elif work_type == 'IMAGE':
                            csvData = {
                            'filename' : row['filename'],
                            'label' : row['label'],
                            'work_type' : work_type,
                            'work_accession_number' : row['work_accession_number'],
                            'file_accession_number' : row['file_accession_number'],
                            'role' : row ['role'],
                            'description' : row['description']
                            }
                        else:
                            print("--- ERROR: Problem identifying work type in " + i + " ---")
                            quit()
                        csvDict.append(csvData)
                        #print(csvDict)
                    if missing_fieldnames == True:
                        missing_description_field_handler(missing_descriptive_fieldnames)
            else:
                print('\n--- ERROR: ' + i + ' is not a file ---\n')
                quit()
        else:
            print('\n--- ERROR: Inventory path is not valid ---\n')
        source_inventory_dictlist.extend(csvDict)
    #print(source_inventory_dictlist)
    #quit()
    return source_inventory_dictlist

#sorted[]
'''setting up inputs and outputs'''
indir = args.input_path
input_check(indir)
if args.output_path:
    meadow_csv_file = args.output_path
else:
    base_folder_name = os.path.basename(indir)
    meadow_csv_file = os.path.join(indir, base_folder_name + '-meadow_ingest_inventory.csv')
output_check(meadow_csv_file)

if args.aux_parse:
    interpret_aux_command()

'''importing inventories'''
if args.source_inventory:
    source_inventories = args.source_inventory
    source_inventory_dictlist = import_inventories(source_inventories)
else:
    print('\n*** Checking input directory for CSV files ***')
    source_inventories = glob.glob(os.path.join(indir, "*.csv"))
    #skip auto-generated meadow ingest csv if it already exists
    source_inventories = [i for i in source_inventories if not '-meadow_ingest_inventory.csv' in i]
    if not source_inventories:
        print("\n+++ WARNING: Unable to find CSV inventory file +++")
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
        source_inventory_dictlist = import_inventories(source_inventories)

#check that each csv file actually exists [approach later will be to iterate through loaded dictionaries of CSV files to check if a file corresponds to a key, which is derived from the filename column]
#fallback 1: if source inventory exists in indir, iterate through loading csv files all csv files
#fallback 2: if no inventory is specified and no csv files are found in indir, warn and proceed with no inventory

'''
setting up parameters for meadow inventory
'''
#TODO may want to convert everything to lowercase so you don't risk running into errors
#TODO move generating this dict to a function in a separate module
role_dict = {
'framemd5' : {'identifiers' : ['.framemd5'], 'type' : 'extension', 'role' : 'S', 'label' : 'Framemd5 file', 'file_builder' : '_supplementary_'},
'metadata' : {'identifiers' : ['.xml', '.json'], 'type' : 'extension', 'role' : 'S', 'label' : 'Metadata file', 'file_builder' : '_supplementary_'},
'qctools' : {'identifiers' : ['.xml.gz', '.qctools.mkv'], 'type' : 'extension', 'role' : 'S', 'label' : 'QCTools report', 'file_builder' : '_supplementary_'},
'spectrogram' : {'identifiers' : ['.png', '.PNG'], 'type' : 'extension', 'role' : 'S', 'label' : 'Spectrogram file', 'file_builder' : '_supplementary_'},
'dpx_checksum' : {'identifiers' : ['dpx.txt'], 'type' : 'extension', 'role' : 'S', 'label' : 'Source DPX sidecar checksum', 'file_builder' : '_supplementary_'},
'access' : {'identifiers' : ['-a.', '_a.', '-am.', '_am.', '_am_', '-am-', '.mp4'], 'type' : 'pattern', 'role' : 'A', 'label' : None, 'file_builder' : '_access_'},
'preservation' : {'identifiers' : ['-p.', '_p.', '-pm.', '_pm.', '_pm_', '-pm-', '.mkv'], 'type' : 'pattern', 'role' : 'P', 'label' : None, 'file_builder' : '_preservation_'}
}
if not args.aux_parse:
    aux_dict = {'auxiliary' : {'identifiers' : None, 'type' : None, 'role' : None, 'label' : None, 'file_builder' : None}}
elif 'extension' in args.aux_parse:
    aux_dict = {
    'auxiliay' : {'identifiers' : ['.jpg', '.JPG'], 'type' : 'extension', 'role' : 'X', 'label' : 'image', 'file_builder' : '_auxiliary_'}
    }
elif 'parse' in args.aux_parse:
    aux_dict = {'auxiliary' : {'identifiers' : ['_Asset', '-Asset', '_Can', '-Can', 'Front.', 'Back.'], 'type' : 'xparse', 'role' : 'X', 'label' : None, 'file_builder' : '_auxiliary_'}}
role_dict.update(aux_dict)
#add generic catch-all for unexpected file types
role_dict.update({'other' : {'identifiers' : None, 'type' : None, 'role' : None, 'label' : None, 'file_builder' : None}})

header_names = ['work_type', 'work_accession_number', 'file_accession_number', 'filename', 'description', 'label', 'role', 'work_image', 'structure']
'''
extract the filenames from the inventories as a list
'''
filename_list = []
for i in source_inventory_dictlist:
    name = i.get('filename')
    filename_list.append(name)
#error out if duplicate filenames are found
if len(filename_list) != len(set(filename_list)):
    print('\n--- ERROR: There are duplicate filenames in your inventories ---\n')
    quit()
#convert list to dict so it becomes easier to parse from here on
source_inventory_dict = {}
for item in source_inventory_dictlist:
    name = item['filename']
    source_inventory_dict[name] = item
#TODO add a check for existing file with filename before overwriting
'''
attempt to create output csv before continuing
'''
try:
    with open(meadow_csv_file, 'w', newline='\n') as outfile:
        outfile.close
except OSError:
    print("\n--- ERROR: Unable to create output file", meadow_csv_file + ' ---\n')
    quit()

meadow_inventory = []
meadow_full_dict = {}
for subdir, dirs, files in os.walk(indir):
    dirs.sort()
    clean_subdir = (subdir.replace(indir, ''))
    clean_subdir = clean_subdir.strip('/')
    #skip file types we don't want
    #TODO put this in an external function to make this a little cleaner
    files = [f for f in files if not f[0] == '.']
    files = [f for f in files if not f == 'Thumbs.db']
    files = [f for f in files if not f.endswith('.md5')]
    files = [f for f in files if not f.endswith('.csv')]
    if args.skip:
        skip_list = args.skip
        for i in skip_list:
            files = [f for f in files if not i in f]
    dirs[:] = [d for d in dirs if not d[0] == '.']
    for file in sorted(files):
        #set filename
        filename = os.path.join(clean_subdir, file)
        meadow_file_dict = {
        'work_type': None,
        'work_accession_number': None,
        'file_accession_number': None,
        'filename': filename,
        'description': None,
        'label': None,
        'role': None,
        'work_image': None,
        'structure': None
        }

        #TODO add safety check to make sure there aren't multiple matches for a filename in the accession numbers
        #check for corresponding item in loaded inventory
        #TODO handle cases where there is no inventory
        for item in filename_list:
            if item in file:
                meadow_file_dict.update({'work_accession_number': source_inventory_dict[item]['work_accession_number']})
                #load the work type
                work_type = source_inventory_dict[item]['work_type']
                meadow_file_dict.update({'work_type': work_type})
                #load the description
                meadow_file_dict.update({'description': source_inventory_dict[item]['description']})
                #if dictionary does not already have a key corresponding to the item add it
                if item not in meadow_full_dict:
                    meadow_full_dict[item] = [meadow_file_dict]
                #otherwise append it to the existing key
                else:
                    meadow_full_dict[item].append(meadow_file_dict)
                #setting a generic label
                inventory_label = source_inventory_dict[item]['label']
                if work_type == "VIDEO" or work_type == "AUDIO":
                    label,role,file_builder = meadow_parser_funcs.get_label(role_dict, file, inventory_label)
                    meadow_file_dict.update({'role': role})
                    role_count = sum(x.get('role') == role for x in meadow_full_dict.get(item))
                    meadow_file_dict.update({'label': label})
                    meadow_file_dict.update({'file_accession_number' : item + file_builder + f'{role_count:03d}'})
                else:
                    meadow_file_dict.update({'role': source_inventory_dict[item]['role']})
                    meadow_file_dict.update({'label': inventory_label})
                    meadow_file_dict.update({'file_accession_number' : source_inventory_dict[item]['file_accession_number']})
        #TODO build out how to handle cases where a file is not found in the inventory
        #allow user to add the file anyway
        if not any(item in file for item in filename_list):
            print("+++ WARNING: No entry matching " + file + " was found in your inventory +++")

#TODO final check that all ihidden files and folderstems from filename list are accounted for in the final inventory

with open(meadow_csv_file, 'w') as f:
    writer = csv.DictWriter(f, fieldnames = header_names)
    writer.writeheader()
    for item in meadow_full_dict:
        for file_info in meadow_full_dict[item]:
            writer.writerow(file_info)
print("Process complete!")
print("Meadow inventory located at: " + meadow_csv_file)
