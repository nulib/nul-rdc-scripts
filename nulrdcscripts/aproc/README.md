# aproc
A script for processing and performing QC on audio files.

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed: ffmpeg, ffprobe, SoX, BWFMetaedit, Mediaconch, poetry

## Usage
In the terminal, navigate to the `nul-rdc-scripts` folder before running.  
*Example command:* embed BWF metadata, transcode access files, generate spectrograms, and create sidecar json file.
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
`--skip_coding`,      To skip coding history creation