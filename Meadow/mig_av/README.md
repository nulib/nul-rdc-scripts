# Meadow Ingest Sheet Generator for AV <br/>
This is a Python script for converting AV inventories to Meadow ingest sheets. It can also be used to create ingest sheets for image projects with nested folder structures. <br/>

## Overview
The script performs the following primary functions:
- Identify files associated with the filename listed in the source inventory
- Expand filename to include path information
- Assign work_type
- Generate file_accession_number
- Assign file role
- Allows multiple fields to be combined in the description field
- Allows certain files to be flagged as auxiliary files
- Expands label if certain filename patterns are detected
- Outputs a Meadow ingest sheet that is ready to upload

## Commands
**-i**, **--input**   This should be the full path to a project folder. If no `--output` is specified, the script will default to using the input director for the output. <br/>
**-o**, **--output**   This should be the full path, including file name, to a csv file for writing the Meadow inventory to. If the output already exists it will be overwritten. Example - /user/my_documents/project_meadow_inventory.csv <br/>
**-l**, **--load_inventory**  Use to specify an inventory (.csv) or folder containing inventories. If not specified the script will look in the base folder of the input for inventories. <br/>
**-s**, **--skip**  Defines patterns to ignore. For example, `-s ".mp3"` would prevent the script from adding any .mp3 files it finds to the final inventory. <br/>
**-d**, **--description** Use to specify column names to populate Meadow description field with. Can take multiple inputs. Information from each column will be separated by a ";" in the description. Example usage: `-d "Date/Time" "Barcode"`. If not specified, script will default to looking for the column "inventory_title"<br/>
**-x**, **--auxiliary** Sets how to parse auxiliary files. Options include: `extension` (by extension; i.e. ".jpg"), `parse` (by word; i.e. "_Asset_Front"), `none` (no aux files). Default is `none`. <br/>
**--prepend_accession**, **-p** Set a string to be added to the beginning of the file accession number when it is generated

## Usage
Use the run.py file to run the script without installing.
Use Atom's Git integration for your work

Basic usage, input folder containing inventory and files. No auxiliary files. Outputting Meadow ingest inventory to input folder:
```
run.py -i path/to/input/folder
```

Basic usage, separate input folder, inventory, and output folder. No auxiliary files:
```
run.py -i path/to/input/folder -l path/to/inventory.csv -o path/to/output/file.csv
```

Parse image file filenames that contain keywords identifying them as auxiliary files ("_AssetFront", "_CanBack", etc.):
```
run.py -i path/to/input/folder -x parse
```

Skip ".mp4" and ".png" files. Add any JPEG files as auxiliary files. Add "P0001-" to the beginning of all file accession numbers. Combine information from the inventory_title, barcode, and record_date columns into the description :
```
run.py -i path/to/input/folder -s .mp4 .png -x extension -p P0001- -d inventory_title barcode record_date
```

## Notes
When ingesting files associated with an inventory created using the script, the folder structure in the S3 bucket should match the folder structure of the input that the script was run on.
