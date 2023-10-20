# aproc
A script for processing and performing QC on audio files.

## Commands
`-h`, `--help`            show help message and exit   
`--input INPUT_PATH`, `-i INPUT_PATH`
                      full path to input folder   
`--output OUTPUT_PATH`, `-o OUTPUT_PATH`
                      full path to output csv file for QC results. If not specified this will default to creating a file in the input directory   
`--load_inventory INVENTORY_PATH`, `-l INVENTORY_PATH`
                      Use to specify a CSV inventory. If not specified the script will look in the base folder of the input for CSV inventories. If no inventories are found the script will leave some fields blank.   
`--sox SOX_PATH`        For setting a custom sox path   
`--bwfmetaedit METAEDIT_PATH`
                      For setting a custom BWF Metaedit path   
`--ffmpeg FFMPEG_PATH`  For setting a custom ffmpeg path   
`--ffprobe FFPROBE_PATH`
                      For setting a custom ffprobe path   
`--mediaconch MEDIACONCH_PATH`
                      For setting a custom mediaconch path   
`--transcode`, `-t`       Transcode access files   
`--write_metadata`, `-m`  Write Broadcast WAVE metadata to Preservation file   
`--write_json`, `-j`      Write metadata to json file   
`--spectrogram`, `-s`     generate spectrograms   
`--p_policy INPUT_POLICY`
                      Mediaconch policy for preservation files   
`--a_policy OUTPUT_POLICY`
                      Mediaconch policy for access files   
`--all`, `-a`         This is equivalent to using `-t -m -j -s`. Defaults to true. 

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed: ffmpeg, ffprobe, SoX, BWFMetaedit, Mediaconch, poetry

## Usage
Embed BWF metadata, transcode access files, generate spectrograms, and create sidecar json file. Correctly formatted inventory present in base of input directory.
```
poetry run aproc -i INPUT_PATH
```
### Example File Structure
```
project folder (script input)
├── inventory.csv
├── item_1
│   └── p
│       └── item_1_v01_p.wav
└── item_2
    └── p
        ├── item_2_v01s01_p.wav
        └── item_2_v01s02_p.wav
```

**Note:** Inventory column names MUST use the following names for the script to work (a reference inventory is provided in the data folder for this script and should reflect the most recent requirements):
```
work_accession_number
filename
label
inventory_title
Record Date/Time
Housing/Container Markings
Condition Notes
Barcode
Box/Folder
Alma number
Format
Running time (mins)
Tape Brand
Speed IPS
Tape Thickness
Base (acetate/polyester)
Track Configuration
Sound
Length/Reel Size
Tape Type (Cassette)
Noise Reduction
Capture Date
Digitizer
Digitizer Notes
Shot Sheet Check
Date
File Format & Metadata Verification
Date
File Inspection
Date
QC Notes
Notes for the Metadata Record
```
