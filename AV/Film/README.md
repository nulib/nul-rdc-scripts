# DPX to FFV1 RAWCooked Transcoding Script
Scripts for batch transcoding DPX sequences using RAWCooked <br/>

## Commands
**--input**, **-i** INPUT_PATH      full path to input folder <br/>
**--output**, **-o** OUTPUT_PATH     full path to output folder. If left blank, this will default to the same folder as the input. <br/>
**--framerate** override the default framerate with a custom framerate <br/>
**--subfolder_identifier** specifies the name of the folder within each item folder that contains DPX files <br/>
**--limit** 	only process items in folders that contain the provided string in their filename <br/>
**--filter_list** 	provide a text file with a list of folder names for each item that you want to process <br/>
**--check_runtime** 	compare the runtime of the FFV1/MKV file against the runtime of a corresponding access file <br/>

### Flags for custom tool paths
#### Only include if trying to use a version of the listed tool other than the system version or if the tool is not installed in the current path.
**--ffmpeg** FFMPEG_PATH <br/>
**--ffprobe** FFPROBE_PATH <br/>
**--rawcooked** RAWCOOKED_PATH <br/>

### Installation


### Usage
- The input must be a folder containing subfolders for each item (film/reel). The folder for each item must contain a preservation folder with the folder name 'p' that contains a DPX sequence. The preservation folder name can be changed using `--subfolder_identifier` followed by the name of the folder that contains DPX sequences. <br/>
- The command can be set to run on folders for specific films using the `--limit` or `--filter_list` commands. `--limit` should be followed by a string of text. Only folders containing that string will be processed. `--filter_list` should be followed by the path to a text file containing a list of folder names that you want to process. <br/>


**Basic usage:**
```
dpx2ffv1 -i input_folder -o output_folder
```

**Transcode and compare FFV1/MKV runtime against access file runtime**
```
dpx2ffv1 -i input_folder -o output_folder --check_runtime
```
