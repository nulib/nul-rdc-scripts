# aproc
A script for processing and performing QC on audio files.

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed: ffmpeg, ffprobe, SoX, BWFMetaedit, Mediaconch, poetry

## Usage
In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.  

**Note: make sure valid inventory csv is in the input folder**

### Basic usage (--all defaults true)
```
poetry run aproc -i INPUT_PATH
```

### Generate spectrograms only
```
poetry run aproc -i INPUT_PATH -s
```

### Generate spectrograms and skip coding (for vendors)
```
poetry run aproc -i INPUT_PATH -s --skip_coding
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
`--all`, `-a`         This is equivalent to using `-t -m -j -s`.  
`--transcode`, `-t`       transcode access files   
`--write_metadata`, `-m`  write Broadcast WAVE metadata to preservation file   
`--write_json`, `-j`      write metadata to json file   
`--spectrogram`, `-s`     generate spectrograms   
`--skip_coding`,      to skip coding history creation  
`--load_inventory INVENTORY_PATH`, `-l INVENTORY_PATH`
                      Use to specify a CSV inventory. If not specified the script will look in the base folder of the input for CSV inventories. If no inventories are found the script will leave some fields blank.   
`--sox SOX_PATH`        for setting a custom sox path   
`--bwfmetaedit METAEDIT_PATH`
                      for setting a custom BWF Metaedit path   
`--ffmpeg FFMPEG_PATH`  for setting a custom ffmpeg path   
`--ffprobe FFPROBE_PATH`
                      for setting a custom ffprobe path   
`--mediaconch MEDIACONCH_PATH`
                      for setting a custom mediaconch path   
`--p_policy INPUT_POLICY`
                      mediaconch policy for preservation files   
`--a_policy OUTPUT_POLICY`
                      mediaconch policy for access files   


## Terminal help
Change directory with `cd FILEPATH`
- can be relative to current directory `cd folder`
- or absolute `cd C:\folder\subfolder`
- go back one folder with `cd ..`
- and return to your user folder with just `cd`  

See contents of current directory
- `dir` (WINDOWS)
- `ls` (LINUX)

Clear terminal
- `cls` (WINDOWS)
- `clear` (LINUX)