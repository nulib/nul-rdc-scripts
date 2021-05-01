#!/usr/bin/env python3

import csv
import sys
import os
import glob
from meadow_csv_script.parameters import args
import pandas as pd

def csv_main():
    column_to_match = 'file'
    indir = args.input_path
    if indir.endswith('.csv'):
        if os.path.isfile(indir):
            inventorydf = pd.read_csv(indir, skiprows=0, header=0)
        else:
            print('ERROR: Supplied inventory path is not valid')
            quit()
    else:
        if os.path.isdir(indir):
            inventories = glob.glob(os.path.join(indir, "*.csv"))
            inventorydf = pd.concat([pd.read_csv(inv, skiprows=0, header=0') for inv in inventories])
        else:
            print('ERROR: Supplied inventory path is not valid')
            quit()
    inventorydf = inventorydf[['work_accession_number', 'file_accession_number', 'filename', 'description', 'label', 'role']]

    #Write merged inventory to output specified in command
    print ("writing to file")
    inventorydf.to_csv(args.output_path, sep=',', encoding='utf-8', index=False)
    print('your file was written to ' + args.output_path)