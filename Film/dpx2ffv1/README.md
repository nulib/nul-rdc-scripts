# DPX to FFV1 RAWCooked Transcoding Script
Scripts for batch transcoding DPX sequences using RAWCooked <br/>

## Commands
**--input**, **-i** INPUT_PATH      full path to input folder <br/>
**--output**, **-o** OUTPUT_PATH     full path to output folder. If left blank, this will default to the same folder as the input. <br/>
**--framerate** <br/>
**--subfolder_identifier** <br/>
**--limit** <br/>
**--filter_list** <br/>
**--check_runtime** <br/>

### Flags for custom tool paths
#### Only include if trying to use a version of the listed tool other than the system version or if the tool is not installed in the current path.
**--ffmpeg** FFMPEG_PATH <br/>
**--ffprobe** FFPROBE_PATH <br/>
**--rawcooked** RAWCOOKED_PATH <br/>

### Installation


### Usage
- The input must be a folder containing subfolders for each film. By default the script expects the DPX sequence for each film to be in a folder named 'pm'. This can be changed using `--subfolder_identifier` followed by the name of the folder that contains DPX sequences. <br/>
- The command can be set to run on folders for specific films using the `--limit` or `--filter_list` commands. `--limit` should be followed by a string of text. Only folders containing that string will be processed. `--filter_list` should be followed by the path to a text file containing a list of folder names that you want to process. <br/>


**Example command:**
	`dpx2ffv1 -i input_folder -o output_folder --check_runtime`
