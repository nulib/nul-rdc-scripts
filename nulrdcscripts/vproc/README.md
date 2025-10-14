# vproc
A script for transcoding video files

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed: ffmpeg, ffprobe, qcli, Mediaconch, poetry

## Usage  

In the terminal, [navigate](#terminal-help) to the `nul-rdc-scripts` folder before running. 

**Note:** make sure valid transcode_inventory.csv is in the input folder

### Single video

```
poetry run vproc -i INPUT_PATH
```
Example file structure
```
input_folder
├── transcode_inventory.csv
└── item.mov
```
### Batch videos

```
poetry run vproc -i INPUT_PATH -b
```
Example file structure
```
input_folder
├── transcode_inventory.csv
├── item_1
│   └── item_1_p.mkv
└── item_2
    └── item_2_p.mkv
```

## Commands
`--input`, `-i INPUT_PATH`
	full path to input folder  
`--output`, `-o OUTPUT_PATH`
	full path to output folder. If left blank, this will default to the same folder as the input.  
`--mixdown MIXDOWN`
	Sets how audio streams will be mapped when transcoding the access copy. Inputs include: `copy`, `4to3`, and `4to2`. Defaults to copy. 4to3 mixes streams 1&2 to a single stereo stream and copies streams 3 and 4. 4to2 mixes streams 1&2 and 3&4 to two stereo streams.  
`--verbose`
	view ffmpeg output when transcoding  
`--batch`, `b`
	for batch video transcoding

#### Only include if trying to use a version of the listed tool other than the system version or if the tool is not installed in the current path.
`--ffmpeg FFMPEG_PATH`  
`--ffprobe FFPROBE_PATH`  
`--qcli QCLI_PATH`  
`--mediaconch MEDIACONCH_PATH`  

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