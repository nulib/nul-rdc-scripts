# vproc
A script for transcoding video files

## Prerequisites
In order to use all of the script's functions you will need to have the following programs installed: ffmpeg, ffprobe, qcli, Mediaconch, poetry

## Usage
Place the transcode_inventory.csv file in the input folder and add any associated inventory information.  
**Note:** Make sure the values in the 'filename' column correspond with the base filename for the video file.  
Run the following command from the `nul-rdc-scripts` folder. Include any desired arguments  
`poetry run vproc -i INPUT_PATH`

**Note:** file structure must be as follows   
```
input_folder
└── item.mov
```
Or for batch transcoding
```
input_folder
├── item_1
│   └── item_1.mov
└── item_2
    └── item_2.mov
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