# aqc
A script for performing QC on audio files.

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed: ffmpeg, Mediaconch, poetry

## Usage
In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.  

You can run on a single file, or a project. For single file, the `-i` argument should recieve the path to that file.  

For a project, see example file structure below. 

```
project folder (script input path)
├── inventory.csv
├── item_1
│   └── p
│       └── item_1_v01_p.wav
└── item_2
    └── p
        ├── item_2_v01s01_p.wav
        └── item_2_v01s02_p.wav
```
**Note: an inventory csv is not required, but recommended with projects to check for all necessary files.**  

### Basic usage

This will generate a json file in the input path that contains loudness data and any potential clipping or silence.

```
poetry run aqc -i INPUT_PATH --lstats --find_clipping --find_silence
```

### Print graphs (currently hardcoded which graphs to plot)

Grpahs are saved as images in the input path.

```
poetry run aqc -i INPUT_PATH -p
```

### Load specific inventory file

This can be used if you want to load a specific inventory file. By default, it will search for a valid inventory in the input path and move on if it doesn't find one. This extra option could be used if there are multiple valid inventories in the input path or if the inventory is not in the input path.

```
poetry run aqc -i INPUT_PATH --inventory INVENTORY_PATH --lstats --find_clipping --find_silence
```

## Commands
`-h`, `--help` show help message and exit   
`-i INPUT_PATH`, `-input INPUT_PATH` full path to input folder   
`-l`, `--l_stats` generate loudness stats (peak dBTP and dBLUFS-I)  
`--inventory INVENTORY_PATH` use to load a specific inventory file  
`-p`, `--plot` plot graphs of data and save as images, currently hardcoded to specific values to graph  
`-c`, `--find_clipping` find clipping in the audio  
`-s`, `--find_silence` find potential silence in the audio  
`-v`, `--verbose` display a more detailed printout in the terminal  


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