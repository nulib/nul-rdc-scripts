# avqc
A script to use when QCing AV that validates checksums and opens media as a playlist.  
By default, only preservation files are opened in the playlist.

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed: mpv, poetry

**Optional:** visualizer.lua for mpv  
See [below](#visualizerlua-install) for install 

## Usage
In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running.  

**Note: make sure valid inventory csv is in the input folder**

**Note: --audio, --video, or --film is required to choose project type**

### Basic audio project
```
poetry run avqc -i INPUT_PATH -a
```

### Video project without validating checksums
```
poetry run avqc -i INPUT_PATH -a -s
```

### Film project with access files played
```
poetry run avqc -i INPUT_PATH -f --play_access
```

### Example File Structure
```
project folder (script input)
├── inventory.csv
├── item_1
│   ├── p
│   │   └── item_1_v01_p.wav
│   └── a
│       └── item_1_v01_a.wav
└── item_2
    ├── p
    │   ├── item_2_v01s01_p.wav
    │   └── item_2_v01s02_p.wav
    └── a
        ├── item_2_v01s01_a.wav
        └── item_2_v01s02_a.wav
```

## Commands
`-h`, `--help` show help message and exit   
`--input INPUT_PATH`, `-i INPUT_PATH` full path to input folder   
`--audio`, `-a` use for audio projects  
`--video`, `-v` use for video projects  
`--film`, `-f` use for film projects  
`--skip_checksums`, `-s` use to skip validating checksums  
`--play_access` use to play access files during qc

## visualizer.lua Install 
- Navigate to `%AppData%/Roaming/mpv/scripts`  
**Note:** You may have to create the `scripts` folder  
- Download [visualizer.lua](https://github.com/mfcc64/mpv-scripts/blob/master/visualizer.lua) and save to `scripts` folder  
- (Optional) Change the line 10 from `name = "showcqt",` to `name = "avectorscope",`  
This makes it start on the vectorscope.
- During use, press `c` to cycle through visualizations.  


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