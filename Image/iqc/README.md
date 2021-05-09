# IQC - Image Quality Checker <br/>
Python tools for running various automated QC functions on NUL RDC image projects. <br/>

## Dependencies - CHECK BEFORE TRYING TO RUN THE SCRIPT <br/>
- This script requires ExifTool and Python 3 with the Pandas and Pillow libraries. <br/>
- Install Python from the Python website if it is not already installed. If you aren't sure whether or not Python is installed, try typing `python -h` in the command line. If installing Python on Windows make sure to check the box to add Python to your PATH during installation. <br/>
- If installing an iqc release using pip, it should automatically install Pandas and Pillow. <br/>
- ExifTool can be installed from the ExifTool website: https://exiftool.org/ <br/>
- If on Windows, make sure that ExifTool is in your PATH or that you specify the path to the ExifTool executable using `--exiftool` when running the script. <br/>
- If you need to manually install the pandas and Pillow libraries follow the instructions on their respective websites. <br/>


## Installation <br/>
- Download the latest release from the releases page. <br/>
- The release will be a .zip folder. <br/>
- To install the script open the command line or terminal, cd to the folder containing the zipped folder and run `pip install iqc.zip`. <br/>

## Updating <br/>
- To update the script, follow the same process as installing, but run `pip install -U iqc.zip`. <br/>
- You can check the version of iqc that you have installed by running `pip show iqc`. <br/>

## Usage <br/>
### Commands <br/>
**-i**, **--input**   This should be the full path to a project folder. If one or more inventory csv files are placed in the base folder of your input and you do not use the `--inventory` command to specify a different csv file or directory, those inventories will be used for processing the files. <br/>
**-o**, **--output**   This should be the full path, including file name, to a json file for writing a json report to. If the output already exists it will be overwritten. Example - /user/my_documents/project_report.json <br/>
**--exiftool**  Used to specify a custom path to ExifTool. This should generally not be needed. <br/>
**--inventory**   This should be the full path to a folder containing inventory csv files. Inventories should be left in their original formatting at the moment. If the folder contains multiple inventories the script will try to combine them. <br/>
**--verify_checksums**, **-c**  This will try to verify existing checksums. It should be followed by the specific type of checksum file to verify (i.e. `--verify_checksums md5` or `--verify_checksums md5 sha1`). Currently the only supported formats are `md5` and `sha1`. Checksum files are expected to end with the specified text (sha1 files should end with .sha1). <br/>
**--verify_metadata**, **-m**  This will run ExifTool on each TIFF file and check whether the IPTC fields By-line, Headline, Source, and CopyrightNotice match the listed information in the inventory (the Creator, Headline, Source, and Copyright Notice columns). By default this command will only check if the inventory field contains the text found in the file so that truncated metadata will also be matched (i.e. a file with IPTC metadata "Northwestern Uni" would pass even if the inventory metadata is "Northwestern University"). <br/>
**--strict**  When used with `--verify_metadata` this enforces exact matches when checking metadata (i.e. a file with IPTC metadata "Northwestern Uni" would fail if the inventory metadata is "Northwestern University"). <br/>
**--verify_techdata**, **-t** This will use ExifTool to check the bit depth and color profile of images and compare them against expected Access and Preservation file specifications used by RDC. <br/>
**--all**, **-a** This is equivalent to using the commands `--verify_metadata --verify_techdata --verify_checksums md5 -o /path/to/output/project_folder/project_folder_report.json`. The output path will default to the base folder of your input. Using the `-o` command and specifying an output in addition to using `-a` will output the report to the specified output rather than the default `-a` one. <br/>
### Examples <br/>
- Basic usage where you have a csv inventory in your project folder and want to check that there are TIFF files for all of the files in the inventory. This will output a short report in the terminal/command line: <br/>
```
  iqc -i /path/to/project/folder/P000_ProjectID
```
- Basic usage where you have a csv inventory in your project folder and want to run all of the QC checks and output a report to a file: <br/>
```
  iqc -i /path/to/project/folder/P000_ProjectID -a
```
- Example of using a directory containing multiple csv inventories for a single project stored in a separate folder and verifying SHA1 checksums and only output the results to the command line: <br/>
```
  iqc --inventory /path/to/inventory/folder -i /path/to/project/folder/P000_ProjectID -c sha1
```
- The script can be run without installing using the run.py script located in the base iqc directory. <br/>
- You may need to make the script executable first. In order to do so, type `chmod 755` into the command line on a Mac followed by a space, then drag and drop the run.py file into the command line and press return. The full command should look something like `chmod 755 path/to/git/folder/iqc/run.py` <br/>
- You can check if the script is executable by trying to bring up the help text `path/to/git/folder/iqc/run.py -h` <br/>
- Once the script is executable, you can run it by setting the correct inputs and outputs: <br/>
```
  path/to/git/folder/pandas_testing/image_processing/run.py -i path/to/input/folder -o path/to/csv/my_report.json --inventory path/to/inventory/folders
```
- The commands can be included in any order as long as each is followed by the correct path (i.e. `--inventory` should always have the path to a csv file after it regardless of where it is in the command). <br/>

## Notes on changing script functionality <br/>
- Customizing the inventory column name used to match file names: Change the value of the column_to_match variable in the script <br/>
- Handle csv files with a second header row Change header=0 to header=1 <br/>
