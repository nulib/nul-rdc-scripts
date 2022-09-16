#!/usr/bin/env python3

import os
import subprocess
from iqc_parameters import args
import iqc_supportfuncs

indir = args.input_path
target_id = 'target_'
target_list = []
file_dict = {}
missing_in_inventory = []


source_inventories = iqc_supportfuncs.find_inventories()
source_inventory_dictlist = iqc_supportfuncs.import_inventories(source_inventories)
inventory_filename_list = iqc_supportfuncs.generate_inventory_filename_list(source_inventory_dictlist)

for subdir, dirs, files in os.walk(indir):
    dirs.sort()
    files = iqc_supportfuncs.clean_file_list(files)
    dirs[:] = [d for d in dirs if not d[0] == '.']
    for file in files:
        if target_id in file:
            is_target = True
        else:
            is_target = False
        if file in inventory_filename_list:
            in_inventory = True
        else:
            in_inventory = False
        filepath = os.path.join(subdir, file)
        item_dict = {
        'path' : filepath,
        'target' : is_target,
        'in inventory' : in_inventory
        }
        file_dict.update({file : item_dict})


file_list = [i for i in file_dict]
missing_in_files = [i for i in inventory_filename_list if i not in file_list]
for item in file_dict:
    #make this a separate function
    if file_dict[item]['in inventory'] is False and file_dict[item]['target'] is False:
        missing_in_inventory.append(item)
    if file_dict[item]['target'] is True:
        target_list.append(item)


input_folder_size = iqc_supportfuncs.get_size_format(iqc_supportfuncs.get_directory_size(indir))
print('INPUT SIZE: ' + input_folder_size)
print('TARGET FILES: ' + str(target_list))
print('TIFF Files Not Found in Inventory: ' + str(missing_in_inventory))
print('Inventory Files Not Found in TIFF Files: ' + str(missing_in_files))
